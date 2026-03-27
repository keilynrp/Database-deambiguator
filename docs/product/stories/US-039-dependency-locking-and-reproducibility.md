# US-039 - Lockfile y reproducibilidad de dependencias

## 1. User story

Como equipo tecnico, quiero instalaciones reproducibles para evitar builds distintos entre entornos y reducir riesgo de regresiones invisibles.

## 2. Context

- Epic: `EPIC-011`
- Sprint objetivo: `SPRINT-104`

## 3. Acceptance criteria

- [x] existe un mecanismo claro de lock de dependencias
- [x] el camino oficial de instalacion usa versiones reproducibles
- [x] la documentacion de setup refleja ese nuevo camino

## 4. Functional notes

- flujo: instalar dependencias -> obtener mismo entorno en dev y CI
- edge cases: incompatibilidades de versiones, transitive deps rotas

## 5. Technical notes

- `requirements.txt`
- lockfile o gestor equivalente
- CI y docs de setup

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Artefactos: `requirements.lock`, `requirements.txt`
- Docs: `README.md`, `docs/TECHNICAL_ONBOARDING.md`, `docs/CONTRIBUTING.md`
- Validacion: verificacion directa de referencias a `requirements.lock` y generacion del lockfile desde `.venv`
