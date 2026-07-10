"""Tests for src.db_loader — SQLite load, indexes and idempotency."""

import sqlite3

import pytest

from src.db_loader import load_csv_to_sqlite, TABLE


def _row_count(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {TABLE};").fetchone()[0]
    finally:
        conn.close()


def test_all_rows_loaded(db_path, sales_df):
    assert _row_count(db_path) == len(sales_df)


def test_indexes_created(db_path):
    conn = sqlite3.connect(db_path)
    try:
        idx = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?;",
            (TABLE,),
        ).fetchall()
    finally:
        conn.close()
    names = {row[0] for row in idx}
    assert "idx_region_category_week" in names
    assert "idx_week" in names


def test_load_is_idempotent(csv_path, tmp_path):
    """Loading the same CSV twice must not duplicate rows (DROP + recreate)."""
    db = str(tmp_path / "idem.db")
    load_csv_to_sqlite(csv_path=csv_path, db_path=db)
    first = _row_count(db)
    load_csv_to_sqlite(csv_path=csv_path, db_path=db)
    second = _row_count(db)
    assert first == second


def test_missing_csv_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv_to_sqlite(
            csv_path=str(tmp_path / "does_not_exist.csv"),
            db_path=str(tmp_path / "x.db"),
        )
