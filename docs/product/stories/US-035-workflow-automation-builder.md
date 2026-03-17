# US-035 - Builder de workflows automatizados

## 1. User story

Como operador, quiero definir workflows con triggers, condiciones y acciones para automatizar decisiones operativas del sistema.

## 2. Context

- Epic: `EPIC-009`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el usuario puede definir trigger, condiciones y acciones
- [ ] el workflow queda persistido y administrable
- [ ] el sistema deja claro cuando un workflow se ejecuto o fallo

## 4. Functional notes

- flujo: crear workflow -> configurar reglas -> activar -> revisar ejecuciones
- edge cases: condicion invalida, accion incompleta, eventos no disparados

## 5. Technical notes

- `backend/routers/workflows.py`
- `backend/workflow_engine.py`
- `frontend/app/workflows/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
