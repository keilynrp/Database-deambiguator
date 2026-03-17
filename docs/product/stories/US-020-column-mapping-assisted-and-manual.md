# US-020 - Mapeo manual y asistido de columnas

## 1. User story

Como operador de datos, quiero mapear columnas manualmente o con ayuda AI para transformar archivos heterogeneos en datos compatibles con UKIP.

## 2. Context

- Epic: `EPIC-002`
- Sprint objetivo: `SPRINT-103`

## 3. Acceptance criteria

- [ ] el usuario puede asignar columnas a campos del modelo
- [ ] existe sugerencia asistida cuando aplica
- [ ] el mapping final es visible y confirmable antes de importar

## 4. Functional notes

- flujo: preview -> sugerencia AI -> ajuste manual -> confirmacion
- edge cases: columnas extra, campos obligatorios faltantes, sugerencias poco confiables

## 5. Technical notes

- `backend/routers/ingest.py`
- `backend/routers/column_maps.py`
- `frontend/app/import/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Docs:
