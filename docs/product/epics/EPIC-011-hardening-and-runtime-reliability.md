# EPIC-011 - Hardening and Runtime Reliability

## 1. Summary

Endurecer la base tecnica de UKIP para que el runtime, las dependencias y el path de despliegue sean reproducibles, creibles y sostenibles para un MVP comercial.

## 2. Problem

- SQLite como default y dependencias no fijadas reducen credibilidad tecnica
- el lifecycle de migraciones y jobs en proceso hace fragil el runtime
- varias afirmaciones de readiness dependen de cerrar estos huecos primero

## 3. Objective

Mover UKIP de un runtime orientado a demo hacia un runtime orientado a producto operable.

## 4. User value

Como equipo tecnico y eventual cliente enterprise, quiero una plataforma predecible y estable para confiar en despliegues, upgrades y operacion diaria.

## 5. Scope

Incluye:

- dependency locking
- PostgreSQL-first path
- lifecycle seguro de migraciones
- roadmap de externalizacion de background jobs

Excluye:

- tenant isolation profunda
- billing y compliance comercial

## 6. Success criteria

- dependencias reproducibles
- runtime primario orientado a PostgreSQL
- migraciones desacopladas del import de modulo
- plan claro para sacar workers fuera del proceso web

## 7. Technical impact

- `requirements.txt`
- `backend/database.py`
- `backend/main.py`
- Docker y scripts de arranque

## 8. Risks

- riesgo: tocar path de arranque y DB puede afectar entorno de desarrollo
- impacto: regresiones en boot o tests
- mitigacion: avanzar por historias pequenas y validar boot dev/prod por separado

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-039 | Lockfile y reproducibilidad de dependencias | Planned |
| US-040 | PostgreSQL-first runtime y despliegue | Planned |
| US-041 | Ciclo seguro de migraciones y arranque | Planned |
| US-042 | Plan de externalizacion de background jobs | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-104 | Cerrar los gaps de runtime y reproducibilidad mas peligrosos |

## 11. Evidence

- Valoracion tecnica senior 2026-03-24
- `requirements.txt`
- `backend/database.py`
- `backend/main.py`
