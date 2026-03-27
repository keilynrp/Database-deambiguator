# US-053 - Verificaciones operativas y alertas base

## 1. User story

Como equipo de operaciones, quiero verificaciones operativas y alertas base para detectar temprano degradaciones del servicio.

## 2. Context

- Epic: `EPIC-015`
- Sprint objetivo: `SPRINT-104`

## 3. Acceptance criteria

- [x] existe lista minima de checks operativos
- [x] se define como alertar fallos relevantes
- [x] la operacion tiene una base repetible de monitoreo

## 4. Functional notes

- complementa health y telemetry
- foco en baseline reusable, no en observabilidad enterprise

## 5. Technical notes

- docs operativas
- integrations o alerting base
- endpoint reusable: `GET /ops/checks`
- ejecucion con notify explicito: `POST /ops/checks/run?notify=true`
- event bridge: `ops.check_failed` sobre `AlertChannel`

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Plan: baseline de checks sobre DB, schedulers y readiness de alertado usando runtime real del backend
- Docs: `README.md`, `docs/TECHNICAL_ONBOARDING.md`, `docs/product/epics/EPIC-015-observability-and-operations.md`, `docs/product/TRACEABILITY_MATRIX.md`, `docs/product/sprints/SPRINT-104.md`
- Checks: `backend/tests/test_sprint104_ops_checks.py`, `backend/tests/test_sprint61.py`, `backend/tests/test_sprint79.py`, `backend/tests/test_sprint68d.py`, `backend/tests/test_sprint104_health_logging.py`
