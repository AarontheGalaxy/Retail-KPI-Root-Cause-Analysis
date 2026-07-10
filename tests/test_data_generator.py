"""Tests for src.data_generator — dataset shape, integrity and the injected anomaly."""

import pandas as pd

from src.data_generator import (
    generate_sales_data,
    ANOMALY_REGION,
    ANOMALY_CATEGORY,
    REGIONS,
)

# 14 days x 5 regions x 12 stores x 42 products x 3 shifts = 105,840 rows.
EXPECTED_ROWS = 105_840


def test_row_count_is_105840(sales_df):
    assert len(sales_df) == EXPECTED_ROWS


def test_expected_columns_present(sales_df):
    expected = {
        "date", "week", "region", "store_id", "category",
        "product_name", "shift", "units_sold", "unit_price", "revenue", "cost",
    }
    assert expected == set(sales_df.columns)


def test_no_missing_values(sales_df):
    assert not sales_df.isnull().values.any()


def test_two_weeks_and_all_regions(sales_df):
    assert set(sales_df["week"].unique()) == {"Week_1", "Week_2"}
    assert set(sales_df["region"].unique()) == set(REGIONS)


def test_units_and_revenue_are_positive(sales_df):
    assert (sales_df["units_sold"] >= 1).all()
    assert (sales_df["revenue"] > 0).all()


def test_anomaly_is_in_berlin_vegetables(sales_df):
    """Berlin x Vegetables revenue should drop ~40% from Week_1 to Week_2."""
    segment = sales_df[
        (sales_df["region"] == ANOMALY_REGION)
        & (sales_df["category"] == ANOMALY_CATEGORY)
    ]
    w1 = segment.loc[segment["week"] == "Week_1", "revenue"].sum()
    w2 = segment.loc[segment["week"] == "Week_2", "revenue"].sum()
    drop_pct = (w2 - w1) / w1

    assert -0.50 < drop_pct < -0.30, f"expected ~-40% drop, got {drop_pct:.1%}"


def test_other_segments_are_stable(sales_df):
    """Non-anomalous segments should stay within normal week-over-week bounds."""
    for region in REGIONS:
        for category in sales_df["category"].unique():
            if region == ANOMALY_REGION and category == ANOMALY_CATEGORY:
                continue
            segment = sales_df[
                (sales_df["region"] == region) & (sales_df["category"] == category)
            ]
            w1 = segment.loc[segment["week"] == "Week_1", "revenue"].sum()
            w2 = segment.loc[segment["week"] == "Week_2", "revenue"].sum()
            change = (w2 - w1) / w1
            assert abs(change) < 0.15, f"{region}x{category} moved {change:.1%}"


def test_generation_is_deterministic(tmp_path):
    """Same seed => identical data (reproducible pipeline)."""
    a = generate_sales_data(output_path=str(tmp_path / "a.csv"), seed=7)
    b = generate_sales_data(output_path=str(tmp_path / "b.csv"), seed=7)
    pd.testing.assert_frame_equal(a, b)
