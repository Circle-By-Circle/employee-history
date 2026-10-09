from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    employees = relationship("Employee", back_populates="company")


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    title = Column(String)
    department = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    salary = Column(Numeric(precision=12, scale=2), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    company = relationship("Company", back_populates="employees")
    manager = relationship("Employee", remote_side=[id], back_populates="reports")
    reports = relationship("Employee", back_populates="manager")
    history = relationship(
        "EmployeeHistory",
        back_populates="employee",
        order_by="EmployeeHistory.changed_at",
    )


class EmployeeHistory(Base):
    __tablename__ = "employee_history"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    changed_at = Column(DateTime, default=utc_now, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    title = Column(String)
    department = Column(String)
    manager_id = Column(Integer, nullable=True)
    salary = Column(Numeric(precision=12, scale=2), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    employee = relationship("Employee", back_populates="history")


def init_db(db_path="hris.db"):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
