# US-044 - Enforcements de tenant en queries y acceso

## 1. User story

Como cliente institucional, quiero que las consultas y escrituras respeten tenant isolation para que mis datos no se mezclen con otros.

## 2. Context

- Epic: `EPIC-012`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] las queries criticas aplican filtros de tenant
- [ ] endpoints sensibles no devuelven recursos cruzados
- [ ] el enforcement es reusable y testeable

## 4. Functional notes

- depende de modelo y estrategia de tenant scoping definida

## 5. Technical notes

- auth deps
- queries de entidades y recursos multiusuario

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Docs:
