# EPIC-009 - Automation and Delivery

## 1. Summary

Dar identidad operativa al frente que automatiza el valor del sistema: reportes programados, imports programados, alertas, webhooks y workflows.

## 2. Problem

- UKIP no solo analiza; tambien automatiza y entrega valor
- estas capacidades suelen quedar repartidas entre integraciones y backend jobs
- faltaba una epic que las conecte como frente de producto

## 3. Objective

Tratar automation and delivery como una linea de producto propia y priorizable.

## 4. User value

Como operador o admin, quiero automatizar reportes, imports y notificaciones para que la plataforma trabaje por mi y entregue informacion a tiempo.

## 5. Scope

Incluye:

- scheduled reports
- scheduled imports
- alert channels
- webhooks
- workflows

Excluye:

- analitica interna no automatizada
- collaboration no orientada a entrega automatica

## 6. Success criteria

- existe una epic que agrupa automation and delivery
- backlog futuro de automatizacion queda trazable
- el valor del frente deja de verse como infraestructura invisible

## 7. Technical impact

- backend: `scheduled_reports.py`, `scheduled_imports.py`, `alert_channels.py`, `webhooks.py`, `workflows.py`
- frontend: `frontend/app/reports/`, `frontend/app/workflows/`, integraciones
- tests: suites relacionadas con sprints de automation

## 8. Risks

- riesgo: crecer automatizaciones sin priorizacion comun
- impacto: complejidad operativa y deuda de producto
- mitigacion: exigir que cada automatizacion nueva viva bajo esta epic

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-015 | Backfillear el frente de automation y delivery | Done |
| US-016 | Formalizar criterios operativos para scheduled reports, alerts y workflows | Planned |
| US-033 | Ciclo de vida de reportes programados | Planned |
| US-034 | Gestion de alert channels y webhooks | Planned |
| US-035 | Builder de workflows automatizados | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Incorporar automation al backlog vivo |

## 11. Evidence

- Codigo: `backend/routers/scheduled_reports.py`, `scheduled_imports.py`, `alert_channels.py`, `workflows.py`
- Docs: `README.md`, `CHANGELOG.md`
