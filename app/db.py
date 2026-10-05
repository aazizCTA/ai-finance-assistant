"""Database setup and seed data.

Run `uv run python -m app.db` from the project root to (re)create finance.db.
"""
import random
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "finance.db"

CATEGORIES = [
    "groceries", "rent", "utilities", "transport",
    "eating_out", "entertainment", "shopping", "income",
]

# Fixed dates + fixed random seed = same data every run.
# Your eval script needs this later so expected answers stay stable.
SEED_START = date(2026, 4, 1)
SEED_END = date(2026, 9, 30)

MERCHANTS = {
    "groceries": [("Tesco", 15, 90), ("Sainsbury's", 10, 80), ("Aldi", 10, 60)],
    "transport": [("TfL travel", 2.8, 8.5), ("Uber", 8, 25), ("Trainline", 15, 70)],
    "eating_out": [("Nando's", 12, 30), ("Pret A Manger", 4, 12), ("Deliveroo", 15, 35)],
    "entertainment": [("Cinema tickets", 8, 15), ("Steam", 5, 40), ("Concert tickets", 30, 80)],
    "shopping": [("Amazon", 8, 120), ("ASOS", 20, 90), ("Boots", 5, 30)],
}


@contextmanager
def get_conn():
    """Yield a connection that commits on success and always closes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,   -- YYYY-MM-DD
                description TEXT NOT NULL,
                amount      REAL NOT NULL,   -- always positive; 'income' = money in
                category    TEXT NOT NULL
            )
        """)


def seed():
    """Drop and rebuild the table with ~6 months of dummy data."""
    rng = random.Random(42)
    rows = []
    day = SEED_START
    while day <= SEED_END:
        if day.day == 1:
            rows.append((day, "Rent - Flat 4B", 950.00, "rent"))
            rows.append((day, "Octopus Energy", round(rng.uniform(60, 110), 2), "utilities"))
            rows.append((day, "Three Mobile", 15.00, "utilities"))
        if day.day == 25:
            rows.append((day, "Salary - Acme Ltd", 2300.00, "income"))
        for _ in range(rng.choice([0, 1, 1, 2])):
            category = rng.choice(list(MERCHANTS))
            name, low, high = rng.choice(MERCHANTS[category])
            rows.append((day, name, round(rng.uniform(low, high), 2), category))
        day += timedelta(days=1)

    with get_conn() as conn:
        conn.execute("DROP TABLE IF EXISTS transactions")
    init_db()
    with get_conn() as conn:
        conn.executemany(
            "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
            [(d.isoformat(), desc, amt, cat) for d, desc, amt, cat in rows],
        )
    return len(rows)


if __name__ == "__main__":
    print(f"Seeded {seed()} transactions into {DB_PATH}")