# EPIC-001 - Universal Data Engine

## 1. Summary

Consolidar a UKIP como plataforma realmente agnostica de dominio a partir de un modelo de entidad universal consistente, dominios configurables y catalogo operable de punta a punta.

## 2. Problem

- el proyecto ya opera como plataforma multi-dominio, pero parte de la narrativa y algunos artefactos aun arrastran herencia de etapas anteriores
- sin una consolidacion explicita del motor universal, el equipo puede volver a pensar en features aisladas por dominio
- la falta de trazabilidad entre modelo universal, domains registry y UI dificulta evolucion ordenada

## 3. Objective

Hacer que el modelo universal sea una referencia de producto, arquitectura y ejecucion para todas las capacidades del sistema.

## 4. User value

Como operador o analista, quiero trabajar con una sola plataforma capaz de representar distintas entidades y dominios sin cambiar de flujo ni de herramientas.

## 5. Scope

Incluye:

- modelo `UniversalEntity`
- domains registry y schemas YAML
- catalogo universal y detalle de entidad
- consistencia documental del enfoque multi-dominio

Excluye:

- nuevos dominios especializados profundos
- rediseños grandes de analytics o RAG fuera del impacto directo del modelo universal

## 6. Success criteria

- el sistema mantiene un lenguaje y contrato universal para entidades
- los flujos principales de catalogo e importacion reconocen el enfoque multi-dominio
- la documentacion operativa conecta claramente modelo, dominios y experiencia de usuario

## 7. Technical impact

- backend: `backend/models.py`, `backend/domains/`, `backend/routers/entities.py`
- frontend: `frontend/app/entities/`, `frontend/app/page.tsx`
- datos: migraciones futuras si se extiende el modelo universal
- docs: backlog, trazabilidad, onboarding

## 8. Risks

- riesgo: que el equipo siga diseñando historias como si fueran features aisladas
- impacto: deriva conceptual y deuda documental
- mitigacion: obligar a referenciar esta epic en historias transversales de dominio

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-001 | Formalizar la narrativa y trazabilidad del motor universal | Planned |
| US-002 | Validar consistencia entre domains registry, entidades y catalogo | Planned |
| US-017 | Gestion de schemas de dominio | Planned |
| US-018 | Experiencia universal de catalogo y detalle de entidad | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Consolidar la base operativa y documental del motor universal |

## 11. Evidence

- Docs: `docs/EVOLUTION_STRATEGY.md`, `docs/ARCHITECTURE.md`, `docs/product/PROGRAM_BACKLOG.md`
- Codigo: `backend/models.py`, `backend/domains/`, `backend/routers/entities.py`
