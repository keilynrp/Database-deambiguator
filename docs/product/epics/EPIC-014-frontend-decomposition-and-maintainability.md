# EPIC-014 - Frontend Decomposition and Maintainability

## 1. Summary

Reducir componentes gigantes del frontend para mejorar testabilidad, reviewability y velocidad de iteracion.

## 2. Problem

- hay componentes con demasiada responsabilidad y tamano
- esto frena testing, code review y cambios seguros
- la deuda de UI amenaza crecer con cada feature nueva

## 3. Objective

Descomponer piezas criticas del frontend en modulos mas pequenos y mantenibles.

## 4. User value

Como equipo de producto, quiero un frontend mas mantenible para entregar cambios de UI y flujo con menos riesgo.

## 5. Scope

Incluye:

- `EntityTable.tsx`
- `Sidebar.tsx`
- `RAGChatInterface.tsx`
- otros componentes criticos de alto tamano

Excluye:

- rediseño visual completo
- cambio de framework de estado global

## 6. Success criteria

- al menos los componentes mas grandes tienen plan de descomposicion
- el trabajo futuro del frontend es mas testeable
- la deuda visible deja de crecer sin control

## 7. Technical impact

- `frontend/app/components/*`
- tests frontend
- posible reorganizacion por subcomponentes y hooks

## 8. Risks

- riesgo: refactor grande sin valor inmediato de usuario
- impacto: regresiones de UI y churn alto
- mitigacion: hacer decomposition incremental, no reescritura total

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-049 | Descomponer EntityTable en modulos manejables | Planned |
| US-050 | Reducir componentes frontend gigantes del shell y AI UI | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-TBD | Ejecutar decomposition despues del hardening base mas urgente |

## 11. Evidence

- Valoracion tecnica senior 2026-03-24
- componentes frontend criticos
