# US-034 - Gestion de alert channels y webhooks

## 1. User story

Como admin, quiero configurar canales de alerta y webhooks para enterarme o notificar eventos del sistema en tiempo real.

## 2. Context

- Epic: `EPIC-009`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] se pueden registrar y probar canales de alerta
- [ ] el usuario puede elegir eventos suscritos
- [ ] el sistema registra errores o entregas fallidas

## 4. Functional notes

- flujo: crear canal -> seleccionar eventos -> probar -> revisar entrega
- edge cases: URL invalida, timeout, credenciales malas

## 5. Technical notes

- `backend/routers/alert_channels.py`
- `backend/routers/webhooks.py`
- UI de integraciones

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Logs:
