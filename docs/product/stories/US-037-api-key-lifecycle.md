# US-037 - Ciclo de vida de API keys

## 1. User story

Como usuario tecnico, quiero crear y revocar API keys con scopes para integrar UKIP de forma segura desde sistemas externos.

## 2. Context

- Epic: `EPIC-010`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] el usuario puede crear una API key y verla una sola vez
- [ ] puede revisar metadata y revocarla cuando haga falta
- [ ] los scopes y el uso quedan claros

## 4. Functional notes

- flujo: crear key -> copiar -> usar -> revisar lista -> revocar
- edge cases: expiracion, scope insuficiente, key revocada

## 5. Technical notes

- `backend/routers/api_keys.py`
- UI de configuracion o developer settings
- auth compartida con JWT

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- API examples:
