from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.analytics import rag_engine
from backend.context_engine import ContextEngine
from backend.olap import olap_engine
from backend.routers.deps import _get_active_integration
from backend.routers.nlq import NLQSanitizer, _build_system_prompt
from backend.services.pattern_discovery import PatternDiscoveryService
from backend.tenant_access import persisted_org_id, scope_query_to_org

logger = logging.getLogger(__name__)

ChatMode = Literal["auto", "rag", "nlq", "hybrid"]
ResolvedMode = Literal["rag", "nlq", "hybrid", "unclear"]

# The fixed vocabulary the classifier may answer with. Anything outside it is
# discarded rather than mapped onto a mode by accident — a provider is free to
# invent a label, and an unrecognised one must not silently become a retrieval
# strategy.
_INTENT_VOCABULARY = frozenset({"aggregate", "evidence", "exploration"})

# Issue #227: this used to be three regexes of Spanish keywords. An English
# question matched none of them and fell through to `rag`, so an aggregate
# question got answered by semantic retrieval over documents — fluently, and
# with no signal that it had been misrouted. Adding an English column would
# have left the third language broken the same way, so the question is put to
# the LLM already present in the request path instead. Nothing here reads the
# question's words, which is what makes it language-agnostic.
_INTENT_CLASSIFIER_PROMPT = """You label a research question with the kinds of \
retrieval that can answer it. Reply with JSON only, no prose:

{"intents": ["aggregate", "evidence", "exploration"]}

Use only these labels, and include every one that applies:

- "aggregate": asks for counts, totals, rates, averages, distributions, \
rankings or breakdowns — answerable by querying structured data.
- "evidence": asks which records, sources, papers or documents support \
something, or asks why/how something is the case.
- "exploration": asks for patterns, gaps, risks, impact, recommendations or \
briefing material that requires interpretation.

The question may be in any language; label its intent, not its language.

If the question fits none of these — it is unintelligible, or asks for \
something this system does not retrieve — reply {"intents": []}. Do not guess: \
an empty list is a valid and useful answer."""


class AgenticChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=5000)
    mode: ChatMode = "auto"
    domain_id: str = Field(default="default", min_length=1, max_length=64)
    import_batch_id: int | None = Field(default=None, ge=1)
    provider: str | None = Field(default=None, max_length=80)
    portal_slug: str | None = Field(default=None, max_length=160)
    entity_id: int | None = Field(default=None, ge=1)
    top_k: int = Field(default=6, ge=1, le=20)
    use_tools: bool = True
    persist_trace: bool = True


class AgenticResearchChatService:
    """Orchestrates NLQ, RAG, structured context and trace persistence."""

    @classmethod
    def ask(
        cls,
        db: Session,
        payload: AgenticChatRequest,
        current_user: models.User,
        org_id: int | None,
    ) -> dict[str, Any]:
        # The integration is resolved before the mode because the mode now
        # depends on it: `auto` asks the provider to classify the question.
        integration = _get_active_integration(db)
        mode_used, mode_resolution = cls._resolve_mode(
            payload.question, payload.mode, integration
        )
        scope = cls._scope_payload(payload)
        context = cls._build_context_blocks(db, payload, org_id)

        rag_result: dict[str, Any] | None = None
        nlq_result: dict[str, Any] | None = None
        errors: list[str] = []

        if mode_used in {"rag", "hybrid"}:
            rag_result = cls._run_rag(db, payload, integration, context["system_prompt"], org_id)
            if rag_result.get("error"):
                errors.append(str(rag_result["error"]))

        if mode_used in {"nlq", "hybrid"}:
            nlq_result = cls._run_nlq(db, payload, integration)
            if nlq_result.get("error"):
                errors.append(str(nlq_result["error"]))

        answer = cls._compose_answer(
            payload=payload,
            mode_used=mode_used,
            rag_result=rag_result,
            nlq_result=nlq_result,
            context=context,
            errors=errors,
        )
        sources = cls._normalize_sources(rag_result)
        trace = cls._build_trace(
            payload=payload,
            mode_used=mode_used,
            mode_resolution=mode_resolution,
            rag_result=rag_result,
            nlq_result=nlq_result,
            context=context,
            integration=integration,
            errors=errors,
        )

        trace_id = None
        if payload.persist_trace:
            trace_id = cls._persist_trace(
                db=db,
                payload=payload,
                answer=answer,
                sources=sources,
                trace=trace,
                current_user=current_user,
                org_id=org_id,
            )

        return {
            "answer": answer,
            "mode_used": mode_used,
            "scope": scope,
            "trace_id": trace_id,
            "trace": trace,
            "sources": sources,
            "follow_up_questions": cls._follow_ups(payload, mode_used),
        }

    @staticmethod
    def _scope_payload(payload: AgenticChatRequest) -> dict[str, Any]:
        return {
            "domain_id": payload.domain_id,
            "import_batch_id": payload.import_batch_id,
            "provider": payload.provider,
            "portal_slug": payload.portal_slug,
            "entity_id": payload.entity_id,
        }

    @classmethod
    def _classify_intents(cls, question: str, integration) -> tuple[set[str], str]:
        """Ask the active provider which kinds of retrieval fit *question*.

        Returns the recognised intents and how the answer was reached, so the
        caller can tell "the model found no intent" (a judgement about the
        question) apart from "we could not ask" (a state of the deployment).
        Those two deserve different behaviour and used to be indistinguishable.
        """
        adapter = rag_engine._build_adapter(integration)
        if adapter is None:
            return set(), "no_classifier"

        raw = adapter.chat(
            system_prompt=_INTENT_CLASSIFIER_PROMPT,
            user_query=question,
            context_chunks=[],
        ).strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            parsed = json.loads(raw.strip())
            labels = parsed["intents"]
        except (ValueError, TypeError, KeyError) as exc:
            # A reply we cannot read is not evidence that the question had no
            # intent, so it must not be reported as an empty classification.
            logger.warning("Agentic chat intent classifier returned unparseable JSON: %s", exc)
            return set(), "classifier_error"

        if not isinstance(labels, list):
            logger.warning("Agentic chat intent classifier returned a non-list 'intents'")
            return set(), "classifier_error"
        return {str(label) for label in labels} & _INTENT_VOCABULARY, "llm"

    @classmethod
    def _resolve_mode(
        cls, question: str, requested_mode: ChatMode, integration
    ) -> tuple[ResolvedMode, str]:
        """Pick the retrieval mode, and report how the choice was made.

        The mapping below is the one the keyword table implemented, minus its
        final `else rag`. That fallback is the defect in #227: a question the
        resolver could not read became a confident answer of the wrong shape.
        An unresolved question now says so.
        """
        if requested_mode != "auto":
            return requested_mode, "explicit"

        try:
            intents, resolution = cls._classify_intents(question, integration)
        except Exception as exc:
            logger.warning("Agentic chat intent classification failed: %s", exc)
            intents, resolution = set(), "classifier_error"

        if resolution != "llm":
            # We could not ask. Widening to `hybrid` runs both branches instead
            # of quietly re-picking the old default; it costs a second retrieval
            # rather than an answer of the wrong kind.
            return "hybrid", resolution

        aggregate = "aggregate" in intents
        interpretive = intents & {"evidence", "exploration"}
        if aggregate and interpretive:
            return "hybrid", resolution
        if aggregate:
            return "nlq", resolution
        if "exploration" in intents:
            return "hybrid", resolution
        if "evidence" in intents:
            return "rag", resolution
        return "unclear", resolution

    @classmethod
    def _build_context_blocks(
        cls,
        db: Session,
        payload: AgenticChatRequest,
        org_id: int | None,
    ) -> dict[str, Any]:
        blocks: dict[str, Any] = {}

        try:
            ctx = ContextEngine().build_domain_context(payload.domain_id, db, org_id)
            blocks["domain_snapshot"] = ctx
        except Exception as exc:
            blocks["domain_snapshot_error"] = str(exc)

        entity = None
        if payload.entity_id:
            entity = (
                scope_query_to_org(db.query(models.RawEntity), models.RawEntity, org_id)
                .filter(models.RawEntity.id == payload.entity_id)
                .first()
            )
            if entity:
                blocks["entity_profile"] = cls._entity_profile(entity)
            else:
                blocks["entity_profile_error"] = f"Entity {payload.entity_id} not found in scope."

        try:
            blocks["hidden_patterns"] = PatternDiscoveryService.discover(
                db,
                domain_id=payload.domain_id,
                org_id=org_id,
                import_batch_id=payload.import_batch_id,
                provider=payload.provider,
                portal_slug=payload.portal_slug,
                limit=4,
            )
        except Exception as exc:
            blocks["hidden_patterns_error"] = str(exc)

        summary = cls._scope_summary(db, payload, org_id)
        blocks["scope_summary"] = summary

        system_prompt = (
            "UKIP structured context for this answer. Respect the declared scope, "
            "avoid inventing missing metadata, and cite catalog sources when available.\n"
            + json.dumps(blocks, ensure_ascii=False, default=str)[:12000]
        )
        return {"blocks": blocks, "system_prompt": system_prompt}

    @staticmethod
    def _scope_summary(db: Session, payload: AgenticChatRequest, org_id: int | None) -> dict[str, Any]:
        query = scope_query_to_org(db.query(models.RawEntity), models.RawEntity, org_id).filter(
            models.RawEntity.domain == payload.domain_id
        )
        if payload.import_batch_id:
            query = query.filter(models.RawEntity.import_batch_id == payload.import_batch_id)
        if payload.provider:
            query = query.filter(
                (models.RawEntity.enrichment_source == payload.provider)
                | (models.RawEntity.source == payload.provider)
            )
        total = query.with_entities(func.count(models.RawEntity.id)).scalar() or 0
        enriched = query.filter(
            models.RawEntity.enrichment_status.in_(["completed", "done", "enriched"])
        ).with_entities(func.count(models.RawEntity.id)).scalar() or 0
        avg_quality = query.with_entities(func.avg(models.RawEntity.quality_score)).scalar()
        return {
            "records": int(total),
            "enriched": int(enriched),
            "enrichment_pct": round(enriched / total * 100, 1) if total else 0.0,
            "avg_quality": round(float(avg_quality), 3) if avg_quality is not None else None,
        }

    @staticmethod
    def _entity_profile(entity: models.RawEntity) -> dict[str, Any]:
        return {
            "id": entity.id,
            "label": entity.primary_label,
            "canonical_id": entity.canonical_id,
            "entity_type": entity.entity_type,
            "domain": entity.domain,
            "source": entity.source,
            "enrichment_source": entity.enrichment_source,
            "enrichment_status": entity.enrichment_status,
            "citations": entity.enrichment_citation_count,
            "concepts": entity.enrichment_concepts,
            "quality_score": entity.quality_score,
        }

    @staticmethod
    def _run_rag(
        db: Session,
        payload: AgenticChatRequest,
        integration,
        extra_system_context: str,
        org_id: int | None,
    ) -> dict[str, Any]:
        if payload.use_tools:
            return rag_engine.query_catalog_agentic(
                user_question=payload.question,
                integration_record=integration,
                db=db,
                top_k=payload.top_k,
                extra_system_context=extra_system_context,
                max_iterations=4,
                org_id=org_id,
            )
        return rag_engine.query_catalog(
            user_question=payload.question,
            integration_record=integration,
            top_k=payload.top_k,
            extra_system_context=extra_system_context,
            org_id=org_id,
        )

    @staticmethod
    def _run_nlq(db: Session, payload: AgenticChatRequest, integration) -> dict[str, Any]:
        if not integration:
            return {"error": "No active AI provider configured for NLQ."}
        try:
            dimensions = olap_engine.get_dimensions(payload.domain_id)
            if not dimensions:
                return {"error": "No OLAP dimensions available for this domain."}
            adapter = rag_engine._build_adapter(integration)
            if adapter is None:
                return {"error": "Could not build LLM adapter for NLQ."}
            raw = adapter.chat(
                system_prompt=_build_system_prompt(dimensions),
                user_query=payload.question,
                context_chunks=[],
            ).strip()
            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:]
            translated = json.loads(raw.strip())
            valid_dim_names = {d["name"] for d in dimensions}
            group_by, filters = NLQSanitizer.sanitize(translated, valid_dim_names)
            result = olap_engine.query_cube(
                domain_id=payload.domain_id,
                group_by=group_by,
                filters=filters or None,
            )
            return {
                "translated": {
                    "group_by": group_by,
                    "filters": filters,
                    "explanation": translated.get("explanation", ""),
                },
                "result": result,
            }
        except Exception as exc:
            logger.warning("Agentic chat NLQ branch failed: %s", exc)
            return {"error": str(exc)}

    @staticmethod
    def _compose_answer(
        payload: AgenticChatRequest,
        mode_used: str,
        rag_result: dict[str, Any] | None,
        nlq_result: dict[str, Any] | None,
        context: dict[str, Any],
        errors: list[str],
    ) -> str:
        summary = context["blocks"].get("scope_summary", {})

        if mode_used == "unclear":
            # Saying nothing useful is the correct answer here. The alternative
            # — the behaviour this replaced — was to retrieve documents anyway
            # and present whatever came back as if it answered the question.
            return (
                "No pude determinar que tipo de pregunta es esta, asi que no la "
                "respondi en lugar de arriesgar una respuesta con la forma "
                "equivocada. Reformulala pidiendo explicitamente lo que "
                "necesitas — un conteo o distribucion, la evidencia que sostiene "
                "algo, o un analisis de patrones y brechas — o fija el modo "
                "(nlq, rag o hybrid) en la consulta."
            )

        rag_answer = (rag_result or {}).get("answer")
        nlq_translated = (nlq_result or {}).get("translated")
        nlq_result_data = (nlq_result or {}).get("result")

        parts: list[str] = []
        if rag_answer:
            parts.append(str(rag_answer))
        if nlq_translated and nlq_result_data:
            parts.append(
                "Lectura NLQ: "
                + str(nlq_translated.get("explanation") or "consulta estructurada ejecutada")
                + f". Resultado: {json.dumps(nlq_result_data, ensure_ascii=False, default=str)[:1200]}"
            )
        if parts:
            return "\n\n".join(parts)

        if errors:
            return (
                "No pude completar la consulta con el proveedor LLM activo. "
                "Aun asi, el alcance quedo preparado para analisis: "
                f"{summary.get('records', 0)} registros, "
                f"{summary.get('enrichment_pct', 0)}% enriquecidos. "
                "Configura o revisa el proveedor AI/RAG y vuelve a intentar. "
                f"Detalle tecnico: {'; '.join(errors[:2])}"
            )

        return (
            "El alcance esta listo para consulta, pero no hay suficiente evidencia indexada "
            "para producir una respuesta confiable. Indexa el catalogo RAG o ejecuta enrichment "
            "antes de usar esta pregunta como evidencia de brief."
        )

    @staticmethod
    def _normalize_sources(rag_result: dict[str, Any] | None) -> list[dict[str, Any]]:
        normalized = []
        for doc in (rag_result or {}).get("sources", []) or []:
            metadata = doc.get("metadata") or {}
            normalized.append({
                "entity_id": metadata.get("entity_id") or doc.get("entity_id"),
                "label": metadata.get("entity_name") or doc.get("label") or doc.get("text", "")[:90],
                "score": doc.get("score") or doc.get("distance"),
                "source": metadata.get("source") or "catalog",
            })
        return normalized

    @staticmethod
    def _build_trace(
        payload: AgenticChatRequest,
        mode_used: str,
        mode_resolution: str,
        rag_result: dict[str, Any] | None,
        nlq_result: dict[str, Any] | None,
        context: dict[str, Any],
        integration,
        errors: list[str],
    ) -> dict[str, Any]:
        return {
            "rag_used": mode_used in {"rag", "hybrid"},
            "nlq_used": mode_used in {"nlq", "hybrid"},
            # How the mode was chosen. Without this a `hybrid` answer produced
            # because no classifier was reachable is indistinguishable from one
            # the classifier actually asked for — the kind of silent difference
            # that let #227 live in production.
            "mode_resolution": mode_resolution,
            "tools_used": (rag_result or {}).get("tools_used", []),
            "context_blocks": list(context["blocks"].keys()),
            "iterations": (rag_result or {}).get("iterations", 0),
            "provider": getattr(integration, "provider_name", None),
            "model": getattr(integration, "model_name", None),
            "errors": errors,
        }

    @staticmethod
    def _persist_trace(
        db: Session,
        payload: AgenticChatRequest,
        answer: str,
        sources: list[dict[str, Any]],
        trace: dict[str, Any],
        current_user: models.User,
        org_id: int | None,
    ) -> int:
        snapshot = {
            "kind": "agentic_chat_trace",
            "question": payload.question,
            "answer": answer,
            "scope": AgenticResearchChatService._scope_payload(payload),
            "sources": sources,
            "trace": trace,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        record = models.AnalysisContext(
            domain_id=payload.domain_id,
            user_id=current_user.id,
            org_id=persisted_org_id(org_id),
            label=f"agentic-chat: {payload.question[:72]}",
            context_snapshot=json.dumps(snapshot, ensure_ascii=False, default=str),
            notes="Saved agentic research chat trace.",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return int(record.id)

    @staticmethod
    def _follow_ups(payload: AgenticChatRequest, mode_used: str) -> list[str]:
        if payload.entity_id:
            return [
                "Que evidencia sostiene este registro?",
                "Como se conecta con otros autores, afiliaciones o conceptos?",
                "Conviene incluirlo en el brief final?",
            ]
        if mode_used == "nlq":
            return [
                "Puedes mostrar el mismo resultado por proveedor?",
                "Que dominio concentra mas registros?",
                "Como cambia la distribucion por tipo de entidad?",
            ]
        return [
            "Que registros sostienen mejor esta conclusion?",
            "Que brechas deberia corregir antes del brief?",
            "Como cambia el patron por proveedor o ingesta?",
        ]
