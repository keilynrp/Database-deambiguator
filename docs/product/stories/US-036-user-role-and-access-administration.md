# US-036 - Administracion de usuarios, roles y acceso

## 1. User story

Como super admin, quiero gestionar usuarios, roles y estados de acceso para operar la plataforma con seguridad y control.

## 2. Context

- Epic: `EPIC-010`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] se pueden listar, crear, editar y activar/desactivar usuarios
- [ ] la asignacion de roles es visible y controlada
- [ ] el acceso respeta RBAC en endpoints y UI

## 4. Functional notes

- flujo: abrir settings -> revisar usuarios -> cambiar rol o estado
- edge cases: rol invalido, usuario desactivado, permisos insuficientes

## 5. Technical notes

- `backend/routers/auth_users.py`
- `frontend/app/settings/`
- auth y deps de permisos

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Screenshots:
