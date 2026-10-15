# Orbit

Personal intelligence platform: email, calendar, and news in one daily dashboard. See README.md for architecture and setup, and CONTRIBUTING.md for workflow and code principles. Follow both.

## Working agreements

- Choose simple, conventional code over clever code. Clean, organised, and easy to understand comes first.
- Follow GitHub flow: work on a branch, never commit to `main` directly, and open a pull request.
- Keep security and UX in mind in every change (see CONTRIBUTING.md).

## Commands

Backend (from `backend/`): `uv run pytest`, `uv run ruff check .`, `uv run ruff format .`

Frontend (from `frontend/`): `npm run lint`, `npm run format`, `npm run typecheck`, `npm run build`

Full stack: `docker compose up --build` from the repo root.

## Conventions

- Backend routes live in `backend/app/api/routes/<feature>.py` and are registered in `backend/app/api/router.py`.
- New models go in `backend/app/models/` and must be imported in `backend/app/models/__init__.py` so Alembic sees them.
- Use the `get_db` dependency from `backend/app/db.py` for database sessions in routes.
- Celery tasks must be idempotent: the worker uses late acknowledgement, so a task can run more than once.
- Frontend pages live in `frontend/src/app/`; shared components in `frontend/src/components/`.
- This repo uses Next.js 16 with Cache Components; read `frontend/node_modules/next/dist/docs/` before using unfamiliar Next.js APIs.
