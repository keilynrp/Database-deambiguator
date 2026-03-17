# US-023 - Visualizacion y accion sobre quality score

## 1. User story

Como analista, quiero ver y usar el quality score para priorizar entidades problematicas y mejorar la calidad del dataset.

## 2. Context

- Epic: `EPIC-003`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el quality score es visible en los flujos relevantes
- [ ] se puede filtrar o priorizar por score
- [ ] el usuario entiende los factores que influyen en la puntuacion

## 4. Functional notes

- flujo: revisar catalogo -> filtrar por calidad -> abrir entidad -> tomar accion
- edge cases: score nulo, score desactualizado, score alto con datos pobres

## 5. Technical notes

- `backend/routers/quality.py`
- `backend/models.py`
- `frontend/app/entities/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
