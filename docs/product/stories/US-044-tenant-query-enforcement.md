# US-044 - Enforcements de tenant en queries y acceso

## 1. User story

Como cliente institucional, quiero que las consultas y escrituras respeten tenant isolation para que mis datos no se mezclen con otros.

## 2. Context

- Epic: `EPIC-012`
- Sprint objetivo: `SPRINT-105`

## 3. Acceptance criteria

- [x] las queries criticas aplican filtros de tenant
- [x] endpoints sensibles no devuelven recursos cruzados
- [x] el enforcement es reusable y testeable

## 4. Functional notes

- se aplica enforcement reusable sobre recursos criticos: entities, analytics, authority, disambiguation, harmonization, relationships y workflows
- super admin mantiene visibilidad global
- usuarios sin org activa quedan en scope legado `org_id IS NULL` para compatibilidad transicional sin exponer datos tenantizados

## 5. Technical notes

- auth deps
- queries de entidades y recursos multiusuario
- helper central en `backend/tenant_access.py`
- columnas `org_id` agregadas a tablas core via migracion `e8f9a0b1c2d3`
- cache keys de analytics y queries SQL directas alineadas con scope tenant

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Date: `2026-03-28`
- Migration: `alembic/versions/e8f9a0b1c2d3_sprint_105_tenant_scope_columns.py`
- Code:
  - `backend/tenant_access.py`
  - `backend/routers/entities.py`
  - `backend/routers/analytics.py`
  - `backend/routers/authority.py`
  - `backend/routers/disambiguation.py`
  - `backend/routers/harmonization.py`
  - `backend/routers/relationships.py`
  - `backend/routers/workflows.py`
- Tests:
  - `backend/tests/test_sprint105_tenant_enforcement.py`
  - targeted regression suites for analytics, authority, workflows, ingest, relationships and entity reads
- Docs:
  - `docs/product/epics/EPIC-012-tenant-isolation-and-access-control.md`
  - `docs/product/sprints/SPRINT-105.md`
