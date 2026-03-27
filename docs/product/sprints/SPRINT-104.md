# SPRINT-104

## 1. Sprint goal

Elevar la credibilidad tecnica y la robustez operativa de UKIP atacando primero los gaps que mas comprometen reproducibilidad, despliegue y confianza externa.

## 2. Theme

`Credible runtime -> credible product`

Este sprint prioriza lo que mas duele entre el discurso actual y la realidad tecnica:

1. instalaciones reproducibles
2. path productivo claro sobre PostgreSQL
3. migraciones seguras
4. claims honestos y alineados
5. salud y visibilidad operativa minima

## 3. Scope

| ID | Tipo | Descripcion | Epic | Owner | Estado | Prioridad |
|---|---|---|---|---|---|---|
| US-039 | Story | Lockfile y reproducibilidad de dependencias | EPIC-011 | Team | Done | P0 |
| US-040 | Story | PostgreSQL-first runtime y despliegue | EPIC-011 | Team | Done | P0 |
| US-041 | Story | Ciclo seguro de migraciones y arranque | EPIC-011 | Team | Done | P1 |
| US-046 | Story | Alinear README y claims con la implementacion real | EPIC-013 | Team | Done | P0 |
| US-051 | Story | Health checks y structured logging | EPIC-015 | Team | Done | P1 |
| US-052 | Story | Baseline de Sentry y telemetria operativa | EPIC-015 | Team | Planned | P2 |
| US-047 | Story | Definir MVP comercial y onboarding real | EPIC-013 | Team | Planned | P2 |

## 4. Sprint narrative

Si este sprint sale bien, UKIP no solo sera mas solido tecnicamente: tambien sera mas creible frente a evaluadores, clientes potenciales y al propio equipo.

## 5. Commitments

- reducir el gap entre producto real y claims
- endurecer el path tecnico de despliegue y arranque
- mejorar señales basicas de operacion
- dejar base para tenant isolation y background jobs externos en el sprint siguiente

## 6. Risks and dependencies

- riesgo: tocar DB path, setup y migraciones a la vez
- mitigacion: cerrar primero `US-039`, `US-040` y `US-046`
- riesgo: abrir demasiados frentes sin cerrar uno bien
- mitigacion: `US-052` y `US-047` son expansion controlada
- dependencia: decisiones de PostgreSQL-first pueden afectar docs y scripts existentes

## 7. Suggested execution order

1. `US-046` Alinear README y claims
2. `US-039` Lockfile y reproducibilidad
3. `US-040` PostgreSQL-first runtime
4. `US-041` Ciclo seguro de migraciones
5. `US-051` Health checks y structured logging
6. `US-052` Sentry y telemetry baseline
7. `US-047` MVP comercial y onboarding real

## 8. Demo checklist

- [ ] existe camino reproducible de instalacion
- [ ] PostgreSQL aparece como path oficial de producto
- [ ] migraciones ya no corren al importar el modulo principal
- [ ] README distingue claramente realidad actual vs plan
- [ ] health/logging permiten diagnostico basico
- [ ] docs y backlog quedan alineados

## 9. Exit criteria

- al menos 4 historias cerradas, incluyendo 3 de prioridad P0/P1
- la credibilidad tecnica del proyecto mejora de forma visible
- existe mejor base para vender, operar y endurecer el producto

## 10. Out of scope

- tenant isolation completo
- externalizacion completa de background jobs
- refactor grande de frontend
- billing completo
- compliance enterprise avanzada

## 11. Follow-up recommendation

El sprint natural siguiente deberia orientarse a:

- `real tenant SaaS foundation`

con historias de `EPIC-012` y `US-042`.
