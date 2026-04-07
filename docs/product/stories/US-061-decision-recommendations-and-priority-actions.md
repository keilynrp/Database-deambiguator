# US-061 - Decision Recommendations and Priority Actions

## 1. Summary

Agregar una capa corta y explicable de recomendaciones y acciones prioritarias
sobre el dashboard ejecutivo y el brief piloto, para convertir indicadores en
proximos pasos mas claros.

## 2. Problem

- `US-060` ya entrega dashboard y brief exportable, pero el usuario todavia
  tiene que interpretar por su cuenta que hacer primero
- sin una capa minima de recomendaciones, el flujo puede quedarse en
  visualizacion interesante pero no necesariamente accionable
- para validaciones comerciales, conviene que UKIP sugiera prioridades de forma
  conservadora y entendible

## 3. Objective

Convertir senales del dashboard en una lista corta de acciones recomendadas y
prioridades explicables, visibles tanto en UI como en el brief.

## 4. User value

Como usuario de negocio o investigacion, quiero ver cuales son las siguientes
acciones recomendadas sobre el dataset importado para poder priorizar revisiones,
enrichment y seguimiento sin interpretar todo manualmente.

## 5. Scope

Incluye:

- recomendaciones generadas de forma determinista a partir de KPIs existentes
- lista corta de prioridades o acciones sugeridas
- inclusion de estas recomendaciones en dashboard y brief
- tono conservador y explicable

Excluye:

- recomendaciones generativas abiertas basadas en LLM
- scoring predictivo complejo
- automatizacion completa de acciones

## 6. Acceptance criteria

- el dashboard muestra una lista breve de acciones recomendadas
- cada recomendacion se apoya en una senal visible del dataset
- el brief exportable puede incluir esa misma lista
- las recomendaciones son claras, priorizadas y no dependen de features
  experimentales

## 7. Example actions

- correr enrichment bulk si la cobertura es baja
- revisar records de baja calidad antes de exportar
- priorizar entidades top-impact para analisis manual
- explorar conceptos principales si la densidad semantica ya es suficiente

## 8. Technical impact

- `backend/routers/analytics.py`
- `backend/services/analytics_service.py`
- `frontend/app/analytics/dashboard/page.tsx`
- `frontend/app/reports/page.tsx`
- posible extension del builder de reportes

## 9. Risks

- riesgo: sugerencias demasiado genericas o vacias
- impacto: baja utilidad real
- mitigacion: limitar el primer corte a pocas reglas deterministas y trazables

- riesgo: sonar demasiado prescriptivo
- impacto: sobreventa funcional
- mitigacion: presentar recomendaciones como "suggested next actions"

## 10. Delivery proposal

### Cut 1

- motor simple de acciones recomendadas
- render en dashboard

### Cut 2

- inclusion en brief exportable
- refinamiento de copy y prioridad

## 11. Evidence

- `docs/product/stories/US-060-pilot-decision-dashboard-and-brief.md`
- `frontend/app/analytics/dashboard/page.tsx`
- `frontend/app/reports/page.tsx`
- `backend/services/analytics_service.py`
