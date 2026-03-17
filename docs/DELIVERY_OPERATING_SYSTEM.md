# Delivery Operating System

Sistema documental para mantener coherencia entre vision, roadmap, epicas, historias, sprints y cambios tecnicos.

## 1. Problema que resuelve

Hoy el proyecto tiene buena documentacion estrategica y tecnica, pero la trazabilidad entre:

- vision
- roadmap
- epicas
- historias de usuario
- sprints
- releases
- cambios en codigo

no esta normalizada en un mismo sistema operativo de producto.

Este documento define esa columna vertebral.

## 2. Principio rector

Cada cambio importante debe poder responder cinco preguntas:

1. Que problema de negocio o usuario resuelve.
2. En que epic cae.
3. Que historias de usuario lo componen.
4. En que sprint se implemento o se implementara.
5. Que artefactos tecnicos y funcionales quedaron como evidencia.

Si un cambio no puede trazarse de esa forma, el proyecto pierde hilo conductor.

## 3. Artefactos canonicos

La fuente de verdad queda organizada asi:

```text
docs/
  README.md
  DOCUMENTATION_GOVERNANCE.md
  DELIVERY_OPERATING_SYSTEM.md
  operating/
    README.md
  reference/
    README.md
    HISTORICAL_REFERENCE_INDEX.md
  product/
    README.md
    PROGRAM_BACKLOG.md
    TRACEABILITY_MATRIX.md
    templates/
      EPIC_TEMPLATE.md
      STORY_TEMPLATE.md
      SPRINT_TEMPLATE.md
      RELEASE_TEMPLATE.md
```

## 4. Jerarquia de documentos

Usa esta jerarquia de arriba hacia abajo:

1. Gobernanza documental
   - `docs/DOCUMENTATION_GOVERNANCE.md`
2. Sistema operativo de delivery
   - `docs/DELIVERY_OPERATING_SYSTEM.md`
3. Programa y backlog maestro
   - `docs/product/PROGRAM_BACKLOG.md`
4. Trazabilidad viva
   - `docs/product/TRACEABILITY_MATRIX.md`
5. Ejecucion
   - epicas, historias, sprints y releases usando templates
6. Evidencia tecnica
   - PRs, commits, changelog, tests, docs especificas
7. Referencia historica
   - `docs/reference/HISTORICAL_REFERENCE_INDEX.md`
   - documentos historicos y de contexto

## 5. Convenciones de identificadores

Usa IDs estables y legibles:

- Epic: `EPIC-001`
- Historia: `US-001`
- Sprint: `SPRINT-102`
- Release: `REL-2026.03`
- Decision tecnica: `ADR-001`

Reglas:

- Los IDs nunca se reciclan.
- Una historia pertenece a una sola epic.
- Un sprint puede contener historias de varias epicas.
- Un release puede agrupar uno o varios sprints.

## 6. Flujo de trabajo recomendado

### Antes de construir

1. Confirmar que el problema exista en `PROGRAM_BACKLOG.md`.
2. Si no existe, crear o ajustar una epic.
3. Descomponer en historias pequenas y verificables.
4. Definir criterios de aceptacion.
5. Asignar la historia a un sprint.

### Durante el sprint

1. Cada historia debe tener estado.
2. Cada historia debe enlazar archivos, endpoints o modulos afectados.
3. Si cambia arquitectura o contrato, anotar decision o riesgo.

### Al cerrar el sprint

1. Marcar historias cerradas.
2. Actualizar trazabilidad.
3. Registrar salida visible en `CHANGELOG.md`.
4. Si aplica, crear release note.

## 7. Definicion de Done

Una historia esta realmente terminada cuando:

- la necesidad esta clara
- tiene criterios de aceptacion
- hay evidencia tecnica
- la UI o API fue validada
- hay tests o una justificacion de por que no aplica
- la trazabilidad se actualizo

## 8. Relacion con los documentos ya existentes

Los documentos actuales no se reemplazan; se conectan:

- `README.md`: vision comercial y mapa de capacidades
- `docs/EVOLUTION_STRATEGY.md`: direccion estrategica historica
- `docs/ARCHITECTURE.md`: principios y decisiones de software de referencia
- `CHANGELOG.md`: salida historica implementada
- `docs/TECHNICAL_ONBOARDING.md`: orientacion para tocar codigo

Este sistema agrega la capa que faltaba entre estrategia y ejecucion.

## 9. Regla anti-caos

No abras documentos nuevos si uno de estos ya resuelve el caso.

Primero clasifica el cambio:

- es gobernanza documental -> `DOCUMENTATION_GOVERNANCE.md`
- es estrategia -> `EVOLUTION_STRATEGY.md`
- es arquitectura -> `ARCHITECTURE.md`
- es roadmap/backlog -> `PROGRAM_BACKLOG.md`
- es trazabilidad -> `TRACEABILITY_MATRIX.md`
- es ejecucion del sprint -> usa template de sprint
- es salida publicada -> `CHANGELOG.md`

## 10. Cadencia minima de mantenimiento

- Cada nueva epic: actualizar `PROGRAM_BACKLOG.md`
- Cada inicio o cierre de sprint: actualizar artefacto del sprint y `TRACEABILITY_MATRIX.md`
- Cada entrega visible: actualizar `CHANGELOG.md`
- Cada cambio de direccion: actualizar `EVOLUTION_STRATEGY.md`
