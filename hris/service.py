from __future__ import annotations

"""Service layer — all business logic lives here, independent of HTTP."""


from datetime import date, datetime, timezone
from .models import Employee, EmployeeHistory


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class EmployeeService:
    def __init__(self, db):
        self.db = db

    def hire(self, data: dict) -> Employee:
        required = {"first_name", "last_name", "email", "start_date"}
        missing = required - data.keys()
        if missing:
            raise ValidationError(f"Missing required fields: {missing}")
        try:
            start = date.fromisoformat(data["start_date"])
        except ValueError as exc:
            raise ValidationError("start_date must be YYYY-MM-DD") from exc

        emp = Employee(
            company_id=data.get("company_id", 1),
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            title=data.get("title"),
            department=data.get("department"),
            manager_id=data.get("manager_id"),
            salary=data.get("salary"),
            start_date=start,
        )
        self.db.add(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def update(self, employee_id: int, data: dict) -> Employee:
        emp = self.db.get(Employee, employee_id)
        if emp is None:
            raise NotFoundError(f"Employee {employee_id} not found")

        self._apply_updates(emp, data)
        self.db.flush()
        self._record_snapshot(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def _apply_updates(self, emp: Employee, data: dict) -> None:
        for field in (
            "first_name",
            "last_name",
            "email",
            "title",
            "department",
            "manager_id",
            "salary",
        ):
            if field in data:
                setattr(emp, field, data[field])
        if "start_date" in data:
            try:
                emp.start_date = date.fromisoformat(data["start_date"])
            except ValueError as exc:
                raise ValidationError("start_date must be YYYY-MM-DD") from exc

    def terminate(self, employee_id: int) -> Employee:
        emp = self.db.get(Employee, employee_id)
        if emp is None:
            raise NotFoundError(f"Employee {employee_id} not found")
        if emp.end_date is not None:
            raise ValidationError("Employee is already terminated")

        emp.end_date = datetime.now(timezone.utc).date()
        self.db.flush()
        self._record_snapshot(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def get_employee(self, employee_id: int) -> Employee:
        emp = self.db.get(Employee, employee_id)
        if emp is None:
            raise NotFoundError(f"Employee {employee_id} not found")
        return emp

    def get_employee_history(self, employee_id: int) -> list:
        self.get_employee(employee_id)
        q = self.db.query(EmployeeHistory)
        q = q.filter(EmployeeHistory.employee_id == employee_id)
        return q.order_by(
            EmployeeHistory.changed_at.asc(), EmployeeHistory.id.asc()
        ).all()

    def list_employees(
        self, search: str | None = None, include_terminated: bool = False
    ) -> list:
        q = self.db.query(Employee)
        if not include_terminated:
            q = q.filter(Employee.end_date == None)
        if search:
            like = f"%{search}%"
            q = q.filter(
                Employee.first_name.ilike(like)
                | Employee.last_name.ilike(like)
                | Employee.email.ilike(like)
                | Employee.title.ilike(like)
                | Employee.department.ilike(like)
            )
        return q.order_by(Employee.last_name, Employee.first_name).all()

    def _record_snapshot(self, emp: Employee) -> None:
        self.db.add(
            EmployeeHistory(
                employee_id=emp.id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                title=emp.title,
                department=emp.department,
                manager_id=emp.manager_id,
                salary=emp.salary,
                start_date=emp.start_date,
                end_date=emp.end_date,
            )
        )
