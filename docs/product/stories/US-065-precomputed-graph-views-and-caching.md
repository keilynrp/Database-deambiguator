# US-065 - Precomputed Graph Views and Caching

## 1. Summary

Introducir vistas de grafo precalculadas y caching para servir consultas
visuales de alta frecuencia con baja latencia.

## 2. Objective

Reducir TTFB y carga de CPU sirviendo payloads visuales pregenerados y
cacheables.

## 3. Scope

- snapshots por dominio o subgrafo
- caching de view-models
- invalidacion y expiracion controladas

## 4. Evidence

- `backend/routers/graph_export.py`
- `docs/product/stories/US-062-graph-visualization-read-path-baseline.md`
