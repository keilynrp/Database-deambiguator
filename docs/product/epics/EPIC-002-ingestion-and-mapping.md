# EPIC-002 - Ingestion and Mapping

## 1. Summary

Convertir la ingesta de datos en un frente de producto trazable y robusto, desde la carga de archivos hasta el mapeo de columnas y la importacion consistente al modelo universal.

## 2. Problem

- la ingesta es una puerta de entrada critica del valor de UKIP
- import wizard, preview y mapping ya existen, pero faltaba una epic operativa que los agrupe
- sin una linea clara de backlog, mejoras de ingestion pueden quedar desconectadas del modelo universal

## 3. Objective

Tener una linea de producto clara para todo lo relacionado con captacion, validacion y mapeo de datos de entrada.

## 4. User value

Como operador de datos, quiero importar archivos y mapear sus columnas de forma confiable para llevar informacion al sistema sin friccion ni ambiguedad.

## 5. Scope

Incluye:

- upload
- preview
- analisis de archivos
- sugerencia de mapping
- import wizard
- exportacion base asociada al flujo

Excluye:

- harmonizacion posterior a la importacion
- enrichment externo posterior

## 6. Success criteria

- existe trazabilidad clara del frente de ingestion
- el backlog futuro de importacion puede planificarse bajo esta epic
- el frente conecta UI, endpoints y valor funcional sin depender de documentos sueltos

## 7. Technical impact

- backend: `backend/routers/ingest.py`, `column_maps.py`, parsers
- frontend: `frontend/app/import/`, `frontend/app/import-export/`
- tests: flujos asociados a importacion y preview

## 8. Risks

- riesgo: tratar importacion como plumbing tecnico
- impacto: debilidad en UX y en calidad de entrada al sistema
- mitigacion: usar esta epic como contenedor obligatorio del frente

## 9. Stories

| ID | Story | Estado |
|---|---|---|
| US-009 | Backfillear el frente de ingestion y mapping en el sistema operativo | Done |
| US-010 | Formalizar criterios operativos para import wizard y column mapping | Planned |
| US-019 | Preview y validacion de archivos antes de importar | Planned |
| US-020 | Mapeo manual y asistido de columnas | Planned |

## 10. Sprint allocation

| Sprint | Objetivo |
|---|---|
| SPRINT-102 | Incorporar ingestion al marco operativo vivo |

## 11. Evidence

- Codigo: `backend/routers/ingest.py`, `frontend/app/import/`, `frontend/app/import-export/`
- Docs: `README.md`, `API.md`, `docs/product/TRACEABILITY_MATRIX.md`
