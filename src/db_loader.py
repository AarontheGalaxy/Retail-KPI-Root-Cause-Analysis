"""
╔══════════════════════════════════════════════════════════════╗
║  db_loader.py — SQLite Database Loader                      ║
║  Loads retail_sales.csv into data/retail.db                 ║
║  with optimized indexes for analytical queries              ║
║                                                             ║
║  🐢 AarontheGalaxy                                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sqlite3
import logging
import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CSV_PATH = "data/retail_sales.csv"
DB_PATH  = "data/retail.db"
TABLE    = "sales_transactions"


# ---------------------------------------------------------------------------
# Schema Definition
# ---------------------------------------------------------------------------
CREATE_TABLE_SQL = f"""
    CREATE TABLE IF NOT EXISTS {TABLE} (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        date          TEXT    NOT NULL,
        week          TEXT    NOT NULL,
        region        TEXT    NOT NULL,
        store_id      TEXT    NOT NULL,
        category      TEXT    NOT NULL,
        product_name  TEXT    NOT NULL,
        shift         TEXT    NOT NULL,
        units_sold    INTEGER NOT NULL,
        unit_price    REAL    NOT NULL,
        revenue       REAL    NOT NULL,
        cost          REAL    NOT NULL
    );
"""

# Indexes for common analytical access patterns
INDEX_SQLS = [
    f"CREATE INDEX IF NOT EXISTS idx_region_category     ON {TABLE} (region, category);",
    f"CREATE INDEX IF NOT EXISTS idx_week                ON {TABLE} (week);",
    f"CREATE INDEX IF NOT EXISTS idx_date                ON {TABLE} (date);",
    f"CREATE INDEX IF NOT EXISTS idx_region_category_week ON {TABLE} (region, category, week);",
    f"CREATE INDEX IF NOT EXISTS idx_store_id            ON {TABLE} (store_id);",
]


# ---------------------------------------------------------------------------
# Core Loader
# ---------------------------------------------------------------------------
def load_csv_to_sqlite(
    csv_path: str = CSV_PATH,
    db_path: str = DB_PATH,
) -> None:
    """
    Read *csv_path* and insert all rows into the *sales_transactions* table
    inside the SQLite database at *db_path*.  Existing table is replaced.

    Parameters
    ----------
    csv_path : str
        Path to the source CSV file.
    db_path : str
        Path to the target SQLite database file.
    """
    logger.info("🐢 Starting database load: %s → %s", csv_path, db_path)

    # --- Validate source file ---
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source CSV not found: {csv_path}")

    # --- Read CSV ---
    df = pd.read_csv(csv_path)
    logger.info("  Read %s rows from CSV.", f"{len(df):,}")

    # --- Connect to SQLite ---
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Drop and recreate table for idempotent runs
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE};")
        cursor.execute(CREATE_TABLE_SQL)
        logger.info("  Table '%s' created.", TABLE)

        # --- Bulk insert using pandas (fastest for SQLite) ---
        df.to_sql(TABLE, conn, if_exists="append", index=False)
        logger.info("  Inserted %s rows into '%s'.", f"{len(df):,}", TABLE)

        # --- Create indexes ---
        for idx_sql in INDEX_SQLS:
            cursor.execute(idx_sql)
        logger.info("  Created %d indexes.", len(INDEX_SQLS))

        conn.commit()

        # --- Verification ---
        row_count = cursor.execute(f"SELECT COUNT(*) FROM {TABLE};").fetchone()[0]
        logger.info("  ✅ Verification — row count in DB: %s", f"{row_count:,}")

        # Log table schema
        schema = cursor.execute(f"PRAGMA table_info({TABLE});").fetchall()
        logger.info("  Table schema:")
        for col in schema:
            logger.info("    %-3s %-15s %s", col[0], col[1], col[2])

        # Log DB file size
        db_size = os.path.getsize(db_path)
        logger.info("  Database file size: %s bytes", f"{db_size:,}")

    finally:
        conn.close()
        logger.info("  Database connection closed.")


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )
    load_csv_to_sqlite()
