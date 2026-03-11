# 🐢 Root Cause Analysis Report — Retail KPI Drop

> **Generated:** 2026-03-09 17:37
> **Database:** `data/retail.db` | **Records analysed:** 105,840

---

## 1. Executive Summary

A significant **week-over-week revenue decline** has been detected. While the
overall portfolio showed a **-1.93%** change in total revenue, the
segment **Berlin × Vegetables** experienced a dramatic
**-41.19%** revenue drop — far exceeding the normal
variation across other region-category combinations.

**Root cause:** Supply chain bottleneck preventing vegetables
products from reaching the **Berlin** region, resulting in a uniform
~40% reduction across all stores and products within that segment.

---

## 2. Overall KPI Snapshot

| week | total_revenue | total_units | transaction_count |
| --- | --- | --- | --- |
| Week_1 | 8194800.45 | 2619902 | 52920 |
| Week_2 | 8037025.19 | 2563159 | 52920 |

---

## 3. Week-over-Week Change by Region × Category

The table below ranks all region × category segments by revenue percentage
change (ascending — worst performers first):

| region | category | w1_revenue | w2_revenue | revenue_pct_change | w1_units | w2_units | units_pct_change | drop_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Berlin | Vegetables | 346260.47 | 203646.14 | -41.19 | 124245 | 72907 | -41.32 | 1 |
| Hamburg | Beverages | 217728.43 | 215467.52 | -1.04 | 100125 | 98802 | -1.32 | 2 |
| Berlin | Bakery | 468761.17 | 464355.36 | -0.94 | 99556 | 98780 | -0.78 | 3 |
| Cologne | Dairy | 329285.27 | 326191.56 | -0.94 | 100502 | 99967 | -0.53 | 4 |
| Munich | Snacks | 280803.1 | 278179.92 | -0.93 | 100663 | 99471 | -1.18 | 5 |
| Munich | Vegetables | 348234.16 | 345330.88 | -0.83 | 124845 | 123952 | -0.72 | 6 |
| Frankfurt | Vegetables | 348375.65 | 346185.34 | -0.63 | 124902 | 124022 | -0.7 | 7 |
| Frankfurt | Snacks | 278809.45 | 277190.92 | -0.58 | 99894 | 99520 | -0.37 | 8 |
| Cologne | Snacks | 278572.37 | 277086.94 | -0.53 | 99932 | 99360 | -0.57 | 9 |
| Frankfurt | Bakery | 468480.25 | 466782.52 | -0.36 | 99813 | 99131 | -0.68 | 10 |
| Munich | Dairy | 325818.19 | 324710.96 | -0.34 | 99730 | 99501 | -0.23 | 11 |
| Cologne | Bakery | 471802.1 | 470216.39 | -0.34 | 100385 | 99941 | -0.44 | 12 |
| Hamburg | Bakery | 468119.71 | 466624.78 | -0.32 | 99383 | 99264 | -0.12 | 13 |
| Cologne | Beverages | 217580.72 | 216956.7 | -0.29 | 100077 | 99903 | -0.17 | 14 |
| Berlin | Dairy | 326139.09 | 325588.62 | -0.17 | 99741 | 99148 | -0.59 | 15 |
| Munich | Beverages | 216175.99 | 215832.5 | -0.16 | 99562 | 99198 | -0.37 | 16 |
| Hamburg | Vegetables | 348797.4 | 348826.14 | 0.01 | 125057 | 125254 | 0.16 | 17 |
| Hamburg | Dairy | 325711.52 | 325949.0 | 0.07 | 99273 | 99494 | 0.22 | 18 |
| Cologne | Vegetables | 348000.03 | 348280.22 | 0.08 | 124777 | 124842 | 0.05 | 19 |
| Berlin | Snacks | 276406.6 | 277144.27 | 0.27 | 99388 | 99620 | 0.23 | 20 |
| Berlin | Beverages | 216124.2 | 216943.36 | 0.38 | 99599 | 99836 | 0.24 | 21 |
| Munich | Bakery | 468759.6 | 471022.59 | 0.48 | 99674 | 100048 | 0.38 | 22 |
| Frankfurt | Dairy | 327109.2 | 329066.03 | 0.6 | 99938 | 100606 | 0.67 | 23 |
| Hamburg | Snacks | 276966.1 | 279336.49 | 0.86 | 99318 | 99974 | 0.66 | 24 |
| Frankfurt | Beverages | 215979.68 | 220110.04 | 1.91 | 99523 | 100618 | 1.1 | 25 |

> **Key finding:** Only **Berlin × Vegetables** shows a
> material drop (-41.19%). All other segments fluctuate
> within normal bounds.

---

## 4. Store-Level Drill-Down (Berlin × Vegetables)

Breaking down the anomalous segment by individual store reveals that **every
store** in the region is equally affected, confirming a *regional* supply issue
rather than a store-specific problem.

| store_id | w1_revenue | w2_revenue | revenue_pct_change | w1_units | w2_units | units_pct_change |
| --- | --- | --- | --- | --- | --- | --- |
| Berlin_S05 | 30295.13 | 17000.47 | -43.88 | 10711 | 6145 | -42.63 |
| Berlin_S09 | 28964.38 | 16573.43 | -42.78 | 10406 | 5936 | -42.96 |
| Berlin_S03 | 29472.71 | 16915.87 | -42.6 | 10449 | 6070 | -41.91 |
| Berlin_S12 | 28246.7 | 16555.21 | -41.39 | 10258 | 5940 | -42.09 |
| Berlin_S01 | 29277.37 | 17175.87 | -41.33 | 10556 | 6155 | -41.69 |
| Berlin_S08 | 28740.7 | 17028.93 | -40.75 | 10292 | 6102 | -40.71 |
| Berlin_S02 | 28644.53 | 17021.45 | -40.58 | 10282 | 6043 | -41.23 |
| Berlin_S06 | 28715.51 | 17068.53 | -40.56 | 10286 | 6099 | -40.71 |
| Berlin_S11 | 28174.69 | 16809.19 | -40.34 | 10120 | 6020 | -40.51 |
| Berlin_S10 | 28658.19 | 17124.52 | -40.25 | 10386 | 6111 | -41.16 |
| Berlin_S07 | 28636.21 | 17130.14 | -40.18 | 10278 | 6140 | -40.26 |
| Berlin_S04 | 28434.35 | 17242.53 | -39.36 | 10221 | 6146 | -39.87 |

---

## 5. Product-Level Drill-Down (Berlin × Vegetables)

All products within the affected category show a consistent drop, ruling out
a single-product recall or quality issue.

| product_name | w1_revenue | w2_revenue | revenue_pct_change | w1_units | w2_units | units_pct_change |
| --- | --- | --- | --- | --- | --- | --- |
| Carrot | 15950.08 | 8947.2 | -43.9 | 12461 | 6990 | -43.9 |
| Broccoli | 41167.28 | 23563.52 | -42.76 | 12551 | 7184 | -42.76 |
| Lettuce | 38365.44 | 22427.22 | -41.54 | 12416 | 7258 | -41.54 |
| Tomato | 41440.24 | 24275.84 | -41.42 | 12482 | 7312 | -41.42 |
| Eggplant | 28712.3 | 16847.15 | -41.32 | 12218 | 7169 | -41.32 |
| Onion | 48743.79 | 28685.07 | -41.15 | 12403 | 7299 | -41.15 |
| Cucumber | 28661.28 | 17007.92 | -40.66 | 12354 | 7331 | -40.66 |
| Zucchini | 17445.96 | 10383.12 | -40.48 | 12642 | 7524 | -40.48 |
| Spinach | 41485.92 | 24712.8 | -40.43 | 12347 | 7355 | -40.43 |
| Pepper | 44288.18 | 26796.3 | -39.5 | 12371 | 7485 | -39.5 |

---

## 6. Conclusion & Recommendations

| # | Recommendation |
| --- | --- |
| 1 | **Investigate the supply chain** for vegetables products in Berlin. The uniform drop across all stores and products points to a distribution-centre or logistics bottleneck. |
| 2 | **Contact regional suppliers** to confirm whether shipment delays or stock shortages occurred during Week 2. |
| 3 | **Set up automated alerting** on the `revenue_pct_change` metric so that future drops exceeding -20.0% are flagged within 24 hours. |
| 4 | **Diversify suppliers** for the Berlin region to reduce single-point-of-failure risk in perishable goods logistics. |

---

*Report generated by the Retail KPI Root-Cause Analysis Pipeline 🐢*
