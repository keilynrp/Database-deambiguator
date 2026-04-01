# US-045 - Limites y quotas por tenant o plan

## 1. User story

Como equipo comercial y tecnico, quiero limites por tenant o plan para poder controlar uso y preparar enforcement de planes.

## 2. Context

- Epic: `EPIC-012`
- Sprint objetivo: `SPRINT-105`

## 3. Acceptance criteria

- [x] se identifican limites relevantes por plan o tenant
- [x] existe estrategia inicial de enforcement
- [x] el modelo comercial puede apoyarse en estos limites

## 4. Functional notes

- relacionada con rate limiting, quotas y gating por plan
- el baseline comercial se enfoca en organizaciones con planes `free`, `pro` y `enterprise`
- el enforcement hard del MVP se limita a recursos ya scopeados por `org_id`

## 5. Technical notes

- API keys
- rate limiting
- modelo de organizaciones y planes
- `backend/tenant_quotas.py`
- `backend/routers/organizations.py`
- `backend/routers/stores.py`
- `backend/routers/scrapers.py`
- `backend/routers/scheduled_imports.py`
- `backend/routers/scheduled_reports.py`
- `backend/routers/workflows.py`

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Quota engine: `backend/tenant_quotas.py`
- Endpoint: `GET /organizations/{org_id}/quotas`
- Enforcement: `organizations.py`, `stores.py`, `scrapers.py`, `scheduled_imports.py`, `scheduled_reports.py`, `workflows.py`
- Tests: `backend/tests/test_sprint105_tenant_plan_quotas.py`
- Riesgos: `api_keys` y `alert_channels` quedan como guidance comercial parcial hasta completar su scoping por tenant
