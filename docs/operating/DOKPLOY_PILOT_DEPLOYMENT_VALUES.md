# Dokploy Pilot Deployment Values

This file records the non-secret values for the first UKIP pilot deployment.

Do not place real passwords, API keys, JWT secrets, session secrets, database
passwords, or encryption keys in this file.

## Current Release Candidate

- Commit: `80905837c147b1e5e566767be3cb65754c60637b`
- Short SHA: `8090583`

## GHCR Image Tags

Use pinned SHA tags for the first pilot:

```env
UKIP_BACKEND_IMAGE=ghcr.io/keilynrp/ukip-backend:sha-8090583
UKIP_FRONTEND_IMAGE=ghcr.io/keilynrp/ukip-frontend:sha-8090583
```

## Dokploy Registry Access

Local manifest checks against GHCR returned `unauthorized`, which means Dokploy
must either:

1. authenticate to GHCR with a GitHub token that can read packages, or
2. pull from packages that have been made public.

For a controlled pilot, prefer authenticated pulls.

Recommended GitHub token scope:

- `read:packages`

Use the GitHub account or organization that can access:

- `ghcr.io/keilynrp/ukip-backend`
- `ghcr.io/keilynrp/ukip-frontend`

## Domains to Replace Before Deploy

Replace these placeholders in Dokploy:

```env
ALLOWED_ORIGINS=https://ukip.example.org
NEXT_PUBLIC_API_URL=https://api.ukip.example.org
```

The frontend image bakes `NEXT_PUBLIC_API_URL` at build time, so the first
production image should be built with the final API domain when possible.

## Required Secret Values

Set these directly in Dokploy:

- `DATABASE_URL`
- `ADMIN_PASSWORD` or `ADMIN_PASSWORD_HASH`
- `JWT_SECRET_KEY`
- `SESSION_SECRET_KEY`
- `ENCRYPTION_KEY`

Generate `ENCRYPTION_KEY` with:

```powershell
.\.venv\Scripts\python.exe scripts\generate_fernet_key.py
```

## First Deploy Command Order

1. Configure GHCR registry credentials in Dokploy.
2. Configure PostgreSQL and copy its `DATABASE_URL`.
3. Configure the environment variables.
4. Run `alembic upgrade head` once.
5. Start backend.
6. Start frontend.
7. Bind domains and TLS.
8. Run the smoke tests from the runbook.
