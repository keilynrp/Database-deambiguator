# US-055 - Author Resolution Engine MVP

## 1. User story

Como analista o equipo de research intelligence, quiero resolver identidades de autores de forma adaptativa y explicable para consolidar portafolios sin depender de revision manual masiva.

## 2. Context

- Epic: `EPIC-004`
- Sprint objetivo: `SPRINT-106`

## 3. Acceptance criteria

- [x] existe flujo author-only de resolucion adaptativa
- [x] el sistema clasifica cada caso con `complexity_score`
- [x] el sistema persiste `resolution_route` y evidencia
- [x] existe resultado explicito `NIL` para casos no concluyentes
- [x] el uso de LLM queda acotado a casos ambiguos y nunca es obligatorio para casos simples
- [x] no se introduce infraestructura operativa nueva obligatoria para el MVP

## 4. Functional notes

- foco exclusivo en `author disambiguation`
- rutas esperadas: `fast_path`, `hybrid_path`, `llm_path`, `manual_review`
- el MVP debe servir para portafolios de publicaciones y autores

## 5. Technical notes

- `backend/authority/resolver.py`
- `backend/authority/scoring.py`
- `backend/authority/author_resolution.py`
- `backend/routers/authority.py`
- `backend/models.py`
- `frontend/app/authority/`
- `docs/product/AUTHOR_RESOLUTION_ENGINE_MVP.md`

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Blueprint: `docs/product/AUTHOR_RESOLUTION_ENGINE_MVP.md`
- Base tecnica actual: `backend/authority/resolver.py`, `backend/authority/scoring.py`, `backend/routers/authority.py`
- Endpoint principal: `POST /authority/authors/resolve`
- Cola operativa: `GET /authority/authors/review-queue`
- Persistencia: `AuthorityRecord.resolution_route`, `complexity_score`, `review_required`, `nil_reason`
- Migracion: `alembic/versions/a2b3c4d5e6f7_sprint_106_author_resolution_engine.py`
- Tests: `backend/tests/test_sprint106_author_resolution_engine.py`, `backend/tests/test_sprint106_author_review_queue.py`
- Riesgo clave: evitar crear un subsistema paralelo o introducir `pgvector` / GraphDB antes de validar demanda
