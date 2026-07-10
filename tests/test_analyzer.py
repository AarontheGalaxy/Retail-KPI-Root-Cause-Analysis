"""Tests for src.analyzer — root-cause detection and report generation."""

import pytest

from src.analyzer import run_analysis, generate_report


def test_analysis_result_keys(analysis_results):
    expected = {
        "overall_kpi", "weekly_summary", "wow_change",
        "store_drilldown", "product_drilldown", "anomaly_segment",
    }
    assert expected == set(analysis_results.keys())


def test_worst_segment_is_berlin_vegetables(analysis_results):
    anomaly = analysis_results["anomaly_segment"]
    assert anomaly["region"] == "Berlin"
    assert anomaly["category"] == "Vegetables"
    # The flagged segment must show a material revenue drop.
    assert anomaly["revenue_pct_change"] < -20.0


def test_wow_change_ranks_berlin_first(analysis_results):
    """The worst drop (drop_rank == 1) must be the Berlin x Vegetables row."""
    df = analysis_results["wow_change"]
    top = df.sort_values("revenue_pct_change").iloc[0]
    assert top["region"] == "Berlin"
    assert top["category"] == "Vegetables"


def test_store_drilldown_covers_all_berlin_stores(analysis_results):
    """Every Berlin store should appear and be affected (regional, not per-store)."""
    df = analysis_results["store_drilldown"]
    assert len(df) == 12
    assert (df["revenue_pct_change"] < 0).all()


def test_generate_report_writes_file(analysis_results, tmp_path):
    out = tmp_path / "report.md"
    content = generate_report(analysis_results, output_path=str(out))
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Berlin" in text
    assert "Vegetables" in text
    assert "105,840" in text
    assert content == text


def test_run_analysis_missing_db_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_analysis(db_path=str(tmp_path / "nope.db"))
