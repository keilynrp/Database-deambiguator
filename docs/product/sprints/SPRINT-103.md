# SPRINT-103

## 1. Sprint goal

Fortalecer el flujo operativo que lleva datos crudos a entidades confiables mediante mejoras en preview de archivos, mapping, resolucion de duplicados, authority review y enrichment.

## 2. Theme

`Raw data -> trusted entity`

Este sprint prioriza el tramo mas critico del producto:

1. entender el archivo de entrada
2. mapearlo correctamente
3. detectar y resolver inconsistencias
4. confirmar autoridad externa
5. enriquecer entidades con confianza operativa

## 3. Scope

| ID | Tipo | Descripcion | Epic | Owner | Estado | Prioridad |
|---|---|---|---|---|---|---|
| US-019 | Story | Preview y validacion de archivos antes de importar | EPIC-002 | Team | Planned | P1 |
| US-020 | Story | Mapeo manual y asistido de columnas | EPIC-002 | Team | Planned | P1 |
| US-021 | Story | Revision de clusters y resolucion de duplicados | EPIC-003 | Team | Planned | P1 |
| US-022 | Story | Preview, confirmacion y trazabilidad de transformaciones | EPIC-003 | Team | Planned | P2 |
| US-024 | Story | Revision y confirmacion de candidatos de autoridad | EPIC-004 | Team | Planned | P1 |
| US-025 | Story | Orquestacion de enrichment individual y masivo | EPIC-004 | Team | Planned | P2 |

## 4. Sprint narrative

Si este sprint sale bien, UKIP mejora su tramo mas sensible y repetible:

- la entrada de datos se vuelve mas confiable
- la limpieza deja mas evidencia
- la reconciliacion externa gana control humano
- el enrichment queda mejor integrado al flujo real

## 5. Commitments

- mejorar la confianza en el flujo de importacion y preparacion de datos
- reducir ambiguedad entre datos importados, datos limpios y datos enriquecidos
- dejar evidencia funcional clara en cada paso del pipeline

## 6. Risks and dependencies

- dependencia: varias historias tocan backend y frontend a la vez
- riesgo: el sprint intente abarcar demasiados cambios de UX y logica de negocio simultaneamente
- mitigacion: cerrar primero `US-019`, `US-020`, `US-021` y `US-024`; mover `US-022` o `US-025` si hay presion de capacidad
- riesgo: integraciones externas afecten validacion de enrichment
- mitigacion: definir mocks, fallbacks o pruebas controladas

## 7. Suggested execution order

1. `US-019` Preview y validacion de archivos
2. `US-020` Mapping manual y asistido
3. `US-021` Revision de clusters y duplicados
4. `US-024` Authority review
5. `US-022` Transformations preview y trazabilidad
6. `US-025` Enrichment individual y masivo

## 8. Demo checklist

- [ ] upload preview muestra columnas, muestras y errores relevantes
- [ ] mapping es entendible y confirmable
- [ ] duplicados pueden revisarse y resolverse
- [ ] authority review muestra evidencia y permite confirmar/rechazar
- [ ] enrichment puede dispararse y su estado es visible
- [ ] docs y trazabilidad quedan actualizadas

## 9. Exit criteria

- al menos 4 historias cerradas, incluyendo 3 de prioridad P1
- el flujo `archivo -> entidad confiable` mejora en claridad operativa
- cada historia deja evidencia tecnica y funcional

## 10. Out of scope

- dashboard ejecutivo
- NLQ / OLAP
- agentic RAG
- workflows y automation
- administracion de usuarios y API keys

## 11. Follow-up recommendation

El sprint natural siguiente seria uno orientado a:

- `trusted insight`

con historias de analytics, RAG y dashboards, una vez reforzado el tramo de datos confiables.

## 12. Execution companion

Plan operativo por agente:

- `docs/product/sprints/SPRINT-103-AGENT-PLAN.md`
