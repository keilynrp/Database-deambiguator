# US-062 - Graph Visualization Read-Path Baseline

## 1. Summary

Definir y preparar una arquitectura de lectura especializada para visualizacion
de grafos I+D a gran escala, desacoplando el write-path transaccional del
read-path visual y analitico.

## 2. Problem

- hoy UKIP puede exportar grafos, calcular analitica de grafo y renderizar
  subgrafos pequenos, pero no esta pensado para visualizacion masiva
- calcular BFS, layouts y metricas pesadas request por request degrada el
  rendimiento del core transaccional
- si el producto evoluciona hacia portafolios I+D hiperconectados, hace falta
  una capa especializada para servir vistas de grafo precocinadas

## 3. Objective

Establecer la base arquitectonica para un read-path de visualizacion masiva de
grafos, con precomputacion, snapshots y payloads optimizados para cliente.

## 4. User value

Como analista o investigador, quiero explorar grafos grandes sin bloquear la
plataforma ni esperar calculos pesados cada vez que abro una vista de red.

## 5. Scope

Incluye:

- definicion del read-path de visualizacion
- snapshots o view-models pregenerados
- preparacion para layouts y comunidades precomputadas
- consistencia eventual explicita
- base para cliente WebGL futuro

Excluye:

- migracion inmediata a microservicios separados
- adopcion temprana de una graph DB externa
- reemplazo completo del visualizador actual en el primer corte

## 6. Acceptance criteria

- existe una propuesta tecnica clara para separar write-path y read-path visual
- se define un modelo inicial de snapshots de grafo o vistas precalculadas
- se documenta como regenerar vistas al cambiar nodos/aristas
- se explicita el modelo de consistencia eventual para visualizacion
- el roadmap deja claro que la primera fase puede vivir aun dentro del monolito

## 7. Architecture direction

### Phase 1

- read models dentro del stack actual
- snapshots persistidos en Postgres o almacenamiento compatible
- precomputo de:
  - centralidad
  - comunidades
  - subgrafos utiles
  - coordenadas/layout

### Phase 2

- jobs de preparacion de visualizacion
- regeneracion asincrona ante cambios
- estados visibles de "visualizacion actualizandose"

### Phase 3

- API de lectura dedicada para visualizacion
- payloads optimizados para cliente
- caching agresivo

### Phase 4

- cliente WebGL para grafos masivos
- mantenimiento del visualizador actual solo para subgrafos pequenos

### Phase 5

- evaluacion de graph storage especializado solo si Postgres + snapshots deja de
  ser suficiente

## 8. Technical impact

- `backend/graph_analytics.py`
- `backend/routers/graph_export.py`
- `backend/routers/relationships.py`
- `frontend/app/analytics/graph/page.tsx`
- `frontend/app/components/EntityGraph.tsx`
- posible nueva capa de jobs/read models

## 9. Risks

- riesgo: saltar demasiado pronto a microservicios
- impacto: complejidad operacional innecesaria
- mitigacion: fase 1 dentro del monolito con read models

- riesgo: introducir una graph DB externa demasiado pronto
- impacto: problemas de consistencia y operacion
- mitigacion: priorizar snapshots/read models sobre Postgres primero

## 10. Evidence

- `backend/routers/graph_export.py`
- `backend/graph_analytics.py`
- `frontend/app/components/EntityGraph.tsx`
- `frontend/app/analytics/graph/page.tsx`
- `C:/Users/Jose Paul/Desktop/visualization_architecture_evaluation.md`
