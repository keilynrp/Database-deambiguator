# US-064 - Massive Graph WebGL Client

## 1. Summary

Preparar un cliente de visualizacion de grafos masivos basado en WebGL para
explorar redes I+D de gran tamano sin depender del visualizador SVG actual.

## 2. Objective

Sustituir o complementar la visualizacion radial SVG con una experiencia apta
para miles o cientos de miles de nodos.

## 3. Scope

- evaluacion e integracion de Sigma.js o alternativa equivalente
- cliente optimizado para payloads precalculados
- interaccion progresiva con metadata bajo demanda

## 4. Evidence

- `frontend/app/components/EntityGraph.tsx`
- `docs/product/stories/US-062-graph-visualization-read-path-baseline.md`
