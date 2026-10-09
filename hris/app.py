import os
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS
from .models import Employee, init_db
from .seed import seed
from .service import EmployeeService, NotFoundError, ValidationError

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app = Flask(__name__)
CORS(app)
Session = init_db()


def get_db():
    if "db" not in g:
        g.db = Session()
    return g.db


@app.teardown_appcontext
def close_db(_exc=None):
    db = g.pop("db", None)
    if db:
        db.close()


def get_service():
    return EmployeeService(get_db())


def _utc_iso(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serialize_employee(emp):
    return {
        "id": emp.id,
        "company_id": emp.company_id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "full_name": f"{emp.first_name} {emp.last_name}",
        "email": emp.email,
        "title": emp.title,
        "department": emp.department,
        "manager_id": emp.manager_id,
        "salary": str(emp.salary) if emp.salary is not None else None,
        "start_date": emp.start_date.isoformat() if emp.start_date else None,
        "end_date": emp.end_date.isoformat() if emp.end_date else None,
    }


def serialize_history(h):
    return {
        "id": h.id,
        "changed_at": _utc_iso(h.changed_at),
        "first_name": h.first_name,
        "last_name": h.last_name,
        "email": h.email,
        "title": h.title,
        "department": h.department,
        "manager_id": h.manager_id,
        "salary": str(h.salary) if h.salary is not None else None,
        "start_date": h.start_date.isoformat() if h.start_date else None,
        "end_date": h.end_date.isoformat() if h.end_date else None,
    }


@app.get("/")
def index():
    response = send_from_directory(STATIC_DIR, "index.html")
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/employees")
def list_employees():
    search = request.args.get("q") or None
    include_terminated = request.args.get("include_terminated") == "true"
    employees = get_service().list_employees(
        search=search, include_terminated=include_terminated
    )
    return jsonify([serialize_employee(e) for e in employees])


@app.post("/employees")
def hire():
    try:
        emp = get_service().hire(request.json or {})
        return jsonify(serialize_employee(emp)), 201
    except ValidationError as e:
        return jsonify(error=str(e)), 400


@app.get("/employees/<int:emp_id>")
def get_employee(emp_id):
    try:
        emp = get_service().get_employee(emp_id)
        return jsonify(serialize_employee(emp))
    except NotFoundError as e:
        return jsonify(error=str(e)), 404


@app.get("/employees/<int:emp_id>/history")
def get_employee_history(emp_id):
    try:
        history = get_service().get_employee_history(emp_id)
        return jsonify([serialize_history(h) for h in history])
    except NotFoundError as e:
        return jsonify(error=str(e)), 404


@app.put("/employees/<int:emp_id>")
def update_employee(emp_id):
    try:
        emp = get_service().update(emp_id, request.json or {})
        return jsonify(serialize_employee(emp))
    except NotFoundError as e:
        return jsonify(error=str(e)), 404
    except ValidationError as e:
        return jsonify(error=str(e)), 400


@app.delete("/employees/<int:emp_id>")
def terminate_employee(emp_id):
    try:
        emp = get_service().terminate(emp_id)
        return jsonify(serialize_employee(emp))
    except NotFoundError as e:
        return jsonify(error=str(e)), 404
    except ValidationError as e:
        return jsonify(error=str(e)), 400


if __name__ == "__main__":
    if not os.path.exists("hris.db"):
        seed()
    app.run(host="127.0.0.1", debug=True, port=8000)
