# Orbit

Orbit is a personal intelligence platform. It brings your email, calendar, tasks, and news into one daily dashboard, and uses an LLM to tell you what matters today.

> **Status:** early development. The project foundation is in place; features are being built one at a time (see [Roadmap](#roadmap)).

## Features

- Connect Gmail and Google Calendar with OAuth 2.0
- Spot important emails and messages that need a reply
- Generate a daily briefing with upcoming events and priorities
- Aggregate news from multiple sources
- Categorise and summarise information with an LLM
- Search everything in natural language

## Architecture

```text
            ┌──────────────┐
 Browser ──▶│   Next.js    │  frontend/  · dashboard UI
            └──────┬───────┘
                   │ HTTP / JSON
            ┌──────▼───────┐        ┌──────────────┐
            │   FastAPI    │───────▶│  PostgreSQL  │  data + pgvector embeddings
            └──────┬───────┘        └──────▲───────┘
                   │ enqueue jobs          │
            ┌──────▼───────┐        ┌──────┴───────┐
            │    Redis     │◀───────│    Celery    │  sync, summarise, embed
            └──────────────┘        └──────────────┘
```

The API serves the dashboard. Slow work (syncing Gmail, calling the LLM, creating embeddings) runs in Celery workers so requests stay fast.

## Tech stack

| Area            | Tools                                          |
| --------------- | ---------------------------------------------- |
| Frontend        | Next.js, React, TypeScript, Tailwind CSS       |
| Backend         | Python, FastAPI, SQLAlchemy, Alembic           |
| Database        | PostgreSQL with pgvector                       |
| Background jobs | Celery with Redis                              |
| AI              | LLM API, embeddings, retrieval                 |
| Infrastructure  | Docker, Docker Compose, GitHub Actions         |

## Project structure

```text
orbit/
├── backend/
│   ├── app/
│   │   ├── api/          # HTTP routes, grouped by feature in api/routes/
│   │   ├── auth/         # Google OAuth, session cookies, linking accounts
│   │   ├── models/       # SQLAlchemy database models
│   │   ├── worker/       # Celery app and background tasks
│   │   ├── config.py     # Settings, read from environment variables
│   │   ├── db.py         # Database engine and sessions
│   │   ├── encryption.py # Encrypts tokens before they reach the database
│   │   └── main.py       # FastAPI app
│   ├── migrations/       # Alembic database migrations
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/          # Pages (Next.js App Router)
│       ├── components/   # Shared UI components
│       └── lib/          # API client and other non-UI code
├── .github/              # CI workflow, Dependabot, PR template
└── docker-compose.yml    # Local development stack
```

## Getting started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose
- [Node.js](https://nodejs.org/) 24 or newer
- [uv](https://docs.astral.sh/uv/) (to run backend tests and tools locally)

### 1. Configure your environment

```bash
cp .env.example .env
```

Generate `SESSION_SECRET` and `TOKEN_ENCRYPTION_KEY` with the commands in `.env.example`. The app refuses to start without them. The Google values come from step 2: the stack runs without them, but you can't sign in until they're set.

### 2. Set up Google sign-in

Orbit signs people in with Google and asks for read-only access to Gmail and Google Calendar. You need your own OAuth client:

1. In the [Google Cloud console](https://console.cloud.google.com/), create a project and enable the **Gmail API** and the **Google Calendar API**.
2. Under **Google Auth Platform**, set up the consent screen with the **External** audience, and add your Google account as a **test user**.
3. Under **Clients**, create a **Web application** client with this authorised redirect URI:
   `http://localhost:8000/api/auth/google/callback`
4. Copy the client ID and secret into `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`.

While the app is in Google's **Testing** mode, only test users can sign in, Google warns that the app is unverified, and refresh tokens expire after 7 days. Opening the app to other people requires [Google's verification](https://support.google.com/cloud/answer/13463073), because Gmail access is a restricted scope.

### 3. Start the backend stack

This starts PostgreSQL, Redis, the API, and the worker, and applies database migrations.

```bash
docker compose up --build
```

- API: http://localhost:8000/api/health
- API docs: http://localhost:8000/api/docs
- PostgreSQL: `localhost:5433` (not 5432, so it won't clash with a locally installed PostgreSQL)

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

The dashboard calls the API at `http://localhost:8000`. To use another address, set `NEXT_PUBLIC_API_URL` when you build the frontend, and set `FRONTEND_URL` on the API to the dashboard's address. The two must be on the same site (for example `app.example.com` and `api.example.com`), because the session cookie is `SameSite=Lax`.

## Development

### Backend

Run these from `backend/`:

```bash
uv sync                                    # install dependencies
uv run pytest                              # run tests
uv run ruff check . && uv run ruff format .  # lint and format
```

Database migrations (with the Docker stack running):

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

Always review an autogenerated migration before committing it.

### Frontend

Run these from `frontend/`:

```bash
npm run lint        # ESLint
npm run format      # Prettier
npm run typecheck   # TypeScript
npm run build       # production build
```

## Security

- Secrets live in `.env`, which is never committed. `.env.example` lists the variables without real values. Secrets have no defaults, so the app won't start without them. Only the Google OAuth client may be left out, and only outside production.
- Sign in with Google uses the authorization code flow with PKCE and a `state` check, and asks only for read-only Gmail and Calendar access.
- Google tokens are encrypted at rest with Fernet (`TOKEN_ENCRYPTION_KEY`), so a database dump alone doesn't expose them.
- Sessions are signed, `HttpOnly`, `SameSite=Lax` cookies, and `Secure` in production. The API only accepts credentialed requests from `FRONTEND_URL`.
- Local database and Redis ports are bound to `127.0.0.1` only.
- Containers run as unprivileged users.
- API docs are disabled in production.
- The frontend sends baseline security headers on every response.
- Dependabot opens weekly pull requests for dependency updates.

## Roadmap

- [x] Project foundation: API, worker, database, migrations, dashboard shell, CI
- [x] Sign in with Google (OAuth 2.0) and encrypted token storage
- [ ] Gmail sync and "needs a reply" detection
- [ ] Google Calendar sync
- [ ] News aggregation
- [ ] LLM categorisation and daily briefing
- [ ] Embeddings and natural-language search

## Contributing

This project follows GitHub flow. See [CONTRIBUTING.md](CONTRIBUTING.md).
