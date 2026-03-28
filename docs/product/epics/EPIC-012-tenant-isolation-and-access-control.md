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
| US-044 | Enforcements de tenant en queries y acceso | Planned |
| US-045 | Limites y quotas por tenant o plan | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-105 | Iniciar tenant isolation real despues del hardening base |

## 11. Evidence

- Valoracion tecnica senior 2026-03-24
- `backend/models.py`
- auth y routers de recursos compartidos
- `backend/tenant_scoping.py`
- `GET /ops/tenant-model`
- `docs/product/TENANT_SCOPING_MODEL.md`
