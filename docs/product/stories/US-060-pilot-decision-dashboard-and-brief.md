# US-060 - Pilot Decision Dashboard and Exportable Brief

## 1. Summary

Entregar un dashboard inicial de valor ejecutivo y un brief exportable para que
UKIP pueda demostrar resultado util desde un dataset importado, sin depender de
exploracion tecnica profunda.

## 2. Problem

- hoy UKIP tiene buenas capacidades tecnicas, pero el camino desde importacion
  hasta insight demostrable todavia puede sentirse disperso
- para pilotos comerciales y validaciones con stakeholders, hace falta una
  salida clara, compacta y facil de presentar
- sin un dashboard inicial orientado a decision, el producto puede percibirse
  como potente pero todavia dificil de vender o validar rapidamente

## 3. Objective

Reducir el tiempo entre una importacion valida y una salida ejecutiva
presentable, conectando KPIs, hallazgos y export de brief.

## 4. User value

Como usuario de negocio, investigacion o partnership, quiero importar datos y
obtener rapidamente un dashboard y un brief exportable que resuman hallazgos,
prioridades y siguientes pasos.

## 5. Scope

Incluye:

- dashboard inicial orientado a decision
- KPIs de alto valor y baja ambiguedad
- seccion de hallazgos o prioridades
- export de brief/artifact presentable
- CTA clara desde onboarding, import o dashboard landing

Excluye:

- dashboard totalmente configurable
- reporting enterprise avanzado
- narrativas generativas largas o dependientes de LLM por defecto

## 6. Acceptance criteria

- tras una importacion valida, el usuario puede abrir un dashboard inicial con
  valor ejecutivo claro
- el dashboard muestra entre 3 y 5 KPIs accionables
- existe una seccion visible de hallazgos, riesgos o prioridades
- el usuario puede exportar un brief/artifact presentable
- el flujo desde importacion hacia el dashboard es obvio y corto
- la experiencia funciona sin depender de features experimentales

## 7. Suggested KPIs

- total de entidades importadas
- cobertura por tipo o fuente
- porcentaje con enrichment o authority linkage
- principales gaps o records que requieren revision
- top hallazgos o señales prioritarias

## 8. Technical impact

- `backend/routers/dashboards.py`
- `backend/routers/artifacts.py`
- `backend/routers/reports.py`
- `frontend/app/dashboards/`
- posibles ajustes en onboarding o import para CTA/post-import redirect

## 9. Risks

- riesgo: crear un dashboard demasiado generico y poco vendible
- impacto: baja claridad comercial
- mitigacion: enfocar el primer corte a un caso piloto concreto y un set pequeno
  de KPIs

- riesgo: mezclar demasiadas vistas o opciones en el primer release
- impacto: complejidad y ruido visual
- mitigacion: priorizar un dashboard inicial simple con brief exportable

## 10. Delivery proposal

### Cut 1

- dashboard inicial con KPIs y hallazgos
- CTA clara desde import
- estado vacio bien guiado

### Cut 2

- exportable brief/artifact
- seccion de prioridades y recomendaciones estructuradas

### Cut 3

- refinamiento de narrativa, layout y caso piloto por nicho

## 11. Evidence

- `docs/product/COMMERCIAL_MVP.md`
- `docs/product/epics/EPIC-008-dashboards-and-artifacts.md`
- `backend/routers/dashboards.py`
- `backend/routers/artifacts.py`
- `backend/routers/reports.py`
