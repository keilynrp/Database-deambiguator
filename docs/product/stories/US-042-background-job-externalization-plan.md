# US-042 - Plan de externalizacion de background jobs

## 1. User story

Como equipo tecnico, quiero un plan claro para sacar workers del proceso web para reducir fragilidad operativa y preparar ejecucion confiable.

## 2. Context

- Epic: `EPIC-011`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] existe decision documentada sobre stack de jobs
- [ ] se identifican workers actuales y riesgos
- [ ] hay propuesta incremental de migracion

## 4. Functional notes

- cubre enrichment, scheduled imports y scheduled reports
- evita salto directo a una reescritura sin plan

## 5. Technical notes

- `backend/enrichment_worker.py`
- schedulers actuales
- decision entre Celery, RQ u otra opcion

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- ADR o doc:
- Riesgos:
- Plan incremental:
