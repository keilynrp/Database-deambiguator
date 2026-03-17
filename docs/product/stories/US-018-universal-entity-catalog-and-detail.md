# US-018 - Experiencia universal de catalogo y detalle de entidad

## 1. User story

Como analista, quiero navegar un catalogo universal y ver el detalle de una entidad para trabajar con cualquier dominio desde un flujo consistente.

## 2. Context

- Epic: `EPIC-001`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el catalogo permite navegar entidades sin depender de un dominio unico
- [ ] el detalle de entidad expone una estructura consistente para overview, enrichment, authority y graph
- [ ] filtros y labels respetan el modelo universal

## 4. Functional notes

- flujo: listar entidades -> filtrar -> abrir detalle -> revisar tabs clave
- estados: vacio, loading, error, entidad incompleta

## 5. Technical notes

- `backend/routers/entities.py`
- `frontend/app/page.tsx`
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
