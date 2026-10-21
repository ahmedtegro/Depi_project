# Retail Demand & Sales Intelligence: Business Report

## 1. Problem and objective

The retailer has historical sales data but struggles to understand which products, locations and periods drive revenue, and how future demand may change. This project builds a sales intelligence platform that combines historical analysis with predictive modeling: a relational database, an exploratory analysis, a demand regression model, and an interactive dashboard.

## 2. Data

| Item | Value |
|---|---|
| Rows | 76,000 (one row per store, product and day) |
| Period | 2022-01-01 to 2024-01-30 |
| Stores / Regions / Categories / Products | 5 / 4 / 5 / 20 |
| Missing values / duplicate rows | 0 / 0 |

Revenue is calculated after discount: `units_sold x price x (1 - discount / 100)`. Total revenue is about 412.6 million over 6.75 million units sold.

Outliers (IQR rule) are 1.9% of `units_sold`, 1.3% of `demand` and 3.6% of `inventory_level`. They were kept because they reflect real high-demand days (promotions, good weather) rather than errors.

## 3. Key findings

### Where the revenue comes from

| Category | Revenue (M) | Avg units per row |
|---|---|---|
| Groceries | 153.0 | 102.9 |
| Furniture | 100.9 | 64.4 |
| Clothing | 77.3 | 94.6 |
| Electronics | 59.8 | 83.0 |
| Toys | 21.7 | 78.4 |

- Furniture sells the fewest units but ranks second in revenue because of its high price.
- North generates the most revenue (154.1M) only because it has two stores (S001 and S005). Per store, S003 (East) leads with 89.3M and S005 (North) is lowest with 72.6M.
- Best products: P0014 (33.5M), P0011 (30.4M), P0009 (29.5M). Weakest: P0001 (12.7M), P0007 (13.0M), P0002 (14.9M).
- Revenue was 201.2M in 2022 and 196.1M in 2023 (-2.5%). January 2024 is the only 2024 month in the data.

### Time, season and weather

- Monthly revenue is volatile: the peak is August 2022 (20.0M) and the lowest month is February 2023 (9.8M). The drops line up with epidemic periods, for example February 2023 was 100% epidemic rows.
- Summer has the highest average units sold (95.8) and Spring the lowest (83.5).
- Sunny weather averages 97.0 units per row; rainy and snowy weather average 82.0 and 80.9, about 15-17% lower.

### Epidemic periods (the strongest effect)

Epidemic rows are 20% of the data. Average units sold fall from 95.8 to 60.9 (-36%) and average demand from 112.9 to 70.2. Average inventory also falls from 312 to 257.

### Promotions and discounts

| Discount | Avg units sold | Avg revenue per row |
|---|---|---|
| 0% | 81.6 | 5,912 |
| 5% | 81.7 | 5,285 |
| 10% | 87.7 | 5,298 |
| 15% | 102.9 | 5,926 |
| 20% | 103.8 | 5,302 |
| 25% | 103.6 | 4,605 |

- Promotions raise average units sold from 81.8 to 103.1 (+26%) and average revenue per row from 5,335 to 5,620 (+5%).
- Discounts only lift volume once they reach 15%. Beyond 15% there is no extra volume, and at 25% revenue per row drops sharply. Deeper discounts give away margin without selling more.
- Price has almost no relationship with units sold (correlation -0.01). Our price and the competitor price move together (0.98).

### Unmet demand

Units sold are below demand in about 70% of rows, and the typical row sells about 86% of its demand. This points to sales that could be captured with better stock availability.

## 4. Predictive model

**Problem:** estimate `demand` for a store, product and day. The columns `units_sold` and `units_ordered` were excluded because they are outcomes of demand and would leak the answer.

**Validation:** time-based split. Training data is before 2023-09-01 (60,800 rows) and the test set is from 2023-09-01 (15,200 rows). Models were ranked by 3-fold time-series cross-validation RMSE on the training data, then checked on the test set.

| Model | CV RMSE | Test MAE | Test RMSE | Test R2 | Train R2 - Test R2 |
|---|---|---|---|---|---|
| **Gradient Boosting** | **14.06** | **6.68** | **9.74** | **0.951** | 0.012 |
| Extra Trees | 22.71 | 9.48 | 14.88 | 0.886 | 0.104 |
| Decision Tree | 31.41 | 15.58 | 23.15 | 0.724 | 0.181 |
| Linear Regression | 35.71 | 25.72 | 33.13 | 0.435 | 0.025 |
| Baseline (mean) | 48.13 | 35.43 | 44.37 | -0.013 | 0.013 |

Re-running the notebook can change the third decimal of the Gradient Boosting scores slightly.

**Why Gradient Boosting:** it has the lowest error on both cross-validation and the unseen test period, and its small train/test gap (0.012) shows it is not simply memorizing the training data. Extra Trees is also strong but overfits more (gap 0.10). Linear Regression explains only 44% of the variance because the drivers interact (for example epidemic periods and promotions), which linear models cannot capture. All real models beat the baseline of always predicting the average.

**In business terms:** the selected model is off by about 7 units on average, against an average demand of about 104 units per row.

**What drives the predictions** (permutation importance): category, price and product dominate, followed by store, competitor price and discount. Price, category and product are strongly linked (for example furniture is expensive and toys are cheap), so together they mostly describe the type of item and its baseline demand level. Promotion and epidemic matter less for the model's accuracy but are the main levers that change demand within an item, consistent with the analysis above.

**Where the model is weaker:** errors are highest for promotion rows (MAE 8.3 vs 5.9 without promotion), epidemic rows (7.6 vs 6.5) and for Groceries (8.0, the category with the highest volumes). Furniture is predicted best (4.1).

## 5. Recommendations

1. **Cap discounts at 15%.** Volume stops rising after 15%, and a 25% discount cuts revenue per row by about 22% versus no discount.
2. **Use promotions more deliberately.** They lift volume by 26% and revenue by about 5%. Pair them with enough stock, since demand already exceeds sales in most rows.
3. **Prepare for epidemic-type disruptions.** Sales fall by more than a third, so ordering and staffing plans need a downside scenario.
4. **Review stock availability.** Roughly 14% of demand goes unsold in a typical row; check ordering and replenishment for the high-demand categories.
5. **Investigate store S005** (lowest revenue per row, 4,776 vs 5,872 at S003) and the weakest products (P0001, P0007, P0002).
6. **Consider weather-aware promotions.** Rainy and snowy days sell 15-17% fewer units; targeted offers on those days are worth testing.
7. **Use the model for planning, not auditing.** It estimates demand under given conditions and can support inventory and promotion planning for existing store and product combinations.

## 6. Limitations

- The model uses conditions such as epidemic status, weather and promotions as inputs. These are not always known in advance, so it estimates demand given conditions rather than forecasting the unknown future.
- Predictions are only reliable for realistic inputs. Product, category and price are tightly linked in the data, and unrealistic combinations (for example a price far outside the usual range for that category) give unreliable results.
- Product IDs are not tied to a single category in this dataset, so product-level conclusions should be treated with care.
- Validation uses a single time-based holdout (September 2023 to January 2024), and no extensive hyperparameter search was done.
- The data looks synthetic (for example price has no effect on units sold), so the findings describe this dataset and may not transfer to a real retailer.

## 7. Deliverables

| Deliverable | File |
|---|---|
| SQL database | `retail_sales.db` (table `sales`) |
| Analytical notebook (cleaning, EDA, SQL) | `Retail_Sales_Analysis.ipynb` |
| Regression models, comparison and evaluation | `Retail_ML_Models.ipynb`, `model_comparison.csv` |
| Interactive dashboard | `app.py` |
| Model-serving API (optional extension) | `api.py`, `best_model.joblib` |
| Business report | `REPORT.md` |
