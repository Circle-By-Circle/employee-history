# HRIS interview practice

A reconstructed starter project based on the supplied HRIS code and screenshot. The exact original source history was unavailable. Scheduling code, scheduling tests, implementation notes, and plans have been removed.

The app supports browsing and searching employees, hiring, immediate edits, termination, and history snapshots. It uses Flask, SQLAlchemy, SQLite, and a plain HTML/JavaScript frontend.

## Run locally

Requires Python 3.9 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m hris.app
```

Open http://localhost:8000. Sample data is created on the first launch. Edits survive server reloads.

To reset the local sample database (this discards your practice data):

```sh
python -m hris.seed
```

## Tests

```sh
python -m pytest -q
```

See [INTERVIEW.md](INTERVIEW.md) for the exercise. There is no scheduling solution or implementation plan in this starter.
