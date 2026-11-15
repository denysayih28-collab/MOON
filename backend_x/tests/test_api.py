from sqlalchemy import select

from app.catalog import INDICATORS
from app.models import Alert, Astronaut, Measurement
from app.seed import ASTRONAUTS
from app.services.alert_engine import evaluate_measurement

from .conftest import CODE, OP, post_m


# ---------- Accès par ID ----------
def test_access_with_valid_id(client):
    r = client.post("/api/access", json={"code": CODE})
    assert r.status_code == 200
    body = r.json()
    assert body["last_name"] == "Marchand" and body["mission"]["name"] == "MOON-DEMO-01"
    assert body["mission_day"] >= 1 and "password" not in body


def test_access_is_case_insensitive(client):
    assert client.post("/api/access", json={"code": CODE.lower()}).status_code == 200


def test_access_unknown_id(client):
    assert client.post("/api/access", json={"code": "AST-XXXXXX"}).status_code == 404


def test_five_fictional_astronauts_seeded(session_factory):
    with session_factory() as db:
        assert db.query(Astronaut).count() == 5


# ---------- Test 1 : consultation / test 8 : provenance ----------
def test_latest_measurements_have_unit_date_source(client):
    r = client.get("/api/measurements/latest", params={"astronaut_code": CODE})
    assert r.status_code == 200
    data = r.json()
    assert {m["indicator"] for m in data} == {i[0] for i in INDICATORS}
    for m in data:
        assert m["unit"] and m["recorded_at"].endswith(("Z", "+00:00")) and m["source"] == "simulated"


def test_history_filter_by_indicator(client):
    r = client.get("/api/measurements", params={"astronaut_code": CODE, "indicator": "heart_rate"})
    assert r.status_code == 200 and len(r.json()) > 10
    assert all(m["indicator"] == "heart_rate" for m in r.json())


# ---------- Données de départ dans les normes : aucune alerte ----------
def test_seed_data_all_within_normal_ranges(session_factory):
    with session_factory() as db:
        norms = {i[0]: (i[6], i[7]) for i in INDICATORS}
        for m in db.scalars(select(Measurement)):
            lo, hi = norms[m.indicator_code]
            if lo is not None:
                assert m.value >= lo, (m.indicator_code, m.value)
            if hi is not None:
                assert m.value <= hi, (m.indicator_code, m.value)
        assert db.query(Alert).count() == 0


def test_replaying_seed_data_through_engine_creates_no_alert(session_factory):
    with session_factory() as db:
        for m in db.scalars(select(Measurement).order_by(Measurement.recorded_at)):
            assert evaluate_measurement(db, m) == []


# ---------- Test 2 / 3 : enregistrement et rejet ----------
def test_valid_measurement_saved_and_retrievable(client):
    r = post_m(client, "heart_rate", 72, "bpm", source="manual")
    assert r.status_code == 201 and r.json()["alerts"] == []
    hist = client.get("/api/measurements", params={"astronaut_code": CODE, "indicator": "heart_rate"}).json()
    assert any(m["id"] == r.json()["measurement"]["id"] and m["source"] == "manual" for m in hist)


def test_wrong_unit_rejected(client):
    r = post_m(client, "heart_rate", 72, "°C")
    assert r.status_code == 422 and "Unité incompatible" in r.json()["detail"]


def test_implausible_value_rejected(client):
    assert post_m(client, "heart_rate", 5000, "bpm").status_code == 422


def test_unknown_indicator_and_malformed_value(client):
    assert post_m(client, "glycemia", 5, "mmol/L").status_code == 422
    r = client.post("/api/measurements", json={"astronaut_code": CODE, "indicator": "heart_rate",
                                               "value": "abc", "unit": "bpm"})
    assert r.status_code == 422


def test_unknown_astronaut_rejected(client):
    assert post_m(client, "heart_rate", 72, "bpm", code="AST-XXXXXX").status_code == 404


def test_public_dataset_requires_reference(client):
    assert post_m(client, "heart_rate", 72, "bpm", source="public_dataset").status_code == 422
    ok = post_m(client, "heart_rate", 72, "bpm", source="public_dataset", source_reference="OSDR-123")
    assert ok.status_code == 201


# ---------- Test 4 / 5 : alertes ----------
def test_normal_value_creates_no_alert(client):
    assert post_m(client, "heart_rate", 80, "bpm").json()["alerts"] == []


def test_severe_value_alerts_immediately(client):
    r = post_m(client, "heart_rate", 135, "bpm")
    alerts = r.json()["alerts"]
    assert len(alerts) == 1 and alerts[0]["level"] == "high_priority" and alerts[0]["rule_id"] == "HR-05"
    assert alerts[0]["status"] == "active" and alerts[0]["rule_condition"]


def test_attention_rule_needs_two_consecutive_measurements(client):
    assert post_m(client, "heart_rate", 110, "bpm").json()["alerts"] == []
    second = post_m(client, "heart_rate", 112, "bpm").json()["alerts"]
    assert len(second) == 1 and second[0]["level"] == "attention" and second[0]["rule_id"] == "HR-04"


def test_normal_reading_breaks_the_streak(client):
    post_m(client, "heart_rate", 110, "bpm")
    post_m(client, "heart_rate", 80, "bpm")
    assert post_m(client, "heart_rate", 112, "bpm").json()["alerts"] == []


def test_no_duplicate_active_alert_for_same_rule(client):
    post_m(client, "heart_rate", 135, "bpm")
    assert post_m(client, "heart_rate", 140, "bpm").json()["alerts"] == []
    assert len(client.get("/api/alerts", params={"astronaut_code": CODE}).json()) == 1


def test_spo2_sleep_and_temperature_rules(client):
    assert post_m(client, "spo2", 88, "%").json()["alerts"][0]["level"] == "high_priority"
    assert post_m(client, "sleep_duration", 5, "h").json()["alerts"][0]["rule_id"] == "SLEEP-02"
    post_m(client, "body_temperature", 38.2, "°C")
    assert post_m(client, "body_temperature", 38.4, "°C").json()["alerts"][0]["rule_id"] == "TEMP-02"


def test_alert_status_lifecycle_keeps_history(client):
    alert = post_m(client, "heart_rate", 135, "bpm").json()["alerts"][0]
    r = client.patch(f"/api/alerts/{alert['id']}", params={"astronaut_code": CODE}, json={"status": "resolved"})
    assert r.status_code == 200 and r.json()["status"] == "resolved" and r.json()["resolved_at"]
    assert client.get("/api/alerts", params={"astronaut_code": CODE, "status": "active"}).json() == []
    assert len(client.get("/api/alerts", params={"astronaut_code": CODE}).json()) == 1


def test_astronaut_cannot_read_another_astronauts_alert(client):
    alert = post_m(client, "heart_rate", 135, "bpm").json()["alerts"][0]
    other = ASTRONAUTS[1][0]
    assert client.get(f"/api/alerts/{alert['id']}", params={"astronaut_code": other}).status_code == 404


# ---------- Test 6 : persistance ----------
def test_data_persists_across_sessions(client, session_factory):
    alert_id = post_m(client, "heart_rate", 135, "bpm").json()["alerts"][0]["id"]
    with session_factory() as fresh:  # nouvelle session = « redémarrage »
        assert fresh.get(Alert, alert_id) is not None


# ---------- Simulation ----------
def test_simulation_requires_operator_key(client):
    assert client.get("/api/simulation/scenarios").status_code == 401
    assert client.get("/api/simulation/scenarios", headers={"X-Operator-Key": "bad"}).status_code == 401
    assert client.get("/api/simulation/scenarios", headers=OP).status_code == 200
    assert client.get("/api/simulation/astronauts").status_code == 401  # les ID ne sont pas publics


def test_every_scenario_triggers_its_expected_level(client):
    scenarios = client.get("/api/simulation/scenarios", headers=OP).json()
    assert len(scenarios) == 10
    for s in scenarios:
        client.post("/api/simulation/reset", headers=OP, json={"astronaut_code": CODE})
        r = client.post(f"/api/simulation/scenarios/{s['name']}", headers=OP, json={"astronaut_code": CODE})
        assert r.status_code == 200, s["name"]
        levels = {a["level"] for a in r.json()["alerts"]}
        assert s["expected_level"] in levels, (s["name"], levels)
        assert all(a["source"] == "simulated" for a in r.json()["alerts"])


def test_free_value_simulation_and_reset(client):
    r = client.post("/api/simulation/measurements", headers=OP,
                    json={"astronaut_code": CODE, "indicator": "spo2", "value": 93, "repeat": 2})
    assert r.status_code == 200 and r.json()["alerts"][0]["rule_id"] == "SPO2-01"
    before = len(client.get("/api/measurements", params={"astronaut_code": CODE}).json())
    reset = client.post("/api/simulation/reset", headers=OP, json={"astronaut_code": CODE}).json()
    assert reset["measurements_deleted"] == 2 and reset["alerts_deleted"] == 1
    assert client.get("/api/alerts", params={"astronaut_code": CODE}).json() == []
    assert len(client.get("/api/measurements", params={"astronaut_code": CODE}).json()) == before - 2


def test_unknown_scenario(client):
    r = client.post("/api/simulation/scenarios/nope", headers=OP, json={"astronaut_code": CODE})
    assert r.status_code == 404


def test_health_and_indicators(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    inds = client.get("/api/indicators").json()
    assert len(inds) == 14 and all("normal_min" in i for i in inds)
