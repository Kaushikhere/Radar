from fastapi.testclient import TestClient

from radar import __version__
from radar.api.main import app


def test_health_returns_ok_and_version():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
