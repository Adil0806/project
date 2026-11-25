"""Тесты эндпоинтов. Запуск: ``pytest``."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SLUGS = ["trm138", "dz-so", "pchv3", "io"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_index_and_devices():
    assert client.get("/").status_code == 200
    assert len(client.get("/api/devices").json()) == 4


@pytest.mark.parametrize("slug", SLUGS)
def test_pages_and_state(slug):
    page = client.get(f"/{slug}/")
    assert page.status_code == 200 and "Применить изменения" in page.text
    assert client.get(f"/api/{slug}/state").status_code == 200
    assert isinstance(client.get(f"/api/{slug}/logs?limit=3").json(), list)
    assert client.post(f"/api/{slug}/poll").status_code == 200


def test_trm138_write_setpoint():
    r = client.post("/api/trm138/write", json={"sp1": 55.5})
    assert r.json()["channels"][0]["sp"] == 55.5


def test_dz_so_thresholds_validation():
    client.post("/api/dz-so/write", json={"thr1": 10, "thr2": 30})
    state = client.post("/api/dz-so/write", json={"thr1": 40, "thr2": 30}).json()
    assert (state["thr1"], state["thr2"]) == (10, 30)  # неверные значения отклонены


def test_pchv3_form_post_and_clamp():
    r = client.post("/pchv3/", data={"setpoint": "99", "run": "on"}, follow_redirects=False)
    assert r.status_code == 303
    state = client.get("/api/pchv3/state").json()
    assert state["setpoint"] == 50 and state["run"] is True and state["reverse"] is False
    client.post("/pchv3/", data={"setpoint": "10"})  # чекбокс снят -> стоп
    assert client.get("/api/pchv3/state").json()["run"] is False


def test_io_ao_range():
    r = client.post("/api/io/write", json={"ao1": 100, "ao2": 0})
    ao = r.json()["ao"]
    assert ao[0]["ma"] == 20 and ao[1]["ma"] == 4
