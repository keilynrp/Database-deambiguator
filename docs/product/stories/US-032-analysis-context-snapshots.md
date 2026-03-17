# US-032 - Contextos de analisis reutilizables

## 1. User story

Como analista, quiero guardar y reutilizar contextos de analisis para mantener continuidad entre sesiones y consultas AI.

## 2. Context

- Epic: `EPIC-007`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el usuario puede crear o seleccionar un contexto de analisis
- [ ] el contexto influye en la consulta o recuperacion posterior
- [ ] el flujo deja clara la relacion entre contexto activo y respuesta

## 4. Functional notes

- flujo: crear contexto -> activar contexto -> consultar -> recuperar luego
- edge cases: contexto vacio, contexto obsoleto, conflicto entre contextos

## 5. Technical notes

- `backend/routers/context.py`
- `backend/context_engine.py`
- UI relacionada a contextos

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
