# EPIC-007 - AI, RAG and Context Engineering

## 1. Summary

Consolidar la capa de inteligencia contextual del producto: RAG, proveedores LLM, tool loop, context snapshots y experiencia de consulta asistida.

## 2. Problem

- el sistema ya tiene una capa AI avanzada, pero su trazabilidad de producto es dispersa
- RAG, context engineering y tool calling son diferenciales fuertes y deben tener identidad de roadmap
- sin una epic clara, el equipo puede tratar AI como accesorios y no como plataforma

## 3. Objective

Convertir la capa AI de UKIP en un frente de producto trazable y evolutivo.

## 4. User value

Como investigador o analista, quiero consultar y explorar mi base de conocimiento con contexto y herramientas para obtener respuestas accionables, explicables y conectadas al dataset real.

## 5. Scope

Incluye:

- RAG
- context snapshots
- registry de herramientas
- agentic mode
- UI de consulta AI

Excluye:

- mejoras genericas de copy o UI que no cambien la capacidad AI

## 6. Success criteria

- el backlog del frente AI queda agrupado y referenciable
- historias futuras de RAG y agentic mode parten de esta epic
- existe una base documental para priorizar robustez, seguridad y UX de AI

## 7. Technical impact

- backend: `backend/routers/ai_rag.py`, `context.py`, `tool_registry.py`, `llm_agent.py`
- frontend: `frontend/app/rag/`, componentes relacionados
- tests: `frontend/__tests__/RAGChatInterface.test.tsx`

## 8. Risks

- riesgo: expandir AI sin controles de producto ni criterios de aceptacion claros
- impacto: deuda funcional, riesgos de UX y de gobernanza
- mitigacion: exigir historias verificables y evidencia funcional

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-005 | Backfillear el frente AI/RAG en el sistema operativo de producto | Planned |
| US-006 | Formalizar criterios operativos para agentic mode y contexto | Planned |
| US-030 | Respuestas RAG con grounding y fuentes | Planned |
| US-031 | Agentic mode con herramientas y trazabilidad | Planned |
| US-032 | Contextos de analisis reutilizables | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Incorporar AI/RAG al backlog y trazabilidad viva |

## 11. Evidence

- Docs: `README.md`, `API.md`
- Codigo: `backend/routers/ai_rag.py`, `frontend/app/rag/`
