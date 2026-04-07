# US-069 - Emerging Topic Trend Signals

## 1. Summary

Agregar una capa experimental y conservadora de senales de tendencia emergente
para identificar combinaciones tematicas que parecen acelerar en ventanas
temporales recientes.

## 2. Problem

- UKIP ya muestra conceptos y clusters, pero no traduce todavia la evolucion
  temporal en una senal prospectiva util
- sin esta capa, el sistema describe el presente mejor que el posible futuro
- el forecasting prematuro puede ser metodologicamente debil y facil de
  sobreprometer

## 3. Objective

Construir una primera capa de senales de tendencia emergente basada en series
temporales y crecimiento relativo, sin venderla todavia como prediccion fuerte.

## 4. User value

Como responsable de inteligencia investigativa, quiero detectar temas o
combinaciones que muestran aceleracion para decidir donde profundizar antes que
el resto.

## 5. Scope

Incluye:

- senales de aceleracion por concepto o combinacion de conceptos
- ventanas temporales comparables
- explicacion de por que una senal se considera emergente

Excluye:

- prediccion exacta a 2 anos
- modelos complejos de forecasting listos para produccion
- promesas comerciales fuertes sobre prediccion automatica

## 6. Acceptance criteria

- UKIP puede calcular una senal de aceleracion para conceptos seleccionados
- cada senal muestra evidencia temporal y nivel de confianza conservador
- la UI la presenta como tendencia o early signal, no como certeza
- el benchmark o evaluacion interna puede detectar regresiones del metodo

## 7. Technical impact

- `backend/analyzers/topic_modeling.py`
- `backend/services/analytics_service.py`
- `frontend/app/analytics/`
- potencial extension del benchmark en `EPIC-006`

## 8. Risks

- riesgo: sobreprometer capacidad predictiva
- impacto: dano de credibilidad
- mitigacion: tratarlo como experimental y apoyarlo en evidencia temporal visible

- riesgo: basarse en series temporales demasiado pobres
- impacto: falsas senales
- mitigacion: exigir umbrales minimos de volumen y cobertura antes de emitir tendencias

## 9. Delivery proposal

### Cut 1

- senal simple de aceleracion reciente
- explicacion temporal visible

### Cut 2

- combinaciones de keywords o conceptos
- comparacion por dominio o dataset

## 10. Evidence

- `docs/product/stories/US-060-pilot-decision-dashboard-and-brief.md`
- `docs/product/stories/US-061-decision-recommendations-and-priority-actions.md`
- `docs/product/stories/US-058-ukip-nil-benchmark-and-evaluation-pack.md`
