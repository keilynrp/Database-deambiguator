# EPIC-006 - Analytics and Decision Intelligence

## 1. Summary

Formalizar el frente de analitica, OLAP, NLQ y simulacion como una linea central de producto orientada a soporte de decisiones.

## 2. Problem

- analytics es una promesa nuclear del producto
- el frente ya es amplio, pero faltaba su aterrizaje operativo en el nuevo sistema documental
- sin esta epic, dashboard, NLQ, OLAP y modelos de simulacion pueden evolucionar sin una narrativa de valor comun

## 3. Objective

Conectar en una sola epic todas las capacidades que convierten datos y conocimiento en decision intelligence.

## 4. User value

Como tomador de decisiones o analista, quiero explorar indicadores, hacer consultas naturales y correr analitica avanzada para convertir datos en acciones concretas.

## 5. Scope

Incluye:

- analytics dashboard
- OLAP explorer
- NLQ
- Monte Carlo y ROI
- deteccion de gaps y analitica exploratoria

Excluye:

- ingestion previa
- capa AI/RAG conversacional salvo el punto de cruce con NLQ

## 6. Success criteria

- analytics queda reconocido como frente operativo principal
- backlog futuro del frente puede planificarse con una sola referencia
- la trazabilidad conecta modulos, evidencia y valor funcional

## 7. Technical impact

- backend: `analytics.py`, `nlq.py`, `olap.py`, calculos cuantitativos
- frontend: `frontend/app/analytics/`
- tests: seguridad OLAP y tests de analytics asociados

## 8. Risks

- riesgo: trabajar mejoras de analytics de forma reactiva y dispersa
- impacto: experiencia fragmentada y deuda de priorizacion
- mitigacion: toda historia del frente debe vivir bajo esta epic

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-013 | Backfillear el frente de analytics y decision intelligence | Done |
| US-014 | Formalizar criterios operativos para dashboard, NLQ y OLAP | Planned |
| US-027 | Dashboard ejecutivo y metricas clave | Planned |
| US-028 | Consulta natural conectada a OLAP | Planned |
| US-029 | Simulaciones Monte Carlo y artefactos ROI | Planned |
| US-060 | Pilot Decision Dashboard and Exportable Brief | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Incorporar analytics al sistema operativo vivo |

## 11. Evidence

- Codigo: `backend/routers/analytics.py`, `backend/routers/nlq.py`, `backend/olap.py`, `frontend/app/analytics/`
- Docs: `README.md`, `API.md`
- Story: `docs/product/stories/US-060-pilot-decision-dashboard-and-brief.md`
