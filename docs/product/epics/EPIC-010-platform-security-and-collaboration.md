# EPIC-010 - Platform, Security and Collaboration

## 1. Summary

Dar coherencia a las capacidades transversales que hacen que UKIP opere como plataforma robusta: autenticacion, RBAC, API keys, auditoria, organizaciones, comentarios, notificaciones y gobernanza operativa.

## 2. Problem

- estas capacidades son transversales y facilmente quedan invisibles en el roadmap
- el valor de plataforma depende tanto de estas piezas como de analytics o AI
- sin una epic fuerte, seguridad y colaboracion se vuelven mantenimiento reactivo

## 3. Objective

Hacer visible y trazable el frente de plataforma para sostener crecimiento y operacion confiable.

## 4. User value

Como admin o equipo colaborativo, quiero operar UKIP con permisos claros, auditoria y mecanismos de colaboracion para usar la plataforma con confianza.

## 5. Scope

Incluye:

- autenticacion y RBAC
- API keys
- auditoria
- organizaciones
- anotaciones y notificaciones
- gobernanza operativa documental del proyecto

Excluye:

- infraestructura cloud profunda
- nuevos modulos de negocio no transversales

## 6. Success criteria

- el frente transversal de plataforma queda explicitado
- seguridad y colaboracion tienen historias trazables
- la gobernanza documental se reconoce como parte del frente de plataforma

## 7. Technical impact

- backend: `auth_users.py`, `api_keys.py`, `audit_log.py`, `organizations.py`, `annotations.py`, `notifications.py`
- frontend: `frontend/app/settings/`, `frontend/app/notifications/`, `frontend/app/profile/`
- docs: sistema operativo, gobernanza, onboarding

## 8. Risks

- riesgo: tratar seguridad y colaboracion como trabajo invisible
- impacto: fragilidad operativa y perdida de coherencia
- mitigacion: incluir historias transversales de plataforma en cada ciclo relevante

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-007 | Formalizar la gobernanza operativa para el equipo de agentes | Done |
| US-008 | Iniciar el backfill operativo de epicas, historias y sprint activo | Done |
| US-036 | Administracion de usuarios, roles y acceso | Planned |
| US-037 | Ciclo de vida de API keys | Planned |
| US-038 | Colaboracion con anotaciones y notificaciones | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Establecer la base de gobernanza y trazabilidad del proyecto |

## 11. Evidence

- Docs: `docs/DOCUMENTATION_GOVERNANCE.md`, `docs/DELIVERY_OPERATING_SYSTEM.md`, `docs/product/*`
