# SPRINT-103 Agent Plan

Plan operativo por agente para ejecutar `SPRINT-103` de forma coordinada.

## 1. Objetivo operativo

Ejecutar el flujo `Raw data -> trusted entity` con trabajo paralelo controlado, reduciendo choques entre agentes y dejando evidencia tecnica y funcional por historia.

## 2. Principios de coordinacion

- priorizar flujo vertical antes que optimizaciones laterales
- cerrar dependencias P1 antes de abrir historias P2
- cada agente deja evidencia en historia, sprint y trazabilidad
- si una historia bloquea a otra, el agente aguas abajo no improvisa alcance

## 3. Perfiles de agente

### Agent A - Ingestion Lead

Responsable del tramo de entrada de datos.

Historias:

- `US-019` Preview y validacion de archivos antes de importar
- `US-020` Mapeo manual y asistido de columnas

Objetivo:

Dejar confiable la fase inicial de importacion para que el resto del pipeline opere sobre datos bien entendidos.

Archivos o zonas probables:

- `backend/routers/ingest.py`
- `backend/routers/column_maps.py`
- `frontend/app/import/`
- `frontend/app/import-export/`

Entregables minimos:

- criterios de error y validacion visibles
- preview util antes del import
- mapping confirmable y entendible
- tests o evidencia de validacion manual

Bloquea a:

- `US-021`
- parcialmente `US-024`
- parcialmente `US-025`

### Agent B - Quality Lead

Responsable del tramo de limpieza y consolidacion operativa.

Historias:

- `US-021` Revision de clusters y resolucion de duplicados
- `US-022` Preview, confirmacion y trazabilidad de transformaciones

Objetivo:

Dejar el dataset en mejor estado antes de pasar a reconciliacion externa y enrichment.

Archivos o zonas probables:

- `backend/routers/disambiguation.py`
- `backend/routers/transformations.py`
- `frontend/app/disambiguation/`
- `frontend/app/transformations/`

Entregables minimos:

- flujo de revision comprensible
- decisiones de merge o dismiss persistidas
- preview antes/despues en transformaciones
- evidencia clara de trazabilidad o historial

Dependencias:

- `US-021` depende funcionalmente de buena salida de `US-019` y `US-020`
- `US-022` puede avanzar en paralelo si el alcance no depende de cambios de ingestion

### Agent C - Authority and Enrichment Lead

Responsable del tramo de reconciliacion externa y ampliacion de datos.

Historias:

- `US-024` Revision y confirmacion de candidatos de autoridad
- `US-025` Orquestacion de enrichment individual y masivo

Objetivo:

Hacer que el paso desde entidad limpia a entidad confiable y enriquecida sea visible y operable.

Archivos o zonas probables:

- `backend/routers/authority.py`
- `backend/enrichment_worker.py`
- `backend/routers/scrapers.py`
- `frontend/app/authority/`
- tabs de enrichment en entidad

Entregables minimos:

- authority review con evidencia util
- confirmacion/rechazo persistido
- enrichment disparable con estado visible
- errores y fallbacks comprensibles

Dependencias:

- `US-024` se beneficia de mejor salida de `US-021`
- `US-025` depende de definiciones de entidad y estados consistentes de pasos previos

### Agent D - Integration and QA Lead

Responsable de cohesion transversal, pruebas y evidencia de sprint.

Historias:

- soporte transversal a todas las historias del sprint

Objetivo:

Evitar que el sprint se cierre con piezas aisladas sin validar el flujo completo.

Zonas probables:

- `backend/tests/`
- `frontend/__tests__/`
- `frontend/e2e/`
- docs de sprint e historias

Entregables minimos:

- checklist de flujo completo
- pruebas o validacion manual documentada
- registro de riesgos encontrados
- actualizacion de historias con evidencia

## 4. Secuencia de ejecucion recomendada

### Fase 1 - Base del flujo

- Agent A ejecuta `US-019`
- Agent A prepara `US-020`
- Agent D define checklist de validacion para ingestion

### Fase 2 - Consolidacion

- Agent A cierra `US-020`
- Agent B arranca `US-021`
- Agent B prepara `US-022` si no compite con `US-021`

### Fase 3 - Confianza externa

- Agent C arranca `US-024`
- Agent C prepara `US-025`
- Agent D valida flujo `import -> quality -> authority`

### Fase 4 - Cierre controlado

- cerrar `US-022` si hay capacidad
- cerrar `US-025` si el flujo base ya esta estable
- Agent D actualiza evidencia, estado y hallazgos del sprint

## 5. Matriz de dependencias

| Historia | Depende de | Puede correr en paralelo con |
|---|---|---|
| `US-019` | - | todas |
| `US-020` | `US-019` parcialmente | `US-022` |
| `US-021` | `US-019`, `US-020` | `US-024` parcialmente |
| `US-022` | definicion de alcance de quality | `US-020`, `US-024` |
| `US-024` | salida razonable de entidades limpias | `US-021`, `US-022` |
| `US-025` | estados consistentes de entidades y enrichment | `US-022` parcialmente |

## 6. Regla de prioridad

Orden de cierre ideal:

1. `US-019`
2. `US-020`
3. `US-021`
4. `US-024`
5. `US-022`
6. `US-025`

Si el sprint se aprieta, se sacrifica primero:

1. `US-025`
2. `US-022`

No se sacrifica:

- `US-019`
- `US-020`
- `US-021`
- `US-024`

## 7. Evidencia esperada por agente

Cada agente debe dejar en sus historias:

- resumen de cambio
- archivos afectados
- tests ejecutados o validacion manual
- riesgo residual
- evidencia funcional minima

Cada agente debe dejar en el sprint:

- estado final de sus historias
- blockers encontrados
- recomendacion para siguiente sprint si aplica

## 8. Checklist de coordinacion diaria

- confirmar historias en curso y bloqueos
- no abrir historia nueva si una P1 critica sigue bloqueada
- registrar decisiones de recorte de alcance
- actualizar evidencia al cierre del dia o del bloque de trabajo

Plantillas y registro:

- `docs/product/sprints/SPRINT-DAILY-UPDATE-TEMPLATE.md`
- `docs/product/sprints/SPRINT-103-DAILY-LOG.md`

## 9. Criterio de exito del plan

El plan funciona si:

- los agentes pueden trabajar en paralelo sin pisarse
- el flujo de punta a punta mejora y no solo modulos aislados
- las historias dejan evidencia reutilizable para release y changelog
