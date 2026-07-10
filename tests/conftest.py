"""
Shared pytest fixtures for the Retail KPI pipeline test-suite.

The heavy dataset (105,840 rows) is generated **once** per test session into a
temporary directory and reused across all tests, so the full pipeline is
exercised end-to-end without touching the real ``data/`` folder.
"""

import os
import sys

import pandas as pd
import pytest

# Make the ``src`` package importable regardless of where pytest is invoked.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generator import generate_sales_data
from src.db_loader import load_csv_to_sqlite
from src.analyzer import run_analysis


@pytest.fixture(scope="session")
def csv_path(tmp_path_factory) -> str:
    """Generate the synthetic sales CSV once and return its path."""
    out = tmp_path_factory.mktemp("data") / "retail_sales.csv"
    generate_sales_data(output_path=str(out), seed=42)
    return str(out)


@pytest.fixture(scope="session")
def sales_df(csv_path) -> pd.DataFrame:
    """The generated sales DataFrame, read back from the CSV."""
    return pd.read_csv(csv_path)


@pytest.fixture(scope="session")
def db_path(tmp_path_factory, csv_path) -> str:
    """Load the CSV into a temporary SQLite database and return its path."""
    db = tmp_path_factory.mktemp("db") / "retail.db"
    load_csv_to_sqlite(csv_path=csv_path, db_path=str(db))
    return str(db)


@pytest.fixture(scope="session")
def analysis_results(db_path) -> dict:
    """Run the full analysis once and share the result dict."""
    return run_analysis(db_path=db_path)
