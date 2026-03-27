# Product Documentation Hub

Este directorio contiene el sistema operativo de producto y delivery de UKIP.

## Documentos principales

- `docs/DOCUMENTATION_GOVERNANCE.md`: reglas de autoridad y uso de la documentacion.
- `PROGRAM_BACKLOG.md`: mapa maestro de epicas y lineas de producto.
- `TRACEABILITY_MATRIX.md`: relacion entre vision, epicas, historias, sprints y evidencia.
- `STORY_MAP.md`: vista funcional resumida del backlog refinado.
- `epics/`: epicas activas del programa.
- `stories/`: historias de usuario activas o refinadas.
- `sprints/`: artefactos de sprint.
- `templates/EPIC_TEMPLATE.md`: plantilla para epicas.
- `templates/STORY_TEMPLATE.md`: plantilla para historias de usuario.
- `templates/SPRINT_TEMPLATE.md`: plantilla para plan y cierre de sprint.
- `templates/RELEASE_TEMPLATE.md`: plantilla para releases.

## Como usar este directorio

1. Identifica la epic en `PROGRAM_BACKLOG.md`.
2. Crea o referencia historias usando el template.
3. Planifica el sprint usando el template de sprint.
4. Actualiza `TRACEABILITY_MATRIX.md` cuando cambie el estado.
5. Si hubo valor entregado al usuario, refleja el resultado en `CHANGELOG.md`.

## Backfill inicial ya creado

- epicas iniciales en `docs/product/epics/`
- historias iniciales en `docs/product/stories/`
- sprint activo base en `docs/product/sprints/SPRINT-102.md`
- siguiente sprint operativo en `docs/product/sprints/SPRINT-103.md`
- siguiente sprint de hardening en `docs/product/sprints/SPRINT-104.md`

## Regla de oro

Ninguna iniciativa nueva deberia entrar directamente al codigo sin pasar por:

- epic
- historia
- sprint
- trazabilidad

## Relacion con la capa historica

Si necesitas contexto de origen o decisiones previas:

- consulta `docs/reference/HISTORICAL_REFERENCE_INDEX.md`
- usa esos documentos como referencia, no como autoridad operativa primaria
