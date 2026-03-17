# US-030 - Respuestas RAG con grounding y fuentes

## 1. User story

Como usuario de AI, quiero recibir respuestas RAG con fuentes y grounding para confiar en lo que el sistema me devuelve.

## 2. Context

- Epic: `EPIC-007`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] la respuesta incluye grounding o referencias a fuentes
- [ ] el usuario puede distinguir respuesta generada de evidencia recuperada
- [ ] el flujo maneja ausencia de resultados relevantes

## 4. Functional notes

- flujo: hacer pregunta -> recuperar contexto -> responder con fuentes
- edge cases: corpus vacio, resultados poco relevantes, proveedor caido

## 5. Technical notes

- `backend/routers/ai_rag.py`
- `backend/context.py`
- `frontend/app/rag/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
