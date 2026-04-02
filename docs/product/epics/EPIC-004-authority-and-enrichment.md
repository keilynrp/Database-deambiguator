# EPIC-004 - Authority and Enrichment

## 1. Summary

Agrupar bajo una sola epic el frente de authority resolution y enrichment para sostener la propuesta de valor de conocimiento confiable y enriquecido.

## 2. Problem

- authority y enrichment son diferenciales fuertes de UKIP
- hoy existen como capacidades tecnicas maduras, pero faltaba una linea operativa unificada
- sin esta epic, backlog, riesgos y UX del frente pueden fragmentarse

## 3. Objective

Hacer visible y trazable el frente de reconciliacion externa y enriquecimiento de entidades.

## 4. User value

Como investigador o analista, quiero enriquecer y reconciliar entidades contra fuentes externas para aumentar confianza, profundidad y utilidad de los datos.

## 5. Scope

Incluye:

- authority resolution
- enrichment worker
- scrapers de enriquecimiento
- estadisticas y estado de enrichment
- backlog de proveedores y fuentes externas

Excluye:

- analitica posterior que consume datos ya enriquecidos
- grafo o RAG salvo donde dependan directamente del enrichment

## 6. Success criteria

- authority y enrichment quedan agrupados como frente operativo
- historias futuras del frente parten de esta epic
- se vuelve mas facil priorizar robustez, calidad y fallback de fuentes

## 7. Technical impact

- backend: `authority.py`, `enrichment_worker.py`, `scrapers.py`, adapters externos
- frontend: `frontend/app/authority/`, tabs y vistas de enrichment
- tests: authority, enrichment worker, scrapers

## 8. Risks

- riesgo: agregar fuentes o reglas sin coherencia funcional
- impacto: deuda operativa y experiencia inconsistente
- mitigacion: exigir historias y criterios de aceptacion bajo esta epic

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-011 | Backfillear el frente de authority y enrichment en el sistema operativo | Done |
| US-012 | Formalizar criterios operativos para authority review y enrichment fallback | Planned |
| US-024 | Revision y confirmacion de candidatos de autoridad | Planned |
| US-025 | Orquestacion de enrichment individual y masivo | Planned |
| US-026 | Gestion de fuentes de scraping para enrichment | Planned |
| US-055 | Author Resolution Engine MVP | Done |
| US-056 | Explicit NIL Detection Layer | Done |
| US-057 | Hierarchical Fallback for Concept Linking | Planned |
| US-058 | UKIP NIL Benchmark and Evaluation Pack | Done |
| US-059 | LLM Query Reformulation for Hard NIL Cases | Proposed |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Incorporar authority y enrichment al backlog vivo |
| Post-SPRINT-105 | Entregar `US-055` como baseline operable de author resolution explicable |

## 11. Evidence

- Codigo: `backend/routers/authority.py`, `backend/enrichment_worker.py`, `backend/routers/scrapers.py`
- Docs: `README.md`, `docs/reference/HISTORICAL_REFERENCE_INDEX.md`
- Blueprint recomendado: `docs/product/AUTHOR_RESOLUTION_ENGINE_MVP.md`
- Implementacion MVP: `backend/authority/author_resolution.py`, `POST /authority/authors/resolve`, `GET /authority/authors/review-queue`, `GET /authority/authors/metrics`, `GET /authority/authors/review-queue/{record_id}/compare`
- Deteccion explicita NIL: `backend/authority/nil_detection.py`, `AuthorityRecord.nil_score`, `alembic/versions/b1c2d3e4f5a6_sprint_106_nil_detection_layer.py`
- UI operativa: `frontend/app/authority/page.tsx`
- Tests MVP: `backend/tests/test_sprint106_author_resolution_engine.py`, `backend/tests/test_sprint106_author_review_queue.py`, `backend/tests/test_sprint106_author_metrics.py`, `backend/tests/test_sprint106_author_compare.py`, `backend/tests/test_sprint106_nil_detection.py`, `backend/tests/test_sprint106_nil_benchmark.py`
- Benchmark offline: `backend/tests/fixtures/author_nil_benchmark.json`, `backend/authority/benchmark.py`, `scripts/evaluate_author_nil_benchmark.py`, `docs/product/AUTHORITY_NIL_BENCHMARK_PROTOCOL.md`
- Siguiente roadmap: `US-057`, `US-059`
