# EPIC-012 - Tenant Isolation and Access Control

## 1. Summary

Convertir el multi-tenancy de UKIP en aislamiento real de datos y control de acceso utilizable en un contexto SaaS serio.

## 2. Problem

- el multi-tenancy actual es parcial y mas cosmetico que real
- sin scoping por tenant, una oferta SaaS multi-cliente no es defendible
- el RBAC actual no alcanza para necesidades enterprise

## 3. Objective

Llevar UKIP de organizaciones nominales a aislamiento real por tenant y enforcement consistente de acceso.

## 4. User value

Como cliente institucional, quiero que mis datos y permisos esten aislados de otros tenants para confiar en la plataforma.

## 5. Scope

Incluye:

- modelo de datos con tenant scoping real
- filtros por tenant
- enforcement de acceso por tenant y recurso
- quotas o limites por tenant/plan

Excluye:

- billing completo
- compliance regulatoria avanzada

## 6. Success criteria

- entidades y recursos clave tienen scoping claro por tenant
- queries relevantes no cruzan datos entre organizaciones
- permisos dejan de ser solo globales por rol

## 7. Technical impact

- modelos ORM
- routers y queries de lectura/escritura
- auth y deps
- posible impacto en dashboards, workflows, reports y artifacts

## 8. Risks

- riesgo: cambio transversal con alto impacto en datos y queries
- impacto: regresiones funcionales y aumento de complejidad
- mitigacion: hacer discovery y rollout incremental por dominios de datos

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-043 | Scoping de tenant en modelo de datos | Done |
| US-044 | Enforcements de tenant en queries y acceso | Done |
| US-054 | Scoping tenant en runtime operativo y jobs derivados | Done |
| US-045 | Limites y quotas por tenant o plan | Done |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-105 | Iniciar tenant isolation real despues del hardening base |

## 11. Evidence

- Valoracion tecnica senior 2026-03-24
- `backend/models.py`
- auth y routers de recursos compartidos
- `backend/tenant_scoping.py`
- `backend/tenant_access.py`
- `GET /ops/tenant-model`
- `docs/product/TENANT_SCOPING_MODEL.md`
- `docs/product/stories/US-044-tenant-query-enforcement.md`
- `alembic/versions/f0a1b2c3d4e5_tenant_scope_operational_resources.py`
- `backend/routers/stores.py`
- `backend/routers/scheduled_imports.py`
- `backend/routers/scheduled_reports.py`
- `backend/routers/scrapers.py`
- `backend/report_builder.py`
- `backend/exporters/excel_exporter.py`
- `backend/exporters/pptx_exporter.py`
- `backend/enrichment_worker.py`
- `backend/workflow_engine.py`
- `backend/tenant_quotas.py`
- `GET /organizations/{org_id}/quotas`
- `backend/tests/test_sprint105_tenant_plan_quotas.py`
- `backend/tests/test_sprint105_tenant_async_runtime.py`
- `docs/product/stories/US-054-tenant-operational-runtime-scoping.md`
- `docs/product/stories/US-045-tenant-plan-quotas.md`
