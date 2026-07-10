# Retail KPI Root-Cause Analysis Pipeline

[![CI](https://github.com/AarontheGalaxy/Retail-KPI-Root-Cause-Analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/AarontheGalaxy/Retail-KPI-Root-Cause-Analysis/actions/workflows/ci.yml)

## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Context](#business-context)
3. [System Architecture and Repository Structure](#system-architecture-and-repository-structure)
4. [Pipeline Phases](#pipeline-phases)
   - [Phase 1 -- Data Generation](#phase-1----data-generation)
   - [Phase 2 -- Database Setup](#phase-2----database-setup)
   - [Phase 3 -- SQL Analysis](#phase-3----sql-analysis)
   - [Phase 4 -- Reporting](#phase-4----reporting)
5. [Key Findings (Execution Results)](#key-findings-execution-results)
6. [Installation and Prerequisites](#installation-and-prerequisites)
7. [Usage](#usage)
8. [Technical Stack](#technical-stack)

---

## Project Overview

This project implements a modular, end-to-end data pipeline engineered to detect, diagnose, and report the root cause of key performance indicator (KPI) declines within a large-scale retail dataset. The pipeline processes over 100,000 transactional records, loads them into a relational database, applies optimized SQL-based analytical queries, and produces a formal executive-summary report in Markdown format.

The system is designed with separation of concerns in mind: each phase of the pipeline is encapsulated within its own module, enabling independent testing, maintenance, and future migration to cloud-based data warehousing platforms such as Google BigQuery. All phases execute sequentially through a central orchestrator (`main.py`) with structured logging and per-phase performance measurement.

The pipeline was validated end-to-end with a total execution time of approximately 0.87 seconds across all four phases.

---

## Business Context

Large retail chains operating across multiple geographic regions face a persistent challenge: identifying the precise origin of sudden drops in sales performance. When a KPI such as weekly revenue or units sold experiences a significant decline, the underlying cause may stem from any combination of regional distribution failures, category-specific supply shortages, individual store operational issues, or product-level quality concerns.

This problem is especially acute for **perishable goods** (e.g., vegetables, dairy), where supply chain disruptions have an immediate and measurable impact on shelf availability and, consequently, on revenue. Unlike durable goods, perishable products cannot be back-ordered or stockpiled to compensate for delivery failures, making early detection of supply chain bottlenecks critical for revenue protection.

### The Root-Cause Analysis Challenge

Traditional dashboards surface *what* dropped, but rarely answer *why*. The analytical approach implemented in this pipeline follows a structured drill-down methodology:

1. **Detection** -- Identify which region-by-category segments experienced statistically significant week-over-week revenue declines.
2. **Isolation** -- Determine whether the decline is concentrated in specific stores (indicating a local operational issue) or distributed uniformly across all stores in the region (indicating a systemic supply chain problem).
3. **Granularity** -- Examine individual products within the affected category to confirm whether the decline is product-specific (suggesting a recall or quality issue) or category-wide (suggesting a distributor or logistics failure).

This layered approach allows supply chain managers and regional directors to act on precise, evidence-based findings rather than relying on aggregate metrics that obscure the true point of failure.

---

## System Architecture and Repository Structure

The project adheres to a modular architecture where each pipeline phase is implemented as an independent Python module within the `src/` package. Data artifacts (CSV exports and the SQLite database) are written to the `data/` directory, and generated reports are written to `reports/`. The orchestrator (`main.py`) resides at the project root and imports all modules through the `src` package namespace.

```
Retail KPI Root-Cause Analysis/
|
|-- main.py                         # Pipeline orchestrator (sequential phase execution)
|-- requirements.txt                # Python dependency manifest
|
|-- src/
|   |-- __init__.py                 # Package initializer
|   |-- data_generator.py           # Phase 1: Synthetic data generation with anomaly injection
|   |-- db_loader.py                # Phase 2: CSV-to-SQLite ingestion with schema and indexing
|   |-- analyzer.py                 # Phase 3 & 4: SQL-based analysis engine and report generator
|
|-- data/
|   |-- retail_sales.csv            # Generated dataset (105,840 rows, ~8.8 MB)
|   |-- retail.db                   # SQLite database (~22 MB, indexed)
|
|-- reports/
|   |-- root_cause_analysis.md      # Generated executive summary report
```

### Design Principles

- **Modularity**: Each module exposes a single public function (`generate_sales_data`, `load_csv_to_sqlite`, `run_analysis`, `generate_report`) with default parameters that match the project conventions. Modules can be executed independently via `python -m src.<module>` or imported by the orchestrator.
- **Idempotency**: Every pipeline run produces identical results given the same random seed. The database loader drops and recreates the target table on each execution, ensuring no duplicate data accumulates.
- **Observability**: All modules utilise the Python `logging` standard library with a consistent format (`timestamp | level | module | message`), providing full traceability of each pipeline step.
- **Portability**: The database layer uses the `sqlite3` standard library module. The schema and query patterns are written in ANSI-compatible SQL, facilitating future migration to enterprise database systems.

---

## Pipeline Phases

### Phase 1 -- Data Generation

**Module**: `src/data_generator.py`
**Output**: `data/retail_sales.csv`

This module generates a synthetic retail sales dataset comprising 105,840 transaction records. The data simulates daily point-of-sale transactions for a supermarket chain operating across five German metropolitan regions.

#### Data Dimensions

| Dimension         | Values                                           | Cardinality |
|-------------------|--------------------------------------------------|-------------|
| Date Range        | 2026-02-23 through 2026-03-08 (14 days)          | 14          |
| Weeks             | Week_1 (baseline), Week_2 (current)              | 2           |
| Regions           | Berlin, Munich, Hamburg, Frankfurt, Cologne       | 5           |
| Stores per Region | 12 (named `<Region>_S01` through `<Region>_S12`) | 60 total    |
| Categories        | Vegetables, Dairy, Bakery, Beverages, Snacks      | 5           |
| Products          | 8-10 per category (42 unique products)            | 42          |
| Shifts per Day    | Morning, Afternoon, Evening                       | 3           |

**Row count derivation**: 14 days x 5 regions x 12 stores x 42 products x 3 shifts = **105,840 rows**.

#### Schema

| Column         | Type    | Description                                     |
|----------------|---------|-------------------------------------------------|
| `date`         | TEXT    | Transaction date in ISO 8601 format (YYYY-MM-DD)|
| `week`         | TEXT    | Week label (`Week_1` or `Week_2`)               |
| `region`       | TEXT    | Geographic region of the store                  |
| `store_id`     | TEXT    | Unique store identifier                         |
| `category`     | TEXT    | Product category                                |
| `product_name` | TEXT    | Individual product name                         |
| `shift`        | TEXT    | Intra-day shift (Morning, Afternoon, Evening)   |
| `units_sold`   | INTEGER | Number of units sold in the transaction         |
| `unit_price`   | REAL    | Price per unit (fixed per product, varies by category range) |
| `revenue`      | REAL    | Calculated as `units_sold * unit_price`          |
| `cost`         | REAL    | Calculated as `revenue * 0.35` (35% cost margin)|

#### Anomaly Injection

The module injects a deliberate anomaly into the dataset to simulate a supply chain disruption. During Week 2, all transactions matching the segment **Berlin x Vegetables** have their `units_sold` values reduced by approximately 40% (uniformly sampled from the range 35%-45%). This reduction propagates directly to `revenue` and `cost` columns.

The anomaly is designed to be:

- **Regional**: Only the Berlin region is affected; Munich, Hamburg, Frankfurt, and Cologne operate at normal levels.
- **Category-specific**: Only the Vegetables category is affected; Dairy, Bakery, Beverages, and Snacks in Berlin remain at baseline.
- **Uniform across stores**: All 12 Berlin stores experience the drop equally, ruling out store-specific causes during analysis.
- **Uniform across products**: All 10 vegetable products (Tomato, Cucumber, Pepper, Lettuce, Carrot, Onion, Broccoli, Spinach, Zucchini, Eggplant) are affected, ruling out product-specific causes.

**Reproducibility**: The generator uses `numpy.random.default_rng(seed=42)` for deterministic output.

---

### Phase 2 -- Database Setup

**Module**: `src/db_loader.py`
**Input**: `data/retail_sales.csv`
**Output**: `data/retail.db`

This module reads the generated CSV file using Pandas and loads all rows into a SQLite database. The table is dropped and recreated on each execution to ensure idempotent pipeline runs.

#### Table Schema

The `sales_transactions` table is created with the following DDL:

```sql
CREATE TABLE IF NOT EXISTS sales_transactions (
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
```

#### Index Strategy

Five indexes are created to optimise the analytical query patterns used in Phase 3:

| Index Name                    | Columns                     | Purpose                                                |
|-------------------------------|-----------------------------|--------------------------------------------------------|
| `idx_region_category`         | `(region, category)`        | Accelerates region-by-category GROUP BY aggregations    |
| `idx_week`                    | `(week)`                    | Optimises week-level filtering in CASE expressions      |
| `idx_date`                    | `(date)`                    | Supports date-range queries for future extensions        |
| `idx_region_category_week`    | `(region, category, week)`  | Covers the full predicate of the drill-down queries     |
| `idx_store_id`                | `(store_id)`                | Accelerates store-level drill-down queries              |

#### Verification

After insertion, the loader executes a `SELECT COUNT(*)` verification query and logs the result alongside the full table schema (via `PRAGMA table_info`) and the database file size.

---

### Phase 3 -- SQL Analysis

**Module**: `src/analyzer.py` (function: `run_analysis`)
**Input**: `data/retail.db`
**Output**: Dictionary of Pandas DataFrames containing analysis results

This module connects to the SQLite database and executes five optimised SQL queries that progressively drill down from a high-level KPI overview to the specific root cause of the detected anomaly.

#### Query 1 -- Overall KPI Snapshot

Aggregates total revenue, total units sold, and transaction count per week. Provides the baseline comparison for portfolio-level performance.

```sql
SELECT
    week,
    SUM(revenue)    AS total_revenue,
    SUM(units_sold) AS total_units,
    COUNT(*)        AS transaction_count
FROM
    sales_transactions
GROUP BY
    week
ORDER BY
    week;
```

#### Query 2 -- Weekly KPI Summary by Region and Category

Uses conditional aggregation with `CASE` expressions to pivot Week_1 and Week_2 metrics into separate columns within a single pass over the data, avoiding the overhead of self-joins.

```sql
SELECT
    region,
    category,
    SUM(CASE WHEN week = 'Week_1' THEN revenue ELSE 0 END)    AS week1_revenue,
    SUM(CASE WHEN week = 'Week_2' THEN revenue ELSE 0 END)    AS week2_revenue,
    SUM(CASE WHEN week = 'Week_1' THEN units_sold ELSE 0 END) AS week1_units,
    SUM(CASE WHEN week = 'Week_2' THEN units_sold ELSE 0 END) AS week2_units
FROM
    sales_transactions
GROUP BY
    region, category
ORDER BY
    region, category;
```

#### Query 3 -- Week-over-Week Percentage Change with Ranking

Builds upon Query 2 using a Common Table Expression (CTE) to compute the percentage change in revenue and units for each region-category segment. The `RANK()` window function assigns a ranking based on the severity of the revenue decline, with the worst-performing segment ranked first.

```sql
WITH weekly_kpi AS (
    SELECT
        region, category,
        SUM(CASE WHEN week = 'Week_1' THEN revenue ELSE 0 END)    AS w1_revenue,
        SUM(CASE WHEN week = 'Week_2' THEN revenue ELSE 0 END)    AS w2_revenue,
        SUM(CASE WHEN week = 'Week_1' THEN units_sold ELSE 0 END) AS w1_units,
        SUM(CASE WHEN week = 'Week_2' THEN units_sold ELSE 0 END) AS w2_units
    FROM sales_transactions
    GROUP BY region, category
)
SELECT
    region, category,
    w1_revenue, w2_revenue,
    ROUND((w2_revenue - w1_revenue) * 100.0 / w1_revenue, 2) AS revenue_pct_change,
    w1_units, w2_units,
    ROUND((w2_units - w1_units) * 100.0 / w1_units, 2)       AS units_pct_change,
    RANK() OVER (
        ORDER BY (w2_revenue - w1_revenue) * 100.0 / w1_revenue ASC
    ) AS drop_rank
FROM weekly_kpi
ORDER BY revenue_pct_change ASC;
```

#### Query 4 -- Store-Level Drill-Down

For the segment identified as having the largest revenue decline (Rank 1), this parameterised query breaks down the week-over-week change at the individual store level. This establishes whether the decline is localised to specific stores or uniformly distributed across the region.

```sql
WITH store_kpi AS (
    SELECT
        store_id,
        SUM(CASE WHEN week = 'Week_1' THEN revenue ELSE 0 END) AS w1_revenue,
        SUM(CASE WHEN week = 'Week_2' THEN revenue ELSE 0 END) AS w2_revenue,
        SUM(CASE WHEN week = 'Week_1' THEN units_sold ELSE 0 END) AS w1_units,
        SUM(CASE WHEN week = 'Week_2' THEN units_sold ELSE 0 END) AS w2_units
    FROM sales_transactions
    WHERE region = ? AND category = ?
    GROUP BY store_id
)
SELECT
    store_id, w1_revenue, w2_revenue,
    ROUND((w2_revenue - w1_revenue) * 100.0 / w1_revenue, 2) AS revenue_pct_change,
    w1_units, w2_units,
    ROUND((w2_units - w1_units) * 100.0 / w1_units, 2) AS units_pct_change
FROM store_kpi
ORDER BY revenue_pct_change ASC;
```

#### Query 5 -- Product-Level Drill-Down

Analogous to the store-level drill-down, this query examines individual products within the affected segment to confirm whether the decline is product-specific or spans the entire category.

```sql
WITH product_kpi AS (
    SELECT
        product_name,
        SUM(CASE WHEN week = 'Week_1' THEN revenue ELSE 0 END) AS w1_revenue,
        SUM(CASE WHEN week = 'Week_2' THEN revenue ELSE 0 END) AS w2_revenue,
        SUM(CASE WHEN week = 'Week_1' THEN units_sold ELSE 0 END) AS w1_units,
        SUM(CASE WHEN week = 'Week_2' THEN units_sold ELSE 0 END) AS w2_units
    FROM sales_transactions
    WHERE region = ? AND category = ?
    GROUP BY product_name
)
SELECT
    product_name, w1_revenue, w2_revenue,
    ROUND((w2_revenue - w1_revenue) * 100.0 / w1_revenue, 2) AS revenue_pct_change,
    w1_units, w2_units,
    ROUND((w2_units - w1_units) * 100.0 / w1_units, 2) AS units_pct_change
FROM product_kpi
ORDER BY revenue_pct_change ASC;
```

---

### Phase 4 -- Reporting

**Module**: `src/analyzer.py` (function: `generate_report`)
**Input**: Analysis results dictionary from Phase 3
**Output**: `reports/root_cause_analysis.md`

The report generator transforms the analysis DataFrames into a structured Markdown document containing the following sections:

1. **Executive Summary** -- A concise statement of the detected anomaly, its magnitude, and the inferred root cause.
2. **Overall KPI Snapshot** -- A table comparing total revenue, units, and transaction counts between Week 1 and Week 2.
3. **Week-over-Week Change Table** -- All 25 region-by-category segments ranked by revenue percentage change.
4. **Store-Level Drill-Down** -- Per-store performance within the anomalous segment.
5. **Product-Level Drill-Down** -- Per-product performance within the anomalous segment.
6. **Conclusion and Recommendations** -- Actionable recommendations for supply chain investigation, supplier diversification, and automated alerting thresholds.

DataFrames are converted to Markdown table syntax via a utility function (`_df_to_md_table`) that generates properly formatted headers, separators, and row data.

---

## Key Findings (Execution Results)

### Portfolio-Level Overview

| Metric             | Week 1        | Week 2        | Change   |
|--------------------|---------------|---------------|----------|
| Total Revenue      | 8,194,800.45  | 8,037,025.19  | -1.93%   |
| Total Units Sold   | 2,619,902     | 2,563,159     | -2.17%   |
| Transaction Count  | 52,920        | 52,920        | 0.00%    |

### Anomaly Identification

Out of 25 region-by-category segments analysed, only **one** exhibited a statistically significant decline:

| Rank | Region | Category   | Revenue Change | Units Change |
|------|--------|------------|----------------|--------------|
| 1    | Berlin | Vegetables | **-41.19%**    | -41.32%      |
| 2    | Hamburg| Beverages  | -1.04%         | -1.32%       |
| 3    | Berlin | Bakery     | -0.94%         | -0.78%       |

All segments other than Berlin x Vegetables fluctuated within a narrow band of approximately -1.04% to +1.91%, representing normal stochastic variation.

### Store-Level Confirmation

All 12 stores in the Berlin region exhibited a uniform revenue decline ranging from -39.36% to -43.88%, with no statistical outliers. This uniform distribution across all stores eliminates store-specific operational failures as a possible cause.

### Product-Level Confirmation

All 10 vegetable products showed consistent declines ranging from -39.50% (Pepper) to -43.90% (Carrot). The absence of product-level outliers eliminates single-product recalls, quality defects, or pricing errors as possible causes.

### Root Cause Determination

The combination of:

- A single affected region (Berlin) with four unaffected regions,
- A single affected category (Vegetables) with four unaffected categories in the same region,
- Uniform impact across all 12 stores and all 10 products,

points conclusively to a **regional supply chain bottleneck** -- specifically, a failure at the distribution centre or logistics tier responsible for delivering vegetable products to the Berlin metropolitan area during Week 2.

---

## Installation and Prerequisites

### System Requirements

- Python 3.10 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone or download the repository to a local directory.

2. Navigate to the project root directory:

   ```bash
   cd "Retail KPI Root-Cause Analysis"
   ```

3. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   # venv\Scripts\activate         # Windows
   ```

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   This installs the following dependencies:
   - `pandas` -- DataFrame manipulation and CSV I/O
   - `numpy` -- Numerical random generation and array operations

   Note: `sqlite3` is included in the Python standard library and does not require separate installation.

---

## Usage

### Full Pipeline Execution

Execute all four phases sequentially by running the orchestrator:

```bash
python main.py
```

This will:

1. Generate `data/retail_sales.csv` (105,840 rows of synthetic sales data).
2. Create `data/retail.db` (SQLite database with indexes).
3. Run five analytical SQL queries and identify the root cause.
4. Generate `reports/root_cause_analysis.md` (executive summary report).

All operations are logged to standard output with timestamps, log levels, and module identifiers.

### Individual Module Execution

Each module can be executed independently for development or debugging purposes:

```bash
# Phase 1 only -- generate the CSV
python -m src.data_generator

# Phase 2 only -- load CSV into SQLite
python -m src.db_loader

# Phase 3 and 4 -- run analysis and generate report
python -m src.analyzer
```

### Expected Output

A successful pipeline execution produces log output following this structure:

```
RETAIL KPI ROOT-CAUSE ANALYSIS PIPELINE
=================================================================
  [1/4] Phase 1 -- Data Generation
  Generated 105,840 rows across 60 unique stores.
  CSV saved -> data/retail_sales.csv
  Phase 1 completed in 0.44 seconds.
-----------------------------------------------------------------
  [2/4] Phase 2 -- Database Setup
  Inserted 105,840 rows into 'sales_transactions'.
  Created 5 indexes.
  Verification -- row count in DB: 105,840
  Phase 2 completed in 0.37 seconds.
-----------------------------------------------------------------
  [3/4] Phase 3 -- SQL Analysis
  Anomaly detected -> Region: Berlin | Category: Vegetables | Revenue Change: -41.19%
  Phase 3 completed in 0.05 seconds.
-----------------------------------------------------------------
  [4/4] Phase 4 -- Report Generation
  Report saved -> reports/root_cause_analysis.md
  Phase 4 completed in 0.00 seconds.
=================================================================
  PIPELINE COMPLETE -- Total time: 0.87 seconds
=================================================================
```

---

## Technical Stack

| Component            | Technology                                                                                  |
|----------------------|---------------------------------------------------------------------------------------------|
| Programming Language | Python 3.10+                                                                                |
| Database             | SQLite 3 (via Python `sqlite3` standard library module)                                     |
| Data Processing      | Pandas (DataFrame operations, CSV I/O, SQL query result handling)                           |
| Numerical Computing  | NumPy (random number generation with `default_rng`, normal distribution sampling)           |
| SQL Techniques       | Common Table Expressions (CTEs), Conditional Aggregation (CASE), Window Functions (RANK())  |
| Query Optimisation   | Composite B-tree indexes on high-cardinality filter and grouping columns                    |
| Reporting Format     | Markdown (programmatically generated tables and narrative text)                              |
| Logging              | Python `logging` standard library with structured format strings                            |
| Orchestration        | Sequential phase execution with `time.perf_counter()` performance measurement               |

---

*Retail KPI Root-Cause Analysis Pipeline -- Technical Documentation*
