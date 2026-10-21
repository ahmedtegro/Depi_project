# Retail Demand & Sales Intelligence Platform

Historical retail sales analysis with SQL, EDA, a demand regression model, an interactive dashboard and a small prediction API.

## Project files

| File | What it is |
|---|---|
| `sales_data.csv` | Raw data (76,000 rows, Jan 2022 to Jan 2024) |
| `Retail_Sales_Analysis.ipynb` | Cleaning, outliers, EDA visuals, SQL queries |
| `retail_sales.db` | SQLite database created by the notebook (table `sales`) |
| `Retail_ML_Models.ipynb` | Model comparison, selection and evaluation |
| `model_comparison.csv` | Results table written by the ML notebook |
| `best_model.joblib` | Selected model (Gradient Boosting) |
| `app.py` | Interactive Dash dashboard |
| `api.py` | Flask API that serves predictions (optional extension) |
| `REPORT.md` | Business report |

## How to run

```
pip install -r requirements.txt
```

1. Run `Retail_Sales_Analysis.ipynb` to clean the data and rebuild `retail_sales.db`.
2. Run `Retail_ML_Models.ipynb` to compare models and save `best_model.joblib` and `model_comparison.csv`.
3. Dashboard: `python app.py`, then open http://127.0.0.1:8050
4. API: `python api.py`, then send requests to http://127.0.0.1:5000

Keep `sales_data.csv` in the same folder as the notebooks and scripts.

## Results in short

- Total revenue is about 412.6M (after discount) on 6.75M units.
- The epidemic periods are the strongest effect on sales (units sold -36%). Promotions lift units by 26%. Discounts above 15% add no extra volume.
- Target: `demand`. `units_sold` and `units_ordered` are excluded to avoid leakage. Split: train before 2023-09-01, test from 2023-09-01.
- Best model: Gradient Boosting (test R2 about 0.95, MAE about 7 units). It beats Extra Trees, Decision Tree, Linear Regression and a mean baseline.

See `REPORT.md` for the full findings, model comparison and recommendations.

## API example

Start the API with `python api.py`, then:

```
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d '{"date": "2024-01-23", "store_id": "S003", "product_id": "P0004", "category": "Groceries", "region": "East", "inventory_level": 292, "price": 20.47, "discount": 10, "weather_condition": "Cloudy", "promotion": 0, "competitor_pricing": 23.06, "seasonality": "Winter", "epidemic": 0}'
```

Response: `{"predicted_demand": [97.9]}`. You can also send a list of such objects. Use realistic values (for example, prices in the usual range for the category), because the model is not reliable outside the ranges seen in the data.

## Notes

- Revenue is `units_sold x price x (1 - discount / 100)`.
- Re-running the ML notebook can change the third decimal of the scores slightly.
