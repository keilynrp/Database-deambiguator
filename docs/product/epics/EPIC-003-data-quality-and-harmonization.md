# EPIC-003 - Data Quality and Harmonization

## 1. Summary

Fortalecer el conjunto de capacidades que limpian, normalizan, agrupan, transforman y puntuan entidades para convertir datos desordenados en un activo confiable.

## 2. Problem

- la calidad de datos es una propuesta central de valor y a la vez una superficie amplia del producto
- varias capacidades ya existen, pero necesitan trazabilidad operativa comun
- sin una epic fuerte, clustering, transformations, harmonization y quality pueden evolucionar sin cohesion

## 3. Objective

Unificar bajo una sola linea de producto los flujos de calidad, harmonizacion y mejora continua de entidades.

## 4. User value

Como analista de datos, quiero detectar, corregir y transformar inconsistencias rapidamente para confiar en los datos antes de analizarlos o enriquecerlos.

## 5. Scope

Incluye:

- disambiguation
- harmonization
- transformations
- quality score
- faceting y apoyo al filtrado de calidad

Excluye:

- enrichment externo profundo
- analitica avanzada que parte de datos ya limpios

## 6. Success criteria

- las historias del frente de calidad quedan agrupadas bajo una sola epic
- existe trazabilidad entre UI, endpoints y evidencia funcional de calidad
- el backlog futuro de calidad puede priorizarse sin perder el hilo de producto

## 7. Technical impact

- backend: `backend/routers/disambiguation.py`, `harmonization.py`, `transformations.py`, `quality.py`
- frontend: `frontend/app/disambiguation/`, `frontend/app/transformations/`
- tests: `backend/tests/test_sprint87.py`, `test_sprint88.py`, `test_sprint89.py`

## 8. Risks

- riesgo: trabajar mejoras de calidad como tickets aislados
- impacto: baja coherencia de UX y deuda funcional
- mitigacion: toda mejora del frente debe referenciar esta epic

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-003 | Organizar el backlog operativo del frente de calidad | Planned |
| US-004 | Consolidar criterios funcionales de transformations y quality score | Planned |
| US-021 | Revision de clusters y resolucion de duplicados | Planned |
| US-022 | Preview, confirmacion y trazabilidad de transformaciones | Planned |
| US-023 | Visualizacion y accion sobre quality score | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Dejar trazabilidad base del frente de calidad |

## 11. Evidence

- Docs: `README.md`, `CHANGELOG.md`
- Codigo: routers y pantallas del frente de calidad
