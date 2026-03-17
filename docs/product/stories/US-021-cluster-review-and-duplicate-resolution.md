# US-021 - Revision de clusters y resolucion de duplicados

## 1. User story

Como analista de calidad, quiero revisar clusters de posibles duplicados para confirmar merges o descartar agrupaciones incorrectas.

## 2. Context

- Epic: `EPIC-003`
- Sprint objetivo: `SPRINT-103`

## 3. Acceptance criteria

- [ ] el sistema presenta agrupaciones comprensibles de posibles duplicados
- [ ] el usuario puede resolver, fusionar o descartar candidatos
- [ ] la accion deja trazabilidad operativa

## 4. Functional notes

- flujo: ejecutar clustering -> revisar grupo -> decidir merge o dismiss
- edge cases: grupos grandes, baja confianza, conflictos entre campos

## 5. Technical notes

- `backend/routers/disambiguation.py`
- `frontend/app/disambiguation/`
- motores de clustering

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
