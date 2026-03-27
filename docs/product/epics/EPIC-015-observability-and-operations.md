# EPIC-015 - Observability and Operations

## 1. Summary

Construir una base minima de salud operativa, telemetry y logging para detectar fallos y operar UKIP con mayor confianza.

## 2. Problem

- la observabilidad es parcial u opt-in
- faltan health checks claros, logging estructurado y señal operativa consistente
- sin esto, hardening y despliegue productivo quedan ciegos

## 3. Objective

Dotar al sistema de visibilidad operativa basica y reusable.

## 4. User value

Como equipo tecnico, quiero saber cuando UKIP esta sano o fallando para operar y escalar el producto con menos incertidumbre.

## 5. Scope

Incluye:

- health checks
- structured logging
- Sentry/telemetry baseline
- checks o alertas operativas iniciales

Excluye:

- plataforma completa de observabilidad enterprise
- monitoreo avanzado multi-region

## 6. Success criteria

- existe un health path claro y util
- los logs son mas estructurados
- errores y trazas criticas tienen mejor visibilidad

## 7. Technical impact

- `backend/main.py`
- middleware y config de logging
- telemetry / sentry setup
- docs operativas

## 8. Risks

- riesgo: introducir instrumentacion demasiado compleja muy pronto
- impacto: ruido, costo y friccion
- mitigacion: empezar por baseline minimalista y util

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-051 | Health checks y structured logging | Planned |
| US-052 | Baseline de Sentry y telemetria operativa | Planned |
| US-053 | Verificaciones operativas y alertas base | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-104 | Cerrar la visibilidad operativa minima necesaria |

## 11. Evidence

- Valoracion tecnica senior 2026-03-24
- runtime y config actuales
