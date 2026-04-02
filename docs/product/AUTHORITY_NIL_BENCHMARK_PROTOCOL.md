# Authority NIL Benchmark Protocol

## Purpose

Establecer una evaluacion offline, reproducible y versionada para `author resolution` y `NIL detection` en UKIP.

## Scope

- wedge `author-first`
- sin dependencias de servicios externos
- orientado a regresion de calidad antes de cambiar heuristicas, thresholds o introducir LLMs

## Assets

- dataset versionado: `backend/tests/fixtures/author_nil_benchmark.json`
- runner offline: `backend/authority/benchmark.py`
- script reproducible: `scripts/evaluate_author_nil_benchmark.py`
- regression test: `backend/tests/test_sprint106_nil_benchmark.py`

## Dataset design

El pack `ukip_author_nil_benchmark_v1` cubre:

- `in_kb`
- `ambiguous`
- `real_nil`
- `artificial_nil`

Cada caso define:

- valor a resolver
- contexto opcional (`affiliation`, `orcid_hint`, etc.)
- candidatos sinteticos
- resultado esperado
- disponibilidad de fallback parcial a ancestro cuando aplica

## Metrics

El runner mide, como baseline minima:

- `nil_precision`
- `nil_recall`
- `exact_link_accuracy`
- `route_accuracy`
- `review_load_rate`
- `partial_fallback_available_rate`
- `avg_nil_score_on_predicted_nil`
- `avg_complexity_score`

## Interpretation notes

- `partial_fallback_available_rate` no significa que UKIP ya haga `hierarchical fallback` en runtime.
- La metrica refleja si el corpus de evaluacion contiene un ancestro util disponible para medir ese frente de calidad antes de `US-057`.
- El objetivo es congelar una baseline y detectar drift, no sobre-optimizar para ejemplos manuales aislados.

## Execution

Validacion automatizada:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_sprint106_nil_benchmark.py -q
```

Ejecucion manual del runner:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_author_nil_benchmark.py
```

## Update rules

- si cambia la heuristica de `author_resolution` o `nil_detection`, correr primero este pack
- si el cambio es intencional, actualizar dataset o expectativas de test en el mismo commit
- no introducir datasets externos como dependencia central mientras el wedge siga siendo `research intelligence` author-first
