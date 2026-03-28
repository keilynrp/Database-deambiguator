# Tenant Scoping Model

Modelo objetivo de tenant isolation para `EPIC-012` y `US-043`.

## 1. Principio base

El anchor del tenant en UKIP es `Organization`.

Regla objetivo:

- los datos de negocio compartidos deben pertenecer a exactamente una organizacion
- `User` sigue siendo identidad global de control plane
- el contexto activo de trabajo sigue partiendo de `User.org_id`

## 2. Estado actual

Hoy UKIP tiene organizaciones y membresias, pero gran parte de los recursos de negocio siguen siendo globales o solo user-scoped.

Eso significa que el multi-tenancy existe en la UX y en membresias, pero no todavia como aislamiento real de datos.

## 3. Olas incrementales de migracion

### Wave 1 - Core shared data plane

Primero migrar:

- `raw_entities`
- `entity_relationships`
- `authority_records`
- `normalization_rules`
- `harmonization_logs`

Razon:

- son la base del dataset tenant-owned y condicionan casi todos los flujos posteriores

### Wave 2 - Automation and collaboration state

Luego migrar:

- `annotations`
- `workflows`
- `scheduled_reports`
- `scheduled_imports`
- `alert_channels`

Razon:

- operan sobre datos tenant-owned y no deben ejecutarse ni notificarse cruzando organizaciones

### Wave 3 - User-owned tenant surfaces

Luego migrar:

- `user_dashboards`
- `analysis_contexts`
- `artifact_templates`
- `embed_widgets`

Razon:

- siguen teniendo ownership de usuario, pero dependen de datos compartidos del tenant

### Wave 4 - Control plane and exceptions

Revisar finalmente:

- `users`
- singletons globales como branding y notification settings

Razon:

- no todo debe volverse tenant-scoped inmediatamente; aqui se deciden excepciones y semantics de control plane

## 4. Recursos que deben seguir siendo excepciones temporales

Por ahora pueden seguir como control plane:

- `User`
- `Organization`
- `OrganizationMember`
- `BrandingSettings`
- `NotificationSettings`

Eso evita mezclar la migracion del data plane con una reescritura completa del admin plane.

## 5. Criterio para la siguiente historia

`US-044` debe arrancar solo despues de esta baseline y aplicar enforcement reusable sobre:

- entities
- authority
- workflows
- dashboards/reporting

## 6. Artefactos relacionados

- `backend/tenant_scoping.py`
- `GET /ops/tenant-model`
- `docs/product/epics/EPIC-012-tenant-isolation-and-access-control.md`
- `docs/product/stories/US-043-tenant-scoping-data-model.md`
