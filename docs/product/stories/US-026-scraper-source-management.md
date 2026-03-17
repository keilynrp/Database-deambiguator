# US-026 - Gestion de fuentes de scraping para enrichment

## 1. User story

Como admin, quiero configurar fuentes de scraping para enrichment cuando las APIs principales no cubren mi caso.

## 2. Context

- Epic: `EPIC-004`
- Sprint objetivo: `SPRINT-TBD`

## 3. Acceptance criteria

- [ ] se pueden crear y editar fuentes de scraping
- [ ] existe una forma de probar la configuracion
- [ ] el sistema deja claro limites, errores y fallback del scraper

## 4. Functional notes

- flujo: crear config -> probar selector -> guardar -> usar en enrichment
- edge cases: selector invalido, sitio inaccesible, respuestas parciales

## 5. Technical notes

- `backend/routers/scrapers.py`
- UI de scrapers
- `httpx` y `lxml`

## 6. Definition of done

- [ ] implementado
- [ ] probado
- [ ] documentado
- [ ] trazabilidad actualizada

## 7. Evidence

- PR:
- Test:
- API examples:
