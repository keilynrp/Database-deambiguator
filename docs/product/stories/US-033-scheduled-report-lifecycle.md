# US-033 - Ciclo de vida de reportes programados

## 1. User story

Como admin o operador, quiero crear, pausar y ejecutar reportes programados para distribuir informacion de manera automatica.

## 2. Context

- Epic: `EPIC-009`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el usuario puede crear y editar una programacion de reporte
- [ ] existe envio manual o ejecucion inmediata
- [ ] errores, pausas y ultimos resultados son visibles

## 4. Functional notes

- flujo: crear schedule -> activar -> revisar historial -> pausar o enviar ahora
- edge cases: destinatario invalido, fallo de generacion, schedule pausado

## 5. Technical notes

- `backend/routers/scheduled_reports.py`
- `backend/report_builder.py`
- `frontend/app/reports/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
