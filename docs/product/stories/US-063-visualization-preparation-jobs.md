# US-063 - Visualization Preparation Jobs

## 1. Summary

Agregar jobs asincronos para preparar vistas de grafo y artefactos visuales
pregenerados, evitando calculo pesado durante la consulta interactiva.

## 2. Objective

Regenerar snapshots de visualizacion cuando cambian nodos o relaciones, de
forma desacoplada del request interactivo.

## 3. Scope

- jobs o workers de preparacion
- triggers por cambios relevantes
- estado de regeneracion y freshness

## 4. Evidence

- `docs/product/stories/US-062-graph-visualization-read-path-baseline.md`
