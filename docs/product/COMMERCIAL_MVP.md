# Commercial MVP

Definicion operativa del MVP comercial inicial de UKIP para `EPIC-013` y `US-047`.

## 1. Foco inicial

UKIP entra al mercado primero como una plataforma de `research intelligence` para equipos que necesitan consolidar, limpiar y analizar portafolios de publicaciones.

Esto incluye especialmente:

- oficinas de investigacion
- bibliotecas universitarias con funcion analitica
- equipos de estrategia de innovacion o I+D

## 2. Problema que resolvemos primero

El usuario ya tiene datos, pero estan fragmentados entre exportaciones de sistemas internos, hojas de calculo, RIS/BibTeX y fuentes externas. Antes de confiar en dashboards o reportes ejecutivos, necesita:

- importar el portafolio real
- enriquecer autores, afiliaciones y metadata
- corregir ruido repetitivo con reglas de harmonizacion
- validar KPIs basicos de cobertura y tendencia

## 3. Recorrido real de onboarding

El onboarding comercial real deja de girar alrededor de demo mode y sigue este camino:

1. importar publicaciones, autores y afiliaciones desde CSV, Excel, BibTeX o RIS
2. ejecutar enrichment y review de authority para elevar calidad minima del dataset
3. capturar al menos una regla reusable de harmonizacion
4. abrir analytics para revisar cobertura, gaps y tendencias
5. opcionalmente crear un workflow o reporte para el siguiente ciclo operativo

## 4. Time to first value

Objetivo razonable del MVP:

- primera carga y primer insight util en `30-60 minutos`

Ese insight puede ser:

- cobertura de enrichment
- brechas de metadata
- top entidades o afiliaciones
- tendencia basica del portafolio

## 5. Prioridades tecnicas conectadas al MVP

Las prioridades tecnicas inmediatas que mas impactan este MVP son:

- ingestion estable de datos bibliograficos y tabulares
- enrichment y authority review confiables
- harmonizacion reusable para nombres y afiliaciones
- analytics de portafolio listos para conversacion con stakeholders
- workflows/reportes simples para seguimiento recurrente

## 6. Lo que no estamos prometiendo todavia

Este MVP no debe venderse como:

- SaaS enterprise completamente multi-tenant
- plataforma generalista ya endurecida para cualquier vertical
- suite completa de compliance enterprise
- sistema de billing o plan enforcement comercial terminado

## 7. Artefactos relacionados

- `README.md`
- `backend/routers/onboarding.py`
- `frontend/app/components/OnboardingChecklist.tsx`
- `frontend/app/components/WelcomeModal.tsx`
- `docs/product/epics/EPIC-013-commercial-readiness-and-credibility.md`
- `docs/product/stories/US-047-commercial-mvp-and-onboarding-definition.md`
