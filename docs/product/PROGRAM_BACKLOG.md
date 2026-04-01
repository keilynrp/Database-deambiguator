# Program Backlog

Backlog maestro de UKIP para conectar vision, producto y ejecucion tecnica.

## Estado del programa

Vision base:

- Plataforma agnostica de dominio para ingesta, harmonizacion, enriquecimiento, analitica, automatizacion y AI.

Foco comercial de corto plazo:

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

- cerrar `US-045` para terminar el baseline comercial multi-tenant con quotas por plan
- abrir `US-055` como evolucion del authority layer hacia `author resolution` explicable y comercializable
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
