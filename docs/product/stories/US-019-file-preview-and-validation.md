# US-019 - Preview y validacion de archivos antes de importar

## 1. User story

Como operador de datos, quiero previsualizar y validar un archivo antes de importarlo para detectar problemas temprano y evitar cargas defectuosas.

## 2. Context

- Epic: `EPIC-002`
- Sprint objetivo: `SPRINT-103`

## 3. Acceptance criteria

- [ ] el sistema muestra columnas y muestras del archivo antes de importar
- [ ] se informan errores o limites de formato y tamano
- [ ] el usuario puede decidir continuar o corregir antes del import final

## 4. Functional notes

- flujo: subir archivo -> preview -> ver advertencias -> confirmar o cancelar
- edge cases: archivo vacio, columnas ambiguas, formato no soportado

## 5. Technical notes

- `backend/routers/ingest.py`
- `frontend/app/import/`
- parsers y validadores

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- API examples:
