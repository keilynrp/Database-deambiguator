# US-041 - Ciclo seguro de migraciones y arranque

## 1. User story

Como equipo tecnico, quiero que las migraciones tengan un lifecycle seguro para evitar side effects al importar modulos o correr tests.

## 2. Context

- Epic: `EPIC-011`
- Sprint objetivo: `SPRINT-104`

## 3. Acceptance criteria

- [x] las migraciones no corren al importar el modulo principal
- [x] existe un punto de arranque mas controlado para upgrade de schema
- [x] tests y boot local no tocan accidentalmente la DB equivocada

## 4. Functional notes

- flujo: importar app -> no migrar; arrancar app o tarea controlada -> migrar si corresponde
- edge cases: entornos sin DB lista, fallos de migracion

## 5. Technical notes

- `backend/main.py`
- Alembic
- scripts de arranque y test

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- PR:
- Test: `backend.main` importa sin correr Alembic implicitamente; import time bajo de ~65s a ~33s; `backend/tests/test_sprint86_5.py` y `backend/tests/test_sprint94_pg_hardening.py` pasan
- Docs: `README.md`, `docs/TECHNICAL_ONBOARDING.md`, `docs/CONTRIBUTING.md`, `start.bat`
- Code: `backend/main.py`, `backend/tests/conftest.py`, `backend/tests/test_sprint86_5.py`
