# Pilot Review - UDG Executive Dashboard - 2026-04-10

## 1. Summary

Piloto real ejecutado sobre un recorte OpenAlex de Universidad de Guadalajara
con flujo completo:

- import
- executive dashboard
- institutional benchmark
- suggested next actions
- concept map
- top entities by impact
- brief/export support

Resultado general: UKIP ya entrega una lectura ejecutiva creible para un piloto
interno serio. El sistema paso de una demo funcional a una experiencia con
valor analitico visible y accionable.

## 2. What worked well

- el flujo `import -> dashboard -> brief` ya es corto y entendible
- el dashboard cuenta una historia clara con volumen, cobertura, calidad e
  impacto
- el benchmark institucional agrega contexto util y no se siente decorativo
- las recomendaciones ya son explicables y operables
- el CTA de bulk enrichment desde el dashboard reduce friccion real
- el concept map ya aporta lectura semantica util
- la shortlist de impacto ya se ve mas limpia para stakeholder review

## 3. Current pilot readout

- `total_entities`: `1000`
- `enriched_count`: `329`
- `enrichment_pct`: `32.9%`
- `avg_citations`: `322.5`
- `total_concepts`: `1777`
- `avg_quality_pct`: `49.8%`
- benchmark `sni_readiness_baseline`: `33.3%`

## 4. Main findings

### Product

- UKIP ya puede convertir una importacion real en una salida ejecutiva defendible
- la experiencia principal ya no depende de exploracion tecnica profunda
- el dashboard ahora sugiere una accion y permite ejecutarla de inmediato

### Analytics

- el mayor cuello de botella actual es cobertura/calidad, no UI
- los conceptos ya emergen con fuerza suficiente para una lectura inicial
- `Emerging Topic Signals` todavia no agrega valor real en este dataset y debe
  seguir tratado como modulo experimental secundario

### Narrative

- el piloto ya comunica mejor:
  - que tan listo esta el dataset
  - que hacer despues
  - donde estan las entidades mas fuertes
- la narrativa del benchmark y las acciones sugeridas ya es util para briefings

## 5. Remaining gaps

- la cobertura de enrichment sigue siendo demasiado baja para una lectura
  institucional fuerte
- la calidad promedio todavia queda por debajo del umbral objetivo del benchmark
- el vocabulario semantico sigue reflejando parte del ruido natural de OpenAlex
- las señales emergentes necesitan mas profundidad temporal o mayor cobertura
  para ser realmente convincentes

## 6. Decisions

### Decision 1

Dar `US-060` y `US-061` por validadas funcionalmente en un piloto real.

### Decision 2

No seguir invirtiendo de inmediato en mas polish del dashboard ejecutivo salvo
ajustes puntuales de hallazgos reales.

### Decision 3

Priorizar el siguiente salto de valor en benchmark/operacion, no en mas
cosmetica:

- benchmark mas configurable por institucion/tenant
- mayor operabilidad alrededor de enrichment y calidad

## 7. Recommended next steps

1. abrir el siguiente corte de `US-067` para perfiles configurables por tenant
2. revisar si conviene una accion complementaria desde dashboard para
   `quality_score` compute cuando aplique
3. ejecutar un segundo piloto con mayor cobertura o una institucion diferente
4. mantener `US-069` como capa experimental conservadora, sin sobreprometer

## 8. Roadmap implication

Este piloto confirma que la prioridad correcta no es otra ronda grande de
frontend decomposition ni mas visual polish del dashboard. La prioridad ahora
debe moverse hacia:

- benchmark institucional mas configurable
- mejora de cobertura/calidad operativa
- nuevos pilotos con datasets reales

