# test_db.py
import sys
from sqlalchemy import create_engine, text

URL = "postgresql+psycopg2://fitness_user:fitness_pass@localhost:5433/fitness_db"
print("Using URL:", URL)

try:
    engine = create_engine(URL, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print("SELECT 1 ->", result)
except Exception as e:
    print("ERROR:", type(e).__name__, e)
    sys.exit(1)
