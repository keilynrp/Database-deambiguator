# US-025 - Orquestacion de enrichment individual y masivo

## 1. User story

Como operador o analista, quiero disparar enrichment individual o masivo y entender su progreso para ampliar mis datos sin perder control del proceso.

## 2. Context

- Epic: `EPIC-004`
- Sprint objetivo: `SPRINT-103`

## 3. Acceptance criteria

- [ ] el usuario puede lanzar enrichment individual y bulk
- [ ] el sistema expone estados y resultados del proceso
- [ ] errores y fallbacks son visibles de forma operativa

## 4. Functional notes

- flujo: seleccionar entidades -> lanzar enrichment -> revisar estado -> abrir resultado
- edge cases: proveedor caido, rate limit, registros ya enriquecidos

## 5. Technical notes

- `backend/enrichment_worker.py`
- `backend/routers/authority.py`
- tabs de enrichment en frontend

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- Logs:
