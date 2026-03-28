import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# --- Config ------------------------------------------------------------------
DATA_FILE = "fake_data.csv"   # path to your CSV, relative to app.py

# --- Routes ------------------------------------------------------------------
OPENROUTER_API_KEY = "your-openrouter-api-key-here"
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    df = pd.read_csv(DATA_FILE)

    # Zero-pad FIPS so Plotly matches counties correctly (e.g. 1001 → "01001")
    df["fips"] = df["fips"].astype(str).str.zfill(5)

    # Drop rows missing either value — the frontend can't run the rule without both
    df = df.dropna(subset=["rent_2br", "median_price"])

    return jsonify({"data": df.to_dict(orient="records")})


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)