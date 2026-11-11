"""Read-only API. It serves stored results and never computes scores."""

from fastapi import FastAPI

from radar import __version__

app = FastAPI(title="Radar", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
