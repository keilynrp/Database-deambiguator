# US-028 - Consulta natural conectada a OLAP

## 1. User story

Como analista, quiero hacer preguntas en lenguaje natural y obtener resultados conectados al motor OLAP para explorar datos sin escribir consultas manuales.

## 2. Context

- Epic: `EPIC-006`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el usuario puede ingresar una pregunta natural
- [ ] el sistema traduce la pregunta a una consulta valida
- [ ] el resultado es interpretable y conectable al explorador OLAP

## 4. Functional notes

- flujo: escribir pregunta -> generar consulta -> ver resultado -> abrir OLAP
- edge cases: dimensiones invalidas, consulta ambigua, respuesta vacia

## 5. Technical notes

- `backend/routers/nlq.py`
- `backend/olap.py`
- UI de analytics o explorer

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- API examples:
