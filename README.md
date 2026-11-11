# Radar

A point-in-time financial data pipeline and research shortlist for NSE stocks, with a
survivorship-free backtest. It is a research filter, not a stock picker: it gives no
buy or sell advice.

**Status:** Phase 0 (skeleton and data spike). See [doc/PHASE.md](doc/PHASE.md).

## Docs

| File | What it covers |
|---|---|
| [doc/PLAN.md](doc/PLAN.md) | Scope, scoring model, schema and build plan |
| [doc/PHASE.md](doc/PHASE.md) | What each phase delivers, and the push log |
| [doc/DECISIONS.md](doc/DECISIONS.md) | Why each decision was made |
| [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md) | System design and rejected alternatives |
| [doc/SPIKE.md](doc/SPIKE.md) | What the exchange archives actually hold |
| [doc/PRD.md](doc/PRD.md) | The original requirements |

## Run it

Needs Docker.

```bash
cp .env.example .env
docker compose up --build
```

The API is then at http://localhost:8000/health and its docs at http://localhost:8000/docs.

## Develop

Needs Python 3.12 or newer. CI and the Docker image use 3.12.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; use `source .venv/bin/activate` elsewhere
pip install -e ".[dev]"

docker compose up -d db         # Postgres only
alembic upgrade head            # apply migrations
pytest                          # run tests
ruff check . && ruff format --check .
```

To run the checks inside Docker instead:

```bash
docker compose run --rm api pytest
docker compose run --rm api alembic upgrade head
```
