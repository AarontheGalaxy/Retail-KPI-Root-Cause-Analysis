"""
╔══════════════════════════════════════════════════════════════╗
║  data_generator.py — Mock Retail Sales Data Generator       ║
║  Generates 100k+ rows with an intentional anomaly:          ║
║  Vegetable sales in Berlin drop ~40% in Week 2              ║
║                                                             ║
║  🐢 AarontheGalaxy                                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants — Dimension definitions
# ---------------------------------------------------------------------------
REGIONS = ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"]

CATEGORIES = {
    "Vegetables": ["Tomato", "Cucumber", "Pepper", "Lettuce", "Carrot",
                   "Onion", "Broccoli", "Spinach", "Zucchini", "Eggplant"],
    "Dairy":      ["Milk", "Cheese", "Yogurt", "Butter", "Cream",
                   "Kefir", "Sour Cream", "Cottage Cheese"],
    "Bakery":     ["Bread", "Croissant", "Bagel", "Muffin", "Cake",
                   "Pretzel", "Donut", "Baguette"],
    "Beverages":  ["Water", "Juice", "Soda", "Coffee", "Tea",
                   "Lemonade", "Smoothie", "Iced Tea"],
    "Snacks":     ["Chips", "Chocolate", "Cookies", "Nuts", "Crackers",
                   "Popcorn", "Granola Bar", "Trail Mix"],
}

STORES_PER_REGION = 12         # 5 regions × 12 stores = 60 stores total
DAYS_PER_WEEK     = 7
NUM_WEEKS         = 2          # Week 1 = baseline, Week 2 = current
SHIFTS_PER_DAY    = 3          # Morning, Afternoon, Evening
ANOMALY_REGION    = "Berlin"
ANOMALY_CATEGORY  = "Vegetables"
ANOMALY_DROP_RATE = 0.40       # 40% revenue/units drop

# Base sales parameters (per store per product per day)
BASE_UNITS_MEAN = 50
BASE_UNITS_STD  = 12
UNIT_PRICE_RANGE = {
    "Vegetables": (1.0, 4.0),
    "Dairy":      (1.5, 5.0),
    "Bakery":     (2.0, 6.0),
    "Beverages":  (1.0, 3.5),
    "Snacks":     (1.5, 4.5),
}
COST_MARGIN = 0.35  # cost is ~35% of revenue


# ---------------------------------------------------------------------------
# Core Generator
# ---------------------------------------------------------------------------
def generate_sales_data(
    output_path: str = "data/retail_sales.csv",
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic retail sales DataFrame (100k+ rows) and save as CSV.

    The dataset covers 2 weeks of daily sales across 5 regions, 20 stores,
    and 5 product categories.  An intentional anomaly is injected:
    Berlin × Vegetables revenue/units drop ~40% in Week 2.

    Parameters
    ----------
    output_path : str
        File path for the output CSV.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        The generated sales DataFrame.
    """
    rng = np.random.default_rng(seed)
    logger.info("🐢 Starting retail sales data generation (seed=%d)...", seed)

    # Date range: 14 days total (Week 1 + Week 2)
    start_date = datetime(2026, 2, 23)  # Monday of Week 1
    dates = [start_date + timedelta(days=d) for d in range(DAYS_PER_WEEK * NUM_WEEKS)]
    week1_dates = set(dates[:DAYS_PER_WEEK])

    logger.info("  Date range: %s → %s (%d days)",
                dates[0].strftime("%Y-%m-%d"),
                dates[-1].strftime("%Y-%m-%d"),
                len(dates))

    # Build store IDs per region  (e.g. Berlin_S01 .. Berlin_S04)
    stores_by_region = {}
    for region in REGIONS:
        stores_by_region[region] = [
            f"{region}_S{str(i).zfill(2)}" for i in range(1, STORES_PER_REGION + 1)
        ]

    # Pre-compute product-level unit prices (fixed per product)
    product_prices: dict[str, float] = {}
    for cat, products in CATEGORIES.items():
        lo, hi = UNIT_PRICE_RANGE[cat]
        for product in products:
            product_prices[product] = round(rng.uniform(lo, hi), 2)

    # ------------------------------------------------------------------
    # Generate rows
    # ------------------------------------------------------------------
    rows: list[dict] = []

    shift_names = ["Morning", "Afternoon", "Evening"]

    for date in dates:
        is_week1 = date in week1_dates
        week_label = "Week_1" if is_week1 else "Week_2"

        for region in REGIONS:
            for store_id in stores_by_region[region]:
                for category, products in CATEGORIES.items():
                    for product in products:
                        for shift_idx in range(SHIFTS_PER_DAY):
                            # Base units sold (random normal, clipped to ≥ 1)
                            units = int(max(1, rng.normal(BASE_UNITS_MEAN, BASE_UNITS_STD)))

                            # --- Inject anomaly ---
                            if (not is_week1
                                    and region == ANOMALY_REGION
                                    and category == ANOMALY_CATEGORY):
                                # Reduce units by ~40% (with slight randomness)
                                drop = rng.uniform(
                                    ANOMALY_DROP_RATE - 0.05,
                                    ANOMALY_DROP_RATE + 0.05,
                                )
                                units = int(max(1, units * (1 - drop)))

                            unit_price = product_prices[product]
                            revenue = round(units * unit_price, 2)
                            cost = round(revenue * COST_MARGIN, 2)

                            rows.append({
                                "date":         date.strftime("%Y-%m-%d"),
                                "week":         week_label,
                                "region":       region,
                                "store_id":     store_id,
                                "category":     category,
                                "product_name": product,
                                "shift":        shift_names[shift_idx],
                                "units_sold":   units,
                                "unit_price":   unit_price,
                                "revenue":      revenue,
                                "cost":         cost,
                            })

    df = pd.DataFrame(rows)
    logger.info("  Generated %s rows across %d unique stores.",
                f"{len(df):,}", df["store_id"].nunique())

    # ------------------------------------------------------------------
    # Quick sanity check — log anomaly preview
    # ------------------------------------------------------------------
    anomaly_mask = (
        (df["region"] == ANOMALY_REGION) & (df["category"] == ANOMALY_CATEGORY)
    )
    anomaly_summary = (
        df[anomaly_mask]
        .groupby("week")
        .agg(total_revenue=("revenue", "sum"), total_units=("units_sold", "sum"))
    )
    logger.info("  Anomaly preview (Berlin × Vegetables):\n%s", anomaly_summary.to_string())

    # ------------------------------------------------------------------
    # Save CSV
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("  ✅ CSV saved → %s  (%s bytes)",
                output_path, f"{os.path.getsize(output_path):,}")

    return df


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )
    generate_sales_data()
