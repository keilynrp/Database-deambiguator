# AGENT_WORKING_PROTOCOL

Protocolo operativo para cualquier agente que trabaje en UKIP.

## 1. Objetivo

Garantizar que todos los agentes trabajen con:

- la misma fuente de verdad
- la misma disciplina documental
- la misma logica de priorizacion
- la misma forma de reportar avance y bloqueos

Este documento aplica a Claude Code, Codex y cualquier otro agente que opere dentro del repositorio.

## 2. Regla principal

No trabajar desde intuicion o contexto parcial.

Todo agente debe arrancar leyendo la documentacion operativa antes de proponer, editar o ejecutar trabajo.

## 3. Ruta obligatoria de lectura al iniciar

Leer en este orden:

1. `docs/README.md`
2. `docs/DOCUMENTATION_GOVERNANCE.md`
3. `docs/DELIVERY_OPERATING_SYSTEM.md`
4. `docs/product/README.md`
5. `docs/product/PROGRAM_BACKLOG.md`
6. `docs/product/STORY_MAP.md`
7. `docs/product/sprints/SPRINT-103.md`
8. `docs/product/sprints/SPRINT-103-AGENT-PLAN.md`
9. `docs/product/sprints/SPRINT-103-DAILY-LOG.md`

Si el trabajo requiere contexto historico o tecnico adicional:

10. `docs/reference/HISTORICAL_REFERENCE_INDEX.md`
11. `docs/TECHNICAL_ONBOARDING.md`
12. `docs/ARCHITECTURE.md`

## 4. Fuente de verdad

Si hay conflicto entre documentos:

1. manda la documentacion operativa
2. la documentacion historica solo contextualiza
3. si falta algo en la capa viva, el agente debe actualizarla

## 5. Como elegir trabajo

Un agente no debe elegir trabajo arbitrariamente.

Debe seguir este orden:

1. sprint activo
2. historia asignada o priorizada
3. dependencias definidas en el plan del sprint
4. criterio de prioridad P1/P2

Para `SPRINT-103`, el orden de referencia actual es:

1. `US-019`
2. `US-020`
3. `US-021`
4. `US-024`
5. `US-022`
6. `US-025`

## 6. Regla de alcance

Cada agente debe:

- trabajar una historia con foco claro
- evitar mezclar arreglos colaterales no relacionados
- no expandir el alcance sin registrarlo

Si descubre trabajo adicional:

- lo registra como riesgo, nota o propuesta
- no lo incorpora automaticamente si rompe el objetivo de la historia

## 7. Evidencia minima obligatoria

Toda historia trabajada debe dejar:

- resumen del cambio
- archivos tocados
- tests ejecutados o validacion manual
- riesgo residual
- evidencia funcional minima

Esto debe reflejarse en:

- la historia
- el daily log del sprint
- el sprint si cambia estado o alcance

## 8. Actualizacion diaria obligatoria

Todo agente que trabaje en el sprint debe actualizar:

- `docs/product/sprints/SPRINT-103-DAILY-LOG.md`

Usando como base:

- `docs/product/sprints/SPRINT-DAILY-UPDATE-TEMPLATE.md`

La actualizacion diaria debe incluir:

- historias activas
- avance
- bloqueos
- riesgos
- validacion
- coordinacion requerida
- decisiones o cambios de alcance

## 9. Cuando un agente debe escalar

Escalar cuando:

- una historia bloquea otra
- aparece una contradiccion entre docs vivas
- el cambio requiere ampliar alcance
- hay riesgo de romper una capacidad transversal
- la validacion del flujo completo falla

Escalar significa:

- registrar el bloqueo en el daily log
- dejar nota clara en la historia afectada
- proponer decision o recorte, no solo reportar el problema

## 10. Lo que un agente no debe hacer

No debe:

- usar documentos historicos como autoridad principal
- empezar una historia fuera del sprint sin justificarlo
- dejar cambios sin evidencia
- cerrar una historia sin actualizar el estado documental
- abrir estructura paralela de backlog o sprint
- hacer refactors amplios fuera del objetivo actual

## 11. Regla de cierre de historia

Una historia solo puede considerarse cerrada cuando:

- cumple criterios de aceptacion
- tiene evidencia tecnica y funcional
- tiene validacion suficiente
- su estado fue reflejado en el sprint
- el daily log deja rastro de su cierre

## 12. Regla de colaboracion entre agentes

Los agentes deben coordinarse por dependencias, no por preferencia.

Ejemplo en `SPRINT-103`:

- Ingestion habilita quality
- quality habilita authority/enrichment
- integration/QA valida el flujo de punta a punta

Si un agente aguas arriba no cerro una base minima, el agente aguas abajo no debe asumir comportamientos.

## 13. Arranque recomendado para Claude Code

Si Claude Code entra a trabajar ahora:

1. leer este protocolo
2. leer `docs/README.md`
3. leer `SPRINT-103.md`
4. leer `SPRINT-103-AGENT-PLAN.md`
5. tomar `US-019` si va a empezar por el frente de ingestion
6. registrar su primer bloque en `SPRINT-103-DAILY-LOG.md`

## 14. Resultado esperado

Si este protocolo se sigue bien:

- los agentes comparten contexto real
- el sprint avanza con menos friccion
- la documentacion queda viva
- el proyecto mantiene cohesion a largo plazo
