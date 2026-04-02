# US-058 - UKIP NIL Benchmark and Evaluation Pack

## 1. User story

Como equipo de producto e ingenieria, quiero un benchmark propio de `NIL entity linking` para medir precision, cobertura y regresiones antes de introducir nuevas heuristicas o LLMs.

## 2. Context

- Epic: `EPIC-004`
- Dependencias recomendadas: `US-056`, `US-057`

## 3. Acceptance criteria

- [ ] existe un dataset o pack de evaluacion reproducible alineado con el wedge actual de UKIP
- [ ] el pack incluye casos `in-KB`, ambiguos, `NIL` reales y `artificial NIL` generados de forma controlada
- [ ] se miden al menos:
  - NIL detection precision/recall
  - exact linking quality
  - fallback parcial a conceptos mas generales
  - review load esperado
- [ ] la evaluacion corre offline sin dependencia de servicios de produccion
- [ ] el benchmark no depende de `MedPath` para ser util en UKIP

## 4. Functional notes

- author-first y research-intelligence first
- puede inspirarse en estrategias tipo `EvaNIL`, pero adaptadas a UKIP
- priorizar corpus y casos propios antes de adoptar datasets biomedicos externos como pieza central

## 5. Technical notes

- fixtures de tests y datasets de evaluacion
- scripts reproducibles para scoring offline
- documentacion de protocolo de evaluacion
- `backend/tests/`
- `docs/product/`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Notes for prioritization

- clave para evitar drift y sobre-optimizar sobre ejemplos manuales
- mas alineado con UKIP que incorporar `MedPath` como dependencia central hoy
