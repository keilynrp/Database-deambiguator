# US-054 - Tenant scoping en runtime operativo y jobs derivados

## 1. User story

Como cliente institucional, quiero que schedulers, stores, scrapers y reportes derivados respeten mi tenant para que el aislamiento no se rompa fuera de los endpoints CRUD.

## 2. Context

- Epic: `EPIC-012`
- Sprint objetivo: `SPRINT-105`

## 3. Acceptance criteria

- [x] recursos operativos compartidos (`StoreConnection`, `ScheduledImport`, `ScheduledReport`, `WebScraperConfig`) exponen `org_id`
- [x] los routers de stores, schedules y scrapers aplican tenant scoping reusable
- [x] los jobs de enrichment/reporting en background heredan el tenant correcto y no mezclan configuraciones ni datos
- [x] los builders/exporters de reportes respetan `domain_id` y `org_id`

## 4. Functional notes

- cubre el runtime operativo que seguía global después de `US-044`
- mantiene compatibilidad transicional con recursos legacy globales (`org_id = NULL`)
- no cubre todavía quotas ni billing por plan

## 5. Technical notes

- migration incremental con columnas `org_id` en recursos operativos
- validación de asociación `ScheduledImport -> StoreConnection` dentro del mismo tenant
- scoping explícito en report builders y exporters reutilizados por reportes manuales y programados
- scrapers de enrichment filtrados por tenant de la entidad

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Migration: `alembic/versions/f0a1b2c3d4e5_tenant_scope_operational_resources.py`
- Backend:
  - `backend/models.py`
  - `backend/routers/stores.py`
  - `backend/routers/scheduled_imports.py`
  - `backend/routers/scheduled_reports.py`
  - `backend/routers/scrapers.py`
  - `backend/routers/reports.py`
  - `backend/enrichment_worker.py`
  - `backend/workflow_engine.py`
  - `backend/report_builder.py`
  - `backend/exporters/excel_exporter.py`
  - `backend/exporters/pptx_exporter.py`
- Tests:
  - `backend/tests/test_sprint105_tenant_async_runtime.py`
  - targeted regression suites for stores, scheduled imports, scheduled reports, scrapers, workflows and report exports
- Docs:
  - `backend/tenant_scoping.py`
  - `docs/product/epics/EPIC-012-tenant-isolation-and-access-control.md`
  - `docs/product/sprints/SPRINT-105.md`
