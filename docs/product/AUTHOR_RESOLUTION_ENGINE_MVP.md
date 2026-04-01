# Author Resolution Engine MVP

## 1. Summary

Blueprint para evolucionar el authority layer actual de UKIP hacia una capacidad comercializable de resolucion de autores, sin introducir una arquitectura paralela ni dependencias prematuras.

## 2. Strategic fit

Este enfoque refuerza el wedge comercial actual de `research intelligence` definido en `docs/product/COMMERCIAL_MVP.md`:

- portafolios de publicaciones
- autores e identidades investigativas
- afiliaciones y relaciones institucionales
- enrichment explicable y auditable

No redefine UKIP como producto nuevo. Lo convierte en una oferta mas fuerte y mas vendible alrededor de author intelligence.

## 3. Decision

La decision recomendada es:

- no construir un "decision engine" separado
- si construir un `Author Resolution Engine` sobre la capa existente de authority resolution
- limitar el MVP a `author disambiguation`
- mantener `LLM` como ruta terciaria, no como dependencia principal
- evitar por ahora `pgvector` como requisito, GraphDB operativo externo y orquestadores tipo n8n/Make en el core

## 4. Existing foundation in UKIP

La base tecnica actual ya cubre una parte importante del enfoque:

- `backend/authority/resolver.py`
  - resuelve candidatos multi-fuente
  - integra `Wikidata`, `VIAF`, `ORCID`, `DBpedia` y `OpenAlex`
  - deduplica candidatos entre fuentes
- `backend/authority/scoring.py`
  - ya existe scoring explicable por senales
  - hoy pondera identificadores, nombre y afiliacion
- `backend/routers/authority.py`
  - ya persiste authority records
  - ya expone confirmacion/rechazo y seguimiento del estado
- `backend/models.py`
  - `AuthorityRecord` ya soporta `confidence`, `resolution_status`, `score_breakdown`, `evidence` y `merged_sources`
- `backend/routers/graph_export.py`
  - ya existe salida `GraphML`, `Cytoscape JSON` y `JSON-LD`
- `backend/llm_agent.py`
  - ya existe una base de resolucion asistida por LLM, aunque hoy es mas simple y lexical

## 5. Product framing

El MVP debe presentarse como:

`Resolucion adaptativa de autores para portafolios de investigacion`

Valor comercial inicial:

- consolidar autores duplicados o ambiguos
- vincular perfiles externos relevantes
- justificar por que una resolucion fue aceptada o marcada como ambigua
- dejar casos `NIL` o ambiguos en cola de revision

Mercados y nichos mas naturales:

- universidades y oficinas de investigacion
- bibliometria y scientometrics
- publishers y agregadores academicos
- scouting cientifico y consultoria de I+D

## 6. Non-goals for the MVP

El MVP no debe incluir:

- resolucion universal de cualquier tipo de entidad
- migracion a `pgvector`
- dependencia operativa de GraphDB externo
- flujos RDF-first como requisito runtime
- automatizacion externa con n8n/Make en el camino critico
- agentes genericos como capa principal de reconciliacion

## 7. Target architecture

### 7.1 Runtime flow

1. Ingesta de metadatos bibliograficos.
2. Normalizacion de nombre, afiliacion y contexto.
3. Generacion de candidatos multi-fuente.
4. Calculo de `complexity_score`.
5. Ruteo de decision:
   - `fast_path`
   - `hybrid_path`
   - `llm_path`
6. Persistencia de decision, evidencia y trazabilidad.
7. Derivacion a `review queue` o `NIL`.
8. Export o explotacion analitica posterior.

### 7.2 Decision routes

`fast_path`

- identificador fuerte disponible
- coincidencia clara por ORCID/OpenAlex
- score alto y gap amplio frente al segundo candidato
- no usa LLM

`hybrid_path`

- usa scoring actual mas senales contextuales
- aplica cuando no hay identificador concluyente
- debe seguir siendo deterministicamente explicable

`llm_path`

- solo para casos ambiguos o con evidencia incompleta
- nunca reemplaza la persistencia de evidencia
- debe producir `rationale` acotado y reusable

## 8. Data model evolution

Se recomienda extender `AuthorityRecord` y no crear una tabla paralela desconectada.

Campos sugeridos para el MVP:

- `resolution_route`
  - `fast_path`, `hybrid_path`, `llm_path`, `manual_review`
- `complexity_score`
  - decimal corto entre `0.0` y `1.0`
- `review_required`
  - boolean
- `nil_reason`
  - texto corto o enum
- `decision_version`
  - version de la heuristica/pipeline
- `decision_latency_ms`
  - opcional para analitica operativa

Campos que ya pueden reutilizarse:

- `confidence`
- `resolution_status`
- `score_breakdown`
- `evidence`
- `merged_sources`

## 9. API surface recommendation

No conviene reemplazar endpoints existentes. Conviene agregar una capa explicita para autores.

### 9.1 Suggested endpoints

- `POST /authority/authors/resolve`
  - resuelve un autor individual con contexto opcional
- `POST /authority/authors/batch-resolve`
  - resuelve una lista de autores de un dataset o trabajo
- `GET /authority/authors/review-queue`
  - lista casos ambiguos o `NIL`
- `POST /authority/authors/{record_id}/confirm`
  - confirma resolucion
- `POST /authority/authors/{record_id}/reject`
  - rechaza resolucion y preserva evidencia

### 9.2 Resolve response shape

Respuesta minima esperada:

- `record_id`
- `resolution_status`
- `resolution_route`
- `complexity_score`
- `confidence`
- `winning_candidate`
- `runner_up_candidate`
- `score_breakdown`
- `evidence`
- `review_required`
- `nil_reason`

## 10. UI flow recommendation

Frontend recomendado para el MVP:

1. subir o abrir dataset bibliografico
2. detectar autores ambiguos
3. mostrar lista de casos con route/confidence
4. abrir comparador de candidatos
5. confirmar, rechazar o marcar `NIL`
6. ver resumen final del portafolio resuelto

Pantallas sugeridas:

- `Author Resolution Queue`
- `Author Candidate Comparison`
- `Author Resolution Summary`

La UX debe priorizar evidencia y comparabilidad, no chat libre.

## 11. Scoring evolution roadmap

Senales del MVP:

- identificadores
- similitud de nombre
- afiliacion

Senales para la siguiente fase:

- coautoria
- venue o journal
- tiempo o ventana de publicacion
- topicos derivados del corpus
- consistencia con el grafo local ya construido

Importante:

- las nuevas senales deben entrar como breakdown explicable
- no deben reemplazar el score actual con una caja negra

## 12. NIL and manual review

`NIL` debe tratarse como resultado valido, no como error.

Casos `NIL`:

- no hay evidencia suficiente
- el mejor candidato no supera umbral minimo
- hay conflicto fuerte entre fuentes

Todos esos casos deben:

- quedar persistidos
- mantener evidencia
- poder revisarse manualmente
- alimentar futuras mejoras de reglas

## 13. Metrics for success

Metricas del MVP:

- `% autores resueltos en fast_path`
- `% autores resueltos en hybrid_path`
- `% casos enviados a llm_path`
- `% casos `NIL``
- precision de resolucion validada por muestra
- tiempo promedio de resolucion por autor
- tiempo promedio de revision manual
- gap promedio entre primer y segundo candidato

Metricas comerciales:

- tiempo ahorrado en consolidacion de portafolios
- reduccion de duplicados en autores
- porcentaje de perfiles enriquecidos con identificadores externos

## 14. Technical risks and mitigations

Riesgo: sobre-ingenieria temprana con infraestructura nueva.

- mitigacion: reutilizar `resolver.py`, `scoring.py` y `AuthorityRecord`

Riesgo: dependencia excesiva en LLM.

- mitigacion: LLM solo en `llm_path`, con evidencia obligatoria y opt-in por complejidad

Riesgo: drift con la narrativa comercial actual.

- mitigacion: mantener el framing en `research intelligence` y autores

Riesgo: ambiguedad de ownership entre authority, disambiguation y graph.

- mitigacion: ubicar este trabajo primariamente bajo `EPIC-004`

## 15. Recommended implementation phases

### Phase 1 - Author-only adaptive resolution MVP

- author-only
- `complexity_score`
- `resolution_route`
- `fast_path` y `hybrid_path`
- `llm_path` opcional y acotado
- `NIL` y `review_required`

### Phase 2 - Context-rich author scoring

- coautoria
- historial de afiliacion
- ventanas temporales
- venue/journal

### Phase 3 - Review operations and portfolio UX

- review queue madura
- comparador de candidatos
- resumen de portafolio resuelto
- metricas de calidad

### Phase 4 - Enterprise scaling options

- evaluar `pgvector` solo si el retrieval author-context lo justifica
- evaluar graph store externo solo si el volumen o los casos enterprise lo exigen
- nunca adoptar infraestructura adicional sin demanda comprobada

## 16. Sequencing recommendation

Orden recomendado:

1. cerrar `US-045` y el baseline multi-tenant/quotas
2. abrir historia de `Author Resolution Engine MVP`
3. implementar backend author-only
4. agregar review UI
5. medir precision y cobertura antes de ampliar infraestructura

## 17. Conclusion

El enfoque del PRD es viable y estrategicamente valioso para UKIP, siempre que se implemente como una extension del authority layer actual y no como una plataforma nueva.

La apuesta correcta es:

- mas capacidad de resolucion explicable
- mas foco en autores y portafolios
- menos infraestructura prematura
- mas trazabilidad comercial y operativa
