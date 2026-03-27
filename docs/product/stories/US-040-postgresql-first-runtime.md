# US-040 - PostgreSQL-first runtime y despliegue

## 1. User story

Como equipo tecnico, quiero que PostgreSQL sea el path principal de producto para evitar limites de concurrencia y discrepancias entre demo y produccion.

## 2. Context

- Epic: `EPIC-011`
- Sprint objetivo: `SPRINT-104`

## 3. Acceptance criteria

- [x] la documentacion y despliegue oficial priorizan PostgreSQL
- [x] SQLite queda claramente marcado como opcion local/dev
- [x] los paths criticos del sistema se validan sobre PostgreSQL

## 4. Functional notes

- flujo: levantar entorno -> usar PostgreSQL como base por defecto de producto
- edge cases: dev local simple, tests actuales basados en SQLite

## 5. Technical notes

- `backend/database.py`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `start.bat`
- `.env.example`
- docs de setup y despliegue

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- PR:
- Test: conexion validada contra PostgreSQL real con `('ukip', 'ukip')`; Alembic corre sobre `PostgresqlImpl`; fallback SQLite sigue disponible con `UKIP_DB_MODE=sqlite`
- Docs: `README.md`, `docs/TECHNICAL_ONBOARDING.md`, `docs/CONTRIBUTING.md`, `start.bat`, `.env.example`, `.env`, `docker-compose.dev.yml`
- Note: el import de `backend.main` sigue tardando ~65s porque `_run_migrations()` corre al importar el modulo; esto se transfiere a `US-041`
