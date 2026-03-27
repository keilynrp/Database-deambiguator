# US-047 - Definir MVP comercial y onboarding real

## 1. User story

Como equipo de producto, quiero definir un MVP comercial y un onboarding real para enfocar ingenieria y salida a mercado sin dispersion.

## 2. Context

- Epic: `EPIC-013`
- Sprint objetivo: `SPRINT-104`

## 3. Acceptance criteria

- [x] existe definicion explicita del vertical inicial o foco comercial
- [x] existe recorrido de onboarding real mas alla de demo mode
- [x] las prioridades tecnicas se conectan a ese MVP

## 4. Functional notes

- puede enfocarse en un vertical inicial como scientometrics/research intelligence

## 5. Technical notes

- docs de producto
- onboarding
- posibles flujos iniciales del frontend

## 6. Definition of done

- [x] implementado
- [x] probado
- [x] documentado
- [x] trazabilidad actualizada

## 7. Evidence

- Documento MVP: `docs/product/COMMERCIAL_MVP.md`
- Flujo onboarding: `backend/routers/onboarding.py`, `frontend/app/components/OnboardingChecklist.tsx`, `frontend/app/components/WelcomeModal.tsx`
- Tests: `backend/tests/test_sprint95_onboarding.py`, `frontend/__tests__/OnboardingChecklist.test.tsx`
- Riesgos: mantener la promesa comercial enfocada en research intelligence y no volver a narrativa demasiado generalista antes de cerrar `US-048`
