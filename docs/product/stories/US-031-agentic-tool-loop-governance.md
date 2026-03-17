# US-031 - Agentic mode con herramientas y trazabilidad

## 1. User story

Como usuario avanzado, quiero que el asistente pueda usar herramientas con trazabilidad para resolver consultas complejas sin perder control del proceso.

## 2. Context

- Epic: `EPIC-007`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el sistema permite activar o desactivar agentic mode
- [ ] las herramientas usadas quedan visibles
- [ ] el usuario puede entender el resultado y sus iteraciones principales

## 4. Functional notes

- flujo: activar modo agentic -> enviar consulta -> revisar herramientas usadas
- edge cases: loop excesivo, herramienta falla, respuesta parcial

## 5. Technical notes

- `backend/llm_agent.py`
- `backend/tool_registry.py`
- `backend/routers/ai_rag.py`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Logs:
