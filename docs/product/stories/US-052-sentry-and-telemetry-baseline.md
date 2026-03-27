# US-052 - Baseline de Sentry y telemetria operativa

## 1. User story

Como equipo tecnico, quiero una baseline de telemetry para enterarme de errores y degradaciones sin depender solo de inspeccion manual.

## 2. Context

- Epic: `EPIC-015`
- Sprint objetivo: `SPRINT-104`

## 3. Acceptance criteria

- [x] existe baseline clara para Sentry o telemetry equivalente
- [x] los errores criticos tienen mejor visibilidad
- [x] la activacion y configuracion quedan documentadas

## 4. Functional notes

- baseline operativa, no plataforma de observabilidad completa
- activacion explicita y conservadora para evitar side effects en runtime

## 5. Technical notes

- setup actual de sentry
- env vars
- docs operativas
- `backend/telemetry.py` encapsula inicializacion segura e idempotente
- Sentry queda deshabilitado por defecto y solo se activa con `SENTRY_ENABLED=1`
- tracing queda separado de la activacion base y sigue apagado salvo `SENTRY_ENABLE_TRACING=1`

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- PR:
- Test: `backend/tests/test_sprint104_health_logging.py`, `backend/tests/test_sprint104_telemetry.py`, `backend/tests/test_sprint94_pg_hardening.py`, `backend/tests/test_sprint86_5.py`
- Docs: `.env.example`, `README.md`, `docs/TECHNICAL_ONBOARDING.md`, `docs/product/epics/EPIC-015-observability-and-operations.md`, `docs/product/TRACEABILITY_MATRIX.md`, `docs/product/sprints/SPRINT-104.md`
