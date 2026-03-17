# US-017 - Gestion de schemas de dominio

## 1. User story

Como admin o implementador, quiero gestionar dominios y sus schemas para poder adaptar UKIP a distintos tipos de entidad sin romper el modelo universal.

## 2. Context

- Epic: `EPIC-001`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] existe una forma clara de listar y seleccionar dominios
- [ ] el schema de dominio define campos o comportamiento esperable del catalogo
- [ ] la documentacion operativa deja claro como se conectan domain YAML y entidad universal

## 4. Functional notes

- flujo: seleccionar dominio -> revisar schema -> usarlo en importacion o navegacion
- edge cases: dominio inexistente, schema invalido, mismatch entre schema y datos reales

## 5. Technical notes

- `backend/domains/`
- `backend/routers/domains.py`
- `frontend/app/domains/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Docs:
