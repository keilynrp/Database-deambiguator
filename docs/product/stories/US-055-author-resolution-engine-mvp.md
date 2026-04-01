# US-055 - Author Resolution Engine MVP

## 1. User story

Como analista o equipo de research intelligence, quiero resolver identidades de autores de forma adaptativa y explicable para consolidar portafolios sin depender de revision manual masiva.

## 2. Context

- Epic: `EPIC-004`
- Sprint objetivo: `SPRINT-106`

## 3. Acceptance criteria

- [ ] existe flujo author-only de resolucion adaptativa
- [ ] el sistema clasifica cada caso con `complexity_score`
- [ ] el sistema persiste `resolution_route` y evidencia
- [ ] existe resultado explicito `NIL` para casos no concluyentes
- [ ] el uso de LLM queda acotado a casos ambiguos y nunca es obligatorio para casos simples
- [ ] no se introduce infraestructura operativa nueva obligatoria para el MVP

## 4. Functional notes

- foco exclusivo en `author disambiguation`
- rutas esperadas: `fast_path`, `hybrid_path`, `llm_path`, `manual_review`
- el MVP debe servir para portafolios de publicaciones y autores

## 5. Technical notes

- `backend/authority/resolver.py`
- `backend/authority/scoring.py`
- `backend/routers/authority.py`
- `backend/models.py`
- `frontend/app/authority/`
- `docs/product/AUTHOR_RESOLUTION_ENGINE_MVP.md`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- Blueprint: `docs/product/AUTHOR_RESOLUTION_ENGINE_MVP.md`
- Base tecnica actual: `backend/authority/resolver.py`, `backend/authority/scoring.py`, `backend/routers/authority.py`
- Riesgo clave: evitar crear un subsistema paralelo o introducir `pgvector` / GraphDB antes de validar demanda
