# Technical Onboarding

Guia practica para empezar a tocar codigo en UKIP sin perderte.

## 1. Que es UKIP

UKIP (`Universal Knowledge Intelligence Platform`) es un monorepo con:

- `backend/`: API en FastAPI
- `frontend/`: UI en Next.js + React

La idea central del sistema es trabajar sobre entidades universales. El punto de partida real es `UniversalEntity` en `backend/models.py`. Alrededor de esa entidad viven importacion, harmonizacion, authority resolution, enrichment, analytics, grafos, dashboards, reportes y RAG.

## 2. Orden de lectura recomendado

Si entras por primera vez, lee en este orden:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `backend/main.py`
4. `backend/models.py`
5. `backend/database.py`
6. `backend/routers/`
7. `frontend/package.json`
8. `frontend/app/layout.tsx`
9. `frontend/app/page.tsx`
10. `frontend/lib/api.ts`

No intentes recorrer todo el repo. En este proyecto funciona mejor leer una feature de punta a punta.

## 3. Modelo mental rapido

Piensa el sistema en 5 capas:

1. **Datos**
   - `backend/models.py`
   - `backend/schemas.py`
2. **API**
   - `backend/routers/*.py`
3. **Logica especializada**
   - enrichment, analytics, exporters, workflows, graph, adapters
4. **Frontend**
   - `frontend/app/*`
   - `frontend/app/components/*`
   - `frontend/app/contexts/*`
5. **Infra**
   - Alembic, Docker, `.env`, tests, CI

## 4. Mapa corto del repo

### Backend

- `backend/main.py`: entrypoint, routers, lifecycle, workers y schedulers.
- `backend/models.py`: modelos ORM principales.
- `backend/database.py`: engine y sesiones.
- `backend/routers/`: endpoints por dominio.
- `backend/domains/`: schemas YAML (`default`, `science`, `healthcare`).
- `backend/tests/`: tests backend.

### Frontend

- `frontend/app/`: rutas App Router.
- `frontend/app/components/`: componentes reutilizables.
- `frontend/app/contexts/`: auth, idioma, theme, branding, dominio.
- `frontend/lib/api.ts`: wrapper de fetch con token y proxy.
- `frontend/__tests__/`: tests unitarios con Vitest.
- `frontend/e2e/`: smoke tests con Playwright.

### Infra

- `.env.example`: variables de entorno backend.
- `docker-compose.yml`: stack tipo produccion.
- `docker-compose.dev.yml`: stack dev alineado con PostgreSQL.
- `start.bat`: arranque local rapido en Windows.
- `alembic/`: migraciones.

## 5. Como corre el sistema

### Backend

- FastAPI
- PostgreSQL como ruta principal en local y despliegue
- SQLite solo como fallback explicito de compatibilidad
- Alembic al arranque
- workers/schedulers para enrichment, imports y reportes

### Frontend

- Next.js 16
- React 19
- Tailwind 4
- Browser -> llama via `/api/backend/*`
- SSR -> usa `NEXT_PUBLIC_API_URL`

## 6. Primer arranque local

### Windows rapido

```bat
start.bat
```

### Manual

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.lock
docker compose -f docker-compose.dev.yml up -d postgres
alembic upgrade head
uvicorn backend.main:app --reload --port 8000
```

Si Docker vive solo en WSL Ubuntu, levanta PostgreSQL desde el repo montado en WSL, por ejemplo:

```bash
cd /mnt/d/universal-knowledge-intelligence-platform
docker compose -f docker-compose.dev.yml up -d postgres
```

Las migraciones ya no corren al importar `backend.main`; el upgrade de schema es un paso explicito de arranque.

Checks operativos utiles:

- `GET /health` expone estado del servicio, estado de DB, `request_id`, formato de log y duracion del probe.
- `LOG_FORMAT=json` produce logs estructurados; `LOG_FORMAT=text` conserva los mismos campos en texto.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

URLs habituales:

- backend: `http://localhost:8000`
- docs: `http://localhost:8000/docs`
- frontend: `http://localhost:3004`

## 7. Variables que debes conocer

Del backend:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ALLOWED_ORIGINS`
- `SESSION_SECRET_KEY`

Del frontend:

- `NEXT_PUBLIC_API_URL`

## 7.1 Dependencias reproducibles

Para backend:

- `requirements.txt` define la intencion humana de dependencias
- `requirements.lock` es la referencia reproducible de instalacion

Usa `requirements.lock` para entornos repetibles, CI y despliegues.

## 8. Que tocar segun el tipo de cambio

### Si cambias persistencia o datos

Revisa:

- `backend/models.py`
- migracion Alembic
- schemas Pydantic
- router afectado
- tests

### Si cambias un endpoint

Revisa:

- `backend/routers/<dominio>.py`
- schema relacionado
- componente o pagina que lo consume
- tests backend/frontend

### Si cambias UI

Revisa:

- `frontend/app/<ruta>/page.tsx`
- componentes usados
- `frontend/lib/api.ts` si cambia la llamada
- test del componente o pagina

### Si cambias auth o permisos

Revisa:

- `backend/auth.py`
- `backend/auth_users.py`
- dependencias de permisos
- `frontend/app/contexts/AuthContext`

## 9. Archivos que conviene ubicar rapido

Backend:

- `backend/routers/entities.py`
- `backend/routers/ingest.py`
- `backend/routers/analytics.py`
- `backend/routers/authority.py`
- `backend/routers/disambiguation.py`
- `backend/routers/ai_rag.py`
- `backend/routers/reports.py`
- `backend/routers/workflows.py`

Frontend:

- `frontend/app/page.tsx`
- `frontend/app/entities/`
- `frontend/app/analytics/`
- `frontend/app/authority/`
- `frontend/app/disambiguation/`
- `frontend/app/import/`
- `frontend/app/import-export/`
- `frontend/app/rag/`
- `frontend/app/reports/`
- `frontend/app/settings/`

## 10. Metodo para no perderte en una feature

Usa siempre este recorrido:

1. identifica la pantalla o endpoint
2. ubica la ruta frontend
3. sigue el `apiFetch()`
4. encuentra el router backend
5. revisa schema y modelo
6. mira tests existentes
7. cambia lo minimo posible
8. valida en UI y test

Regla practica: **lee vertical, no horizontal**.

## 11. Testing rapido

Backend:

```bash
pytest backend/tests
pytest backend/tests/test_auth.py
```

Frontend:

```bash
cd frontend
npm run test
npm run lint
```

E2E:

```bash
cd frontend
npm run e2e
```

## 12. Cuando algo se rompe

### Frontend no levanta

Revisa en este orden:

1. `frontend/package.json`
2. `frontend/next.config.ts`
3. `frontend/app/layout.tsx`
4. `frontend/lib/api.ts`
5. dependencias instaladas

### Backend no levanta

Revisa en este orden:

1. `.env`
2. `backend/main.py`
3. `backend/database.py`
4. migraciones
5. imports nuevos

### Un endpoint responde mal

Revisa:

1. router
2. schema
3. modelo
4. datos reales
5. tests del dominio

## 13. Realidades del repo

- Hay mucha historia de sprints; varios tests siguen nombrados por sprint.
- Parte de la documentacion secundaria esta desfasada frente al producto actual.
- Si hay conflicto, confia mas en:
  - `backend/main.py`
  - `backend/models.py`
  - `backend/routers/`
  - `frontend/app/`
- Evita refactors amplios si solo necesitas arreglar un flujo puntual.

## 14. Primeras tareas buenas para aprender el sistema

1. levantar backend y frontend
2. abrir `/docs` y autenticarte
3. recorrer home, entities, analytics, authority y disambiguation
4. seguir una llamada UI -> API -> modelo
5. ejecutar un test backend y uno frontend
6. hacer un cambio pequeno de UI y otro de backend

## 15. Resumen corto

Para orientarte rapido:

- piensa en `UniversalEntity` como centro
- sigue una feature desde la UI hasta el router y el modelo
- empieza por `backend/main.py`, `backend/models.py`, `frontend/app/layout.tsx` y `frontend/lib/api.ts`
- cambia poco, prueba pronto y valida contratos
