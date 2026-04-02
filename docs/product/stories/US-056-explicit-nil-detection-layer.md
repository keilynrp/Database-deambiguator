# US-056 - Explicit NIL Detection Layer

## 1. User story

Como analista de research intelligence, quiero que el sistema detecte de forma explicita cuando una entidad no es enlazable para distinguir entre baja confianza, ambiguedad real y ausencia de cobertura en la KB.

## 2. Context

- Epic: `EPIC-004`
- Dependencia natural: `US-055`

## 3. Acceptance criteria

- [x] existe un modulo explicito de deteccion `NIL` separado del routing general
- [x] cada decision `NIL` expone `nil_score` o criterio equivalente mas `nil_reason`
- [x] el sistema diferencia al menos entre:
  - falta de candidatos
  - cobertura insuficiente
  - ambiguedad no resoluble
  - evidencia conflictiva
- [x] la deteccion `NIL` queda trazable en metricas operativas
- [x] el baseline inicial no introduce infraestructura nueva obligatoria

## 4. Functional notes

- author-first, pero reusable para otros tipos de entidad mas adelante
- no reemplaza `resolution_route`; lo complementa
- debe mejorar la operabilidad de review queue y de los indicadores de calidad

## 5. Technical notes

- `backend/authority/author_resolution.py`
- `backend/authority/scoring.py`
- `backend/routers/authority.py`
- `backend/models.py`
- `backend/schemas.py`
- `frontend/app/authority/page.tsx`
- tests de authority y author resolution

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Detector explicito: `backend/authority/nil_detection.py`
- Integracion de routing: `backend/authority/author_resolution.py`
- Persistencia: `AuthorityRecord.nil_score` en `backend/models.py`
- API:
  - `POST /authority/authors/resolve`
  - `GET /authority/authors/review-queue`
  - `GET /authority/authors/metrics`
- UI: `frontend/app/authority/page.tsx`
- Migracion: `alembic/versions/b1c2d3e4f5a6_sprint_106_nil_detection_layer.py`
- Tests:
  - `backend/tests/test_sprint106_nil_detection.py`
  - `backend/tests/test_sprint106_author_resolution_engine.py`
  - `backend/tests/test_sprint106_author_review_queue.py`
  - `backend/tests/test_sprint106_author_metrics.py`
  - `backend/tests/test_sprint86_5.py`

## 8. Notes for prioritization

- es la pieza del paper mas alineada con el estado actual de UKIP
- agrega valor operativo inmediato sin exigir vertical biomedica ni datasets externos
