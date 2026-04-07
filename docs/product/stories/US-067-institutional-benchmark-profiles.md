# US-067 - Institutional Benchmark Profiles

## 1. Summary

Permitir cargar y aplicar marcos externos de evaluacion institucional para
traducir el grafo y los indicadores de UKIP en criterios comparables para
gestion academica e I+D.

## 2. Problem

- UKIP ya describe portafolios, autores y produccion, pero todavia no los
  traduce a marcos concretos de evaluacion institucional
- sin perfiles de benchmark nativos, el usuario debe interpretar manualmente
  si una unidad, autor o grupo cumple con criterios como REF, SNI o esquemas
  internos
- esto reduce el valor de decision intelligence para oficinas de investigacion

## 3. Objective

Crear una capa configurable de benchmark institucional que permita mapear
metricas, thresholds y reglas a perfiles de evaluacion reutilizables.

## 4. User value

Como responsable de investigacion o planeacion, quiero comparar mi portafolio
contra un marco institucional explicito para detectar brechas, priorizar apoyo
y anticipar resultados de evaluacion.

## 5. Scope

Incluye:

- definicion de perfiles de benchmark institucional
- reglas y thresholds configurables por framework
- evaluacion baseline de cumplimiento por autor, unidad o dataset
- visualizacion resumida en dashboard y brief

Excluye:

- automatizacion completa de promociones o ranking oficial
- modelos predictivos avanzados
- certificacion formal del framework externo

## 6. Acceptance criteria

- UKIP permite registrar al menos un perfil de benchmark institucional
- el sistema calcula un baseline de cumplimiento o gap para el dataset
- los resultados muestran evidencia de que regla o threshold disparo cada gap
- el dashboard o brief puede reflejar el resultado del benchmark

## 7. Example frameworks

- REF UK
- SNI Mexico
- criterios institucionales internos por universidad o centro

## 8. Technical impact

- `backend/routers/analytics.py`
- `backend/services/analytics_service.py`
- `backend/models.py`
- `frontend/app/analytics/`
- `frontend/app/reports/`

## 9. Risks

- riesgo: sobrerrepresentar benchmarks externos como verdad universal
- impacto: recomendaciones engañosas
- mitigacion: perfilar reglas como configurables y explicitas, no como juicio final

- riesgo: acoplar demasiado el producto a un solo pais o marco
- impacto: menor portabilidad comercial
- mitigacion: modelar perfiles generalizables y versionados

## 10. Delivery proposal

### Cut 1

- modelo de perfil institucional
- baseline de evaluacion simple por reglas
- visualizacion resumida de gaps

### Cut 2

- multiples perfiles por tenant
- export de benchmark junto al brief
- soporte para unidades y autores

## 11. Evidence

- `docs/product/stories/US-060-pilot-decision-dashboard-and-brief.md`
- `docs/product/stories/US-061-decision-recommendations-and-priority-actions.md`
- `docs/product/stories/US-055-author-resolution-engine-mvp.md`
