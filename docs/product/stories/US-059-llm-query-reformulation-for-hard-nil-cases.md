# US-059 - LLM Query Reformulation for Hard NIL Cases

## 1. User story

Como equipo de authority resolution, quiero usar reformulacion de consultas con LLM solo en casos dificiles para aumentar recall de candidatos sin volver el sistema dependiente de LLMs en el camino principal.

## 2. Context

- Epic: `EPIC-004`
- Dependencias recomendadas: `US-056`, `US-058`

## 3. Acceptance criteria

- [ ] existe un experimento controlado de query reformulation para casos con retrieval vacio o debil
- [ ] el uso de LLM queda bajo feature flag y apagado por defecto
- [ ] se registran consultas alternativas, ganancia de retrieval y costo operativo
- [ ] el sistema no rompe si el proveedor LLM no esta configurado o falla
- [ ] las variantes generadas no sustituyen la evidencia deterministicamente explicable ya existente

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

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Notes for prioritization

- prioridad menor que `US-056` y `US-058`
- debe entrar como experimento medido, no como cambio arquitectonico base
