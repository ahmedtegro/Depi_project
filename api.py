from flask import Flask, jsonify, request
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load("best_model.joblib")

FEATURES = [
    "store_id", "product_id", "category", "region", "weather_condition", "seasonality",
    "inventory_level", "price", "discount", "promotion", "competitor_pricing", "epidemic",
    "year", "month", "day", "dayofweek",
]


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True)
    rows = payload if isinstance(payload, list) else [payload]

    data = pd.DataFrame(rows)
    if "date" in data.columns:
        dates = pd.to_datetime(data["date"])
        data["year"] = dates.dt.year
        data["month"] = dates.dt.month
        data["day"] = dates.dt.day
        data["dayofweek"] = dates.dt.dayofweek

    missing = [c for c in FEATURES if c not in data.columns]
    if missing:
        return jsonify({"error": "missing fields", "missing": missing}), 400

    predictions = model.predict(data[FEATURES])
    return jsonify({"predicted_demand": [round(float(p), 1) for p in predictions]})


if __name__ == "__main__":
    app.run(port=5000)
