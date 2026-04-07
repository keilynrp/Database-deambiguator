# US-068 - Research Network Community Detection

## 1. Summary

Agregar deteccion de comunidades en redes de investigacion para encontrar
sub-redes de colaboracion, afinidad tematica y agrupaciones ocultas entre
autores, instituciones y conceptos.

## 2. Problem

- UKIP ya construye relaciones y visualizacion de grafo, pero sus algoritmos
  actuales no exponen comunidades densas de forma operativa
- sin community detection, el analisis de colaboracion se queda corto para I+D
  de nivel avanzado
- esto limita tanto el valor analitico como la futura visualizacion masiva

## 3. Objective

Introducir community detection util y explicable como capa analitica para redes
de investigacion, empezando por algoritmos tipo Louvain o Leiden.

## 4. User value

Como analista de investigacion, quiero identificar comunidades reales de
colaboracion o afinidad para descubrir clusters fuertes, puentes y vacios de
cooperacion entre actores.

## 5. Scope

Incluye:

- deteccion de comunidades sobre subgrafos relevantes
- exposicion de comunidad por nodo y resumen por cluster
- integracion con analytics y futura visualizacion de grafos

Excluye:

- grafo distribuido a gran escala
- cliente WebGL completo
- microservicios separados para graph analytics

## 6. Acceptance criteria

- el backend puede calcular comunidades sobre un subgrafo acotado
- cada nodo relevante puede devolver su comunidad principal
- el sistema puede resumir comunidades por tamano, densidad o actor lider
- la salida queda lista para consumirse desde dashboards o vistas de grafo

## 7. Technical impact

- `backend/graph_analytics.py`
- `backend/routers/graph_export.py`
- `backend/routers/relationships.py`
- `frontend/app/analytics/graph/`
- futura linea `US-062` a `US-066`

## 8. Risks

- riesgo: aplicar algoritmos costosos sobre grafos aun no preparados
- impacto: degradacion de rendimiento
- mitigacion: limitar el primer corte a subgrafos y read models preparados

- riesgo: mostrar clusters poco interpretables
- impacto: baja utilidad para decision makers
- mitigacion: acompanar cada comunidad con explicacion, top nodes y contexto

## 9. Delivery proposal

### Cut 1

- deteccion de comunidades en backend sobre subgrafos controlados
- resumen por comunidad

### Cut 2

- integracion con read-path de visualizacion
- comparacion entre comunidades y puentes

## 10. Evidence

- `docs/product/stories/US-062-graph-visualization-read-path-baseline.md`
- `docs/product/stories/US-063-visualization-preparation-jobs.md`
- `docs/product/stories/US-064-massive-graph-webgl-client.md`
