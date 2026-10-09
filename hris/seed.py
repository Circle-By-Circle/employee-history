from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Company, Employee


def seed(db_path="hris.db"):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()

    acme = Company(name="Acme Corp")
    db.add(acme)
    db.flush()

    alice = Employee(
        company_id=acme.id,
        first_name="Alice",
        last_name="Smith",
        email="alice@acme.com",
        title="CEO",
        department="Executive",
        start_date=date(2019, 1, 15),
    )
    db.add(alice)
    db.flush()

    bob = Employee(
        company_id=acme.id,
        first_name="Bob",
        last_name="Jones",
        email="bob@acme.com",
        title="VP Engineering",
        department="Engineering",
        manager_id=alice.id,
        start_date=date(2019, 6, 1),
    )
    carol = Employee(
        company_id=acme.id,
        first_name="Carol",
        last_name="White",
        email="carol@acme.com",
        title="VP Human Resources",
        department="HR",
        manager_id=alice.id,
        start_date=date(2020, 2, 1),
    )
    db.add_all([bob, carol])
    db.flush()

    dave = Employee(
        company_id=acme.id,
        first_name="Dave",
        last_name="Brown",
        email="dave@acme.com",
        title="Senior Engineer",
        department="Engineering",
        manager_id=bob.id,
        start_date=date(2021, 3, 15),
    )
    eve = Employee(
        company_id=acme.id,
        first_name="Eve",
        last_name="Davis",
        email="eve@acme.com",
        title="Engineer",
        department="Engineering",
        manager_id=bob.id,
        start_date=date(2022, 7, 1),
    )
    frank = Employee(
        company_id=acme.id,
        first_name="Frank",
        last_name="Miller",
        email="frank@acme.com",
        title="Product Designer",
        department="Design",
        manager_id=alice.id,
        start_date=date(2099, 1, 1),
    )
    grace = Employee(
        company_id=acme.id,
        first_name="Grace",
        last_name="Lee",
        email="grace@acme.com",
        title="Recruiter",
        department="HR",
        manager_id=carol.id,
        start_date=date(2021, 1, 1),
        end_date=date(2023, 12, 31),
    )
    db.add_all([dave, eve, frank, grace])
    db.flush()

    globex = Company(name="Globex Inc")
    db.add(globex)
    db.flush()

    homer = Employee(
        company_id=globex.id,
        first_name="Homer",
        last_name="Simpson",
        email="homer@globex.com",
        title="Safety Inspector",
        department="Operations",
        start_date=date(2010, 4, 5),
    )
    db.add(homer)
    db.commit()
    db.close()
    print("Database seeded.")


if __name__ == "__main__":
    seed()
