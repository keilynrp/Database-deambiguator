# US-071 - Catalog Portal by Ingestion

## Objetivo

Convertir una ingesta o snapshot importado en un portal de consulta mas amplio,
mas legible y mas compartible que el `Knowledge Explorer`, con una UX tipo
catalogo/OPAC orientada a descubrimiento.

## Problema

Hoy UKIP ofrece muy buena capacidad operativa para:

- importar
- enriquecer
- analizar
- generar brief

Pero la experiencia de consulta amplia sigue muy ligada al datatable interno.
Eso funciona para administracion y trabajo analitico, pero no es la mejor vista
para:

- bibliotecas
- investigadores no tecnicos
- stakeholders institucionales
- pilotos demostrativos con necesidad de navegacion tipo catalogo

## Resultado esperado

Despues de una ingesta, un administrador puede publicar una vista de catalogo con:

- URL estable por portal
- branding basico por tenant
- busqueda principal
- filtros/facets
- lista de resultados amigable
- ficha detallada por registro
- visibilidad privada, organizacional o publica

## Hipotesis de valor

Si UKIP puede presentar una ingesta como portal de consulta tipo OPAC, entonces:

- baja friccion para usuarios no tecnicos
- mejora la legibilidad del dataset ante stakeholders
- aumenta la capacidad de validacion externa de un piloto
- hace mas facil convertir una ingesta en producto demostrable

## Alcance MVP

### Incluye

- crear un portal a partir de una ingesta o snapshot
- landing del portal
- resultados con busqueda y facets
- ficha detallada por registro
- branding basico
- visibilidad `private` y `org`
- URL compartible interna

### No incluye en MVP

- SEO publico avanzado
- favoritos
- anotaciones publicas
- exportacion bibliografica avanzada
- recomendaciones semanticas
- personalizacion profunda de templates visuales

## Modelo funcional

### Nueva entidad propuesta

`CatalogPortal`

Campos sugeridos:

- `id`
- `org_id`
- `domain_id`
- `source_import_id`
- `source_snapshot_id`
- `title`
- `slug`
- `description`
- `visibility` (`private`, `org`, `public`)
- `is_default`
- `theme_config_json`
- `featured_facets_json`
- `default_sort`
- `created_by`
- `created_at`
- `updated_at`

### Relacion con los datos

Recomendacion:

- no colgar el portal directamente del estado vivo del dominio
- asociarlo a una `ingesta` o `snapshot`

Razon:

- la vista queda estable para demos y pilotos
- evita que el portal cambie de forma silenciosa despues de nuevas cargas
- facilita trazabilidad de "que dataset estaba viendo el stakeholder"

## Arquitectura funcional

### Backend

Nuevos modulos sugeridos:

- `backend/models.py`
  - agregar `CatalogPortal`
- `backend/routers/catalogs.py`
  - CRUD del portal
  - resultados
  - detalle
- `backend/services/catalog_service.py`
  - resolver snapshot
  - facets
  - search
  - sort
- `backend/tests/test_sprint109_catalog_portal.py`

### Frontend

Nuevas rutas sugeridas:

- `frontend/app/catalogs/page.tsx`
- `frontend/app/catalogs/[slug]/page.tsx`
- `frontend/app/catalogs/[slug]/search/page.tsx`
- `frontend/app/catalogs/[slug]/record/[id]/page.tsx`
- `frontend/app/settings/catalogs/page.tsx`

Componentes sugeridos:

- `CatalogHero`
- `CatalogSearchBar`
- `CatalogFacetPanel`
- `CatalogResultsList`
- `CatalogResultCard`
- `CatalogRecordView`
- `CatalogBrandingBanner`

## API sugerida

### Gestion

- `GET /catalogs`
- `POST /catalogs`
- `GET /catalogs/{id}`
- `PATCH /catalogs/{id}`
- `DELETE /catalogs/{id}`

### Consulta

- `GET /catalogs/{slug}/summary`
- `GET /catalogs/{slug}/results`
- `GET /catalogs/{slug}/facets`
- `GET /catalogs/{slug}/records/{entity_id}`

### Payload de resultados

Debe devolver:

- metadatos del portal
- resultados paginados
- facets disponibles
- orden actual
- total
- snapshot source

## UX direction

### Landing

- titulo
- descripcion
- resumen de volumen
- fecha de carga
- dominio
- CTA principal de busqueda

### Resultados

- input de busqueda prominente
- facets en sidebar
- lista rica, no tabla
- metadata breve y legible
- badges utiles solo si agregan valor

### Ficha

- bloque de identificacion arriba
- metadatos principales
- secciones expandibles
- enlaces externos
- DOI
- fuente
- metadatos extendidos

## Criterios de aceptacion

- un admin puede crear un portal desde una ingesta o snapshot
- el portal queda asociado a una organizacion y dominio
- la URL del portal es estable y compartible
- los resultados muestran solo registros de la fuente seleccionada
- la busqueda textual funciona
- los facets funcionan
- cada registro tiene ficha detallada legible
- la vista funciona en desktop y mobile
- la UX no depende del datatable interno

## Riesgos a cuidar

- colgar el portal del dataset vivo en vez de snapshot
- exponer demasiados metadatos en resultados
- repetir la UX del datatable en vez de una UX de descubrimiento
- mezclar catalogo publico con modulos internos sin aislamiento claro

## Secuencia de implementacion sugerida

### US-071A

- modelo `CatalogPortal`
- creacion desde ingesta/snapshot
- landing + resultados
- busqueda + facets
- visibilidad `private`

### US-071B

- ficha completa por registro
- branding basico
- visibilidad `org`
- URL compartible interna

### US-071C

- visibilidad `public`
- permalink de busqueda
- curacion basica de facets
- refinamiento visual OPAC-like

## Dependencias

- `EPIC-002 Ingestion and Mapping`
- `EPIC-006 Analytics and Decision Intelligence`
- `EPIC-008 Dashboards and Artifacts`
- `EPIC-010 Platform, Security and Collaboration`

## Decisiones recomendadas

- usar snapshot por defecto, no dominio vivo
- empezar con lista rica, no grid experimental
- limitar el MVP a una experiencia interna/tenant antes de abrir publico
- reutilizar facets y detalle donde convenga, pero con UI propia de catalogo

## Definicion de exito

La historia se considera exitosa cuando UKIP puede tomar una ingesta real y
publicarla como portal navegable, entendible y compartible para un stakeholder
no tecnico sin depender del `Knowledge Explorer`.
