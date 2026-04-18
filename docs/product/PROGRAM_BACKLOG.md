# Program Backlog

Backlog maestro de UKIP para conectar vision, producto y ejecucion tecnica.

## Estado del programa

Vision base:

- Plataforma agnostica de dominio para ingesta, harmonizacion, enriquecimiento, analitica, automatizacion y AI.

Foco comercial de corto plazo:

- convertir datasets importados en salidas ejecutivas y demostrables con menor
  friccion

- wedge inicial en `research intelligence` para portafolios de publicaciones, autores y afiliaciones.

Fuentes estrategicas relacionadas:

- `docs/EVOLUTION_STRATEGY.md`
- `docs/ARCHITECTURE.md`
- `docs/UKIP_ENTERPRISE_ROADMAP.md`

## Epicas activas

| ID | Epic | Objetivo | Estado | Modulos clave |
|---|---|---|---|---|
| EPIC-001 | Universal Data Engine | Consolidar el modelo de entidad universal y su operacion multi-dominio | In progress | `backend/models.py`, `backend/domains/`, `backend/routers/entities.py` |
| EPIC-002 | Ingestion and Mapping | Hacer robusta la entrada de datos multi-formato y el mapeo asistido | In progress | `backend/routers/ingest.py`, `frontend/app/import/`, `frontend/app/import-export/` |
| EPIC-003 | Data Quality and Harmonization | Mejorar normalizacion, clustering, transformaciones y calidad compuesta | In progress | `backend/routers/harmonization.py`, `disambiguation.py`, `transformations.py`, `quality.py` |
| EPIC-004 | Authority and Enrichment | Resolver entidades contra bases externas y enriquecer conocimiento | In progress | `backend/routers/authority.py`, `scrapers.py`, `enrichment_worker.py` |
| EPIC-005 | Knowledge Graph | Construir y explotar relaciones entre entidades | In progress | `backend/routers/relationships.py`, `graph_export.py`, `graph_analytics.py` |
| EPIC-006 | Analytics and Decision Intelligence | Convertir datos armonizados en insights, OLAP y simulaciones | In progress | `backend/routers/analytics.py`, `nlq.py`, `olap.py` |
| EPIC-007 | AI, RAG and Context Engineering | Habilitar busqueda semantica y agentes con herramientas | In progress | `backend/routers/ai_rag.py`, `context.py`, `tool_registry.py`, `llm_agent.py` |
| EPIC-008 | Dashboards and Artifacts | Permitir visualizacion ejecutiva y artefactos exportables | In progress | `backend/routers/dashboards.py`, `artifacts.py`, `reports.py`, `frontend/app/dashboards/` |
| EPIC-009 | Automation and Delivery | Automatizar imports, reportes, alertas y workflows | In progress | `scheduled_imports.py`, `scheduled_reports.py`, `alert_channels.py`, `workflows.py` |
| EPIC-010 | Platform, Security and Collaboration | Fortalecer auth, RBAC, auditoria, organizaciones y colaboracion | In progress | `auth_users.py`, `api_keys.py`, `audit_log.py`, `organizations.py`, `annotations.py`, `notifications.py` |
| EPIC-011 | Hardening and Runtime Reliability | Endurecer runtime, dependencias, DB path y lifecycle tecnico base | Planned | `requirements.txt`, `backend/database.py`, `backend/main.py`, Docker/config de despliegue |
| EPIC-012 | Tenant Isolation and Access Control | Llevar multi-tenancy y control de acceso a aislamiento real de datos | In progress | modelos con `org_id`, filtros por tenant, RBAC/ABAC, quotas |
| EPIC-013 | Commercial Readiness and Credibility | Alinear claims, onboarding y readiness comercial con la realidad del producto | Done | `README.md`, docs comerciales, onboarding, compliance baseline |
| EPIC-014 | Frontend Decomposition and Maintainability | Reducir componentes monoliticos y mejorar capacidad de evolucion del frontend | Planned | `EntityTable.tsx`, `Sidebar.tsx`, `RAGChatInterface.tsx`, `DisambiguationTool.tsx` |
| EPIC-015 | Observability and Operations | Construir salud operativa, logging y telemetria minima de producto serio | Done | health endpoints, logging, Sentry/telemetry, checks operativos |

## Prioridades recomendadas de corto plazo

- usar `US-058` como guardarrail para calibrar cualquier cambio posterior en heuristicas o rutas LLM
- extender el fallback jerarquico de `US-057` solo donde exista jerarquia de conceptos realmente util
- cerrar historias pendientes de `EPIC-004` que eleven calidad de authority review y enrichment fallback
- posponer infraestructura nueva de vector/graph store hasta validar demanda y volumen

## Epicas futuras sugeridas

| ID | Epic | Objetivo | Estado |
|---|---|---|---|
| EPIC-016 | Release Governance | Formalizar releases, versionado, notas y criterios de salida | Proposed |
| EPIC-017 | Product Analytics | Medir adopcion, uso de features y valor entregado por modulo | Proposed |

## Criterios para abrir una nueva epic

Abre una nueva epic solo si:

- agrega una nueva capacidad de producto
- afecta multiples modulos o sprints
- necesita identidad propia de roadmap

No abras epic nueva si el trabajo cabe como historia o sub-historia de una epic existente.
## Prioridades siguientes recomendadas

1. validar `US-060` y `US-061` con un piloto real de import -> dashboard -> brief
2. `US-067` - Institutional Benchmark Profiles
3. `US-068` - Research Network Community Detection
4. `US-069` - Emerging Topic Trend Signals
5. seguir endureciendo operacion solo en respuesta a hallazgos reales del despliegue

## Hallazgo piloto reciente

- piloto real UDG ejecutado y documentado en
  `docs/product/PILOT_UDG_EXECUTIVE_DASHBOARD_REVIEW_2026-04-10.md`
- conclusion: `US-060` y `US-061` ya quedaron validadas como flujo util de
  demo interna seria
- lectura mas reciente del piloto:
  - `470/1000` entidades enriquecidas (`47%`)
  - `54%` de calidad promedio
  - benchmark SNI baseline se mantiene en `33.3%`, frenado aun por cobertura y
    calidad
- siguiente prioridad recomendada: siguiente corte de `US-067` para benchmark
  configurable por tenant/institucion

## Frente comercial por stakeholder

- base estrategica inicial documentada en
  `docs/product/STAKEHOLDER_GROWTH_AND_SALES_STRATEGY.md`
- stakeholders prioritarios definidos:
  - liderazgo institucional / rectoria
  - oficina de investigacion
  - biblioteca / metadatos
  - innovacion / transferencia
- conclusion:
  - el siguiente trabajo de crecimiento ya no depende tanto de nuevas features base
  - depende de empaquetar mejor el valor actual en motion comercial, oferta de piloto
    y narrativa por audiencia

## Hallazgo modulo scientific import

- smoke test funcional ejecutado sobre `Scientific Import`
- validado con casos reales en:
  - `CrossRef` por busqueda libre
  - `CrossRef` por DOI batch
  - `PubMed` por busqueda libre
- flujo validado:
  - preview
  - import
  - persistencia en `RawEntity`
  - apertura del registro desde el explorer
- integracion endurecida despues del smoke test:
  - dedupe por DOI ahora scoped por tenant
  - preview DOI usa la misma ruta real de resolucion que el import
  - CTA final del frontend vuelve al explorer correcto
- conclusion:
  - el bloque de adapters + factory + router + frontend scientific import queda
    funcionalmente validado para cierre de integracion base
  - siguientes mejoras ya no son bloqueo base, sino expansiones:
    - prueba complementaria con `arXiv`
    - i18n/copy de la pagina
    - decidir si el import cientifico debe disparar enrichment automaticamente

## Arquitectura futura de visualizacion

- `US-062` - Graph Visualization Read-Path Baseline
- `US-063` - Visualization Preparation Jobs
- `US-064` - Massive Graph WebGL Client
- `US-065` - Precomputed Graph Views and Caching
- `US-066` - Evaluate Native Graph Storage Extensions

## Proximo tramo I+D recomendado

- `US-067` primero para traducir el producto a marcos de evaluacion
  institucional con valor operativo real
- `US-068` despues para fortalecer analitica de redes de colaboracion y
  preparar visualizacion mas avanzada
- `US-069` al final como capa experimental de senales emergentes, solo cuando
  el volumen temporal y la cobertura de datos lo justifiquen
