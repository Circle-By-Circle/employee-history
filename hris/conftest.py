from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    from .models import Base, Company, Employee

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    acme = Company(name="Acme Corp")
    globex = Company(name="Globex Inc")
    session.add_all([acme, globex])
    session.flush()

    alice_emp = Employee(
        company_id=acme.id,
        first_name="Alice",
        last_name="Smith",
        email="alice@acme.com",
        title="CEO",
        department="Executive",
        start_date=date(2019, 1, 15),
    )
    session.add(alice_emp)
    session.flush()

    bob_emp = Employee(
        company_id=acme.id,
        first_name="Bob",
        last_name="Jones",
        email="bob@acme.com",
        title="VP Engineering",
        department="Engineering",
        manager_id=alice_emp.id,
        start_date=date(2019, 6, 1),
    )
    session.add(bob_emp)
    session.flush()

    dave_emp = Employee(
        company_id=acme.id,
        first_name="Dave",
        last_name="Brown",
        email="dave@acme.com",
        title="Senior Engineer",
        department="Engineering",
        manager_id=bob_emp.id,
        start_date=date(2021, 3, 15),
    )
    session.add(dave_emp)
    session.flush()

    grace_emp = Employee(
        company_id=acme.id,
        first_name="Grace",
        last_name="Lee",
        email="grace@acme.com",
        title="Recruiter",
        department="HR",
        manager_id=alice_emp.id,
        start_date=date(2021, 1, 1),
        end_date=date(2023, 12, 31),
    )
    session.add(grace_emp)
    session.flush()

    homer_emp = Employee(
        company_id=globex.id,
        first_name="Homer",
        last_name="Simpson",
        email="homer@globex.com",
        title="Safety Inspector",
        department="Operations",
        start_date=date(2010, 4, 5),
    )
    session.add(homer_emp)
    session.commit()

    ns = SimpleNamespace(
        acme_id=acme.id,
        globex_id=globex.id,
        alice_id=alice_emp.id,
        bob_id=bob_emp.id,
        dave_id=dave_emp.id,
        grace_id=grace_emp.id,
        homer_id=homer_emp.id,
    )
    yield session, ns
    session.close()


@pytest.fixture
def db(db_session):
    session, _ = db_session
    yield session
    session.rollback()  # undo any mutations made by the test


@pytest.fixture
def seed(db_session):
    _, ns = db_session
    return ns


@pytest.fixture
def client(db, seed, monkeypatch):
    from . import app as flask_app
    from flask import g

    def override_get_db():
        if "db" not in g:
            g.db = db
        return g.db

    monkeypatch.setattr(flask_app, "get_db", override_get_db)
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c
