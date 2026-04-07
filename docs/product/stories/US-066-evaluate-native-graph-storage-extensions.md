# US-066 - Evaluate Native Graph Storage Extensions

## 1. Summary

Evaluar de forma conservadora si Postgres con extensiones o almacenamiento de
grafo especializado aporta ventaja real frente al modelo de snapshots y
read-path pregenerado.

## 2. Objective

Tomar una decision informada sobre graph storage solo cuando el volumen y las
consultas lo justifiquen.

## 3. Scope

- evaluacion de extensiones nativas o graph DB externa
- analisis de consistencia, costo y operacion
- decision diferida hasta despues del read-path baseline

## 4. Evidence

- `docs/product/stories/US-062-graph-visualization-read-path-baseline.md`
