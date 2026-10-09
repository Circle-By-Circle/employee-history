"""Integration tests."""

from datetime import datetime, timezone


def test_user_interface_disables_caching(client):
    resp = client.get("/")

    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "no-store"


def test_list_employees_excludes_terminated_by_default(client, seed):
    resp = client.get("/employees")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(e["end_date"] is None for e in data)


def test_include_terminated(client, seed):
    resp = client.get("/employees?include_terminated=true")
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(e["end_date"] is not None for e in data)


def test_search_by_name(client, seed):
    resp = client.get("/employees?q=alice")
    assert resp.status_code == 200
    names = [e["first_name"] for e in resp.get_json()]
    assert "Alice" in names


def test_hire_employee(client, seed):
    resp = client.post(
        "/employees",
        json={
            "first_name": "New",
            "last_name": "Hire",
            "email": "new@acme.com",
            "start_date": "2024-01-01",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["first_name"] == "New"
    assert data["end_date"] is None


def test_hire_missing_required_field(client, seed):
    resp = client.post(
        "/employees",
        json={
            "first_name": "No",
            "last_name": "Email",
            "start_date": "2024-01-01",
        },
    )
    assert resp.status_code == 400


def test_get_employee_by_id(client, seed):
    resp = client.get(f"/employees/{seed.alice_id}")
    assert resp.status_code == 200
    assert resp.get_json()["first_name"] == "Alice"


def test_get_nonexistent_employee(client, seed):
    assert client.get("/employees/999999").status_code == 404


def test_terminate_sets_end_date(client, seed):
    resp = client.delete(f"/employees/{seed.dave_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["end_date"] == datetime.now(timezone.utc).date().isoformat()


def test_terminate_already_terminated(client, seed):
    client.delete(f"/employees/{seed.dave_id}")
    resp = client.delete(f"/employees/{seed.dave_id}")
    assert resp.status_code == 400


def test_terminate_nonexistent(client, seed):
    assert client.delete("/employees/999999").status_code == 404


def test_update_records_snapshot(client, seed):
    client.put(f"/employees/{seed.bob_id}", json={"title": "CTO"})
    history = client.get(f"/employees/{seed.bob_id}/history").get_json()
    assert len(history) == 1
    assert history[0]["title"] == "CTO"
    assert history[0]["changed_at"].endswith("Z")


def test_terminate_records_snapshot(client, seed):
    client.delete(f"/employees/{seed.dave_id}")
    history = client.get(f"/employees/{seed.dave_id}/history").get_json()
    assert len(history) == 1
    assert history[0]["end_date"] == datetime.now(timezone.utc).date().isoformat()
