# US-059 - LLM Query Reformulation for Hard NIL Cases

## 1. User story

Como equipo de authority resolution, quiero usar reformulacion de consultas con LLM solo en casos dificiles para aumentar recall de candidatos sin volver el sistema dependiente de LLMs en el camino principal.

## 2. Context

- Epic: `EPIC-004`
- Dependencias recomendadas: `US-056`, `US-058`

## 3. Acceptance criteria

- [x] existe un experimento controlado de query reformulation para casos con retrieval vacio o debil
- [x] el uso de LLM queda bajo feature flag y apagado por defecto
- [x] se registran consultas alternativas, ganancia de retrieval y costo operativo
- [x] el sistema no rompe si el proveedor LLM no esta configurado o falla
- [x] las variantes generadas no sustituyen la evidencia deterministicamente explicable ya existente

## 4. Functional notes

- no es un aporte central del paper revisado; es una extension opcional para UKIP
- debe correr solo despues de que retrieval determinista y fallback semantico no sean suficientes
- no toca telemetry ni Sentry

## 5. Technical notes

- `backend/authority/resolver.py`
- `backend/authority/author_resolution.py`
- `backend/llm_agent.py`
- `backend/adapters/llm/openai_adapter.py`
- metricas y feature flags operativas

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 8. Evidence

- helper opt-in: `backend/authority/query_reformulation.py`
- safe LLM wrapper: `backend/llm_agent.py`
- persistence: `AuthorityRecord.reformulation_*`, `alembic/versions/d3e4f5a6b7c8_sprint_106_llm_query_reformulation.py`
- metrics/UI: `backend/routers/authority.py`, `frontend/app/authority/page.tsx`
- tests: `backend/tests/test_sprint106_query_reformulation.py`, `backend/tests/test_ci_optional_openai.py`
- flags: `.env.example`

## 7. Notes for prioritization

- prioridad menor que `US-056` y `US-058`
- debe entrar como experimento medido, no como cambio arquitectonico base
