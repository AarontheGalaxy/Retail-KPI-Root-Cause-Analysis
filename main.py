"""
╔══════════════════════════════════════════════════════════════╗
║  main.py — Retail KPI Root-Cause Analysis Pipeline          ║
║  Orchestrates: Generate → Load → Analyse → Report           ║
║                                                             ║
║  🐢 AarontheGalaxy                                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import logging

from src.data_generator import generate_sales_data
from src.db_loader import load_csv_to_sqlite
from src.analyzer import run_analysis, generate_report

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("pipeline")


# ---------------------------------------------------------------------------
# Pipeline Phases
# ---------------------------------------------------------------------------
PHASES = [
    ("Phase 1 — Data Generation", lambda: generate_sales_data()),
    ("Phase 2 — Database Setup",  lambda: load_csv_to_sqlite()),
    ("Phase 3 — SQL Analysis",    lambda: run_analysis()),
    ("Phase 4 — Report Generation", None),   # handled specially
]


def run_pipeline() -> None:
    """Execute the full 4-phase pipeline with timing for each step."""

    logger.info("=" * 65)
    logger.info("🐢  RETAIL KPI ROOT-CAUSE ANALYSIS PIPELINE")
    logger.info("=" * 65)

    total_start = time.perf_counter()
    analysis_results = None

    for idx, (name, func) in enumerate(PHASES, 1):
        logger.info("-" * 65)
        logger.info("  [%d/%d] %s", idx, len(PHASES), name)
        logger.info("-" * 65)

        phase_start = time.perf_counter()

        if func is not None:
            result = func()
            if name.startswith("Phase 3"):
                analysis_results = result
        else:
            # Phase 4 needs the analysis results
            if analysis_results is None:
                raise RuntimeError("Phase 4 requires Phase 3 results.")
            generate_report(analysis_results)

        elapsed = time.perf_counter() - phase_start
        logger.info("  ⏱  %s completed in %.2f seconds.", name, elapsed)

    total_elapsed = time.perf_counter() - total_start
    logger.info("=" * 65)
    logger.info("🐢  PIPELINE COMPLETE — Total time: %.2f seconds", total_elapsed)
    logger.info("=" * 65)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_pipeline()
