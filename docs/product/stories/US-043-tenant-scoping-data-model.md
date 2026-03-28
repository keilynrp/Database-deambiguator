# US-043 - Scoping de tenant en modelo de datos

## 1. User story

Como arquitecto del producto, quiero identificar e introducir scoping de tenant en el modelo para construir aislamiento real de datos.

## 2. Context

- Epic: `EPIC-012`
- Sprint objetivo: `SPRINT-105`

## 3. Acceptance criteria

- [x] existe mapa de recursos que requieren `org_id` o equivalente
- [x] se define orden incremental de migracion de tablas
- [x] el modelo objetivo de tenant isolation queda claro

## 4. Functional notes

- foco en discovery y diseño con impacto alto

## 5. Technical notes

- `backend/models.py`
- routers de entidades, dashboards, workflows, reports

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Modelo objetivo: `docs/product/TENANT_SCOPING_MODEL.md`
- Riesgos: no aplicar enforcement antes de cerrar la secuencia de migracion por olas
- Plan: `backend/tenant_scoping.py`, `GET /ops/tenant-model`, `backend/tests/test_sprint105_tenant_model.py`
