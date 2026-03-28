import pandas as pd
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# --- Config ------------------------------------------------------------------

DATA_FILE = "complete_county_housing_buy_vs_rent.csv"

OPENROUTER_API_KEY = "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"

# "openrouter/free" is not a real model name — use a specific free model instead.
# mistralai/mistral-7b-instruct:free is one of the most reliable free options.
OPENROUTER_MODEL = "openrouter/free"

# Fallback message shown to the user whenever the API returns nothing usable
FALLBACK_REPLY = "Sorry, I can't answer that right now. Please try again in a moment."

SYSTEM_PROMPT = """You are a knowledgeable and friendly financial advisor embedded
in a Rent vs. Buy Interactive Map tool. Your job is to help users understand whether
renting or buying a home makes financial sense in their county, using the 5% rule.

THE 5% RULE:
  Break-even monthly rent = (Home Price x 5%) / 12
  The 5% breaks down as: ~1% property tax + ~1% maintenance + ~3% cost of capital.
  If actual rent < break-even rent -> RENTING is cheaper.
  If actual rent > break-even rent -> BUYING is cheaper.
  A $50/month buffer separates BUY, RENT, and BORDERLINE verdicts.

THE MAP:
  - Green counties: buying is cheaper (actual rent exceeds break-even by $50+/mo)
  - Red counties: renting is cheaper (actual rent is below break-even by $50+/mo)
  - Yellow/borderline: within $50/month of break-even either way
  - The monthly gap shows exactly how much cheaper one option is per month
  - Clicking a state shows a county-by-county ranked bar chart

SCENARIO MODES:
  - Inflation slider (0-10%): adds extra monthly cost to the buyer's side since
    higher inflation leads to higher mortgage rates. High inflation makes the map
    turn redder (renting more favorable).
  - Crash scenario (0%, -10%, -20%, -30%): simulates a home price decline.
    Cheaper homes lower the cost of ownership so buying looks more attractive.
    The map turns greener in a crash scenario.

KEY CONTEXT:
  - This tool is for people actively deciding whether to rent or buy RIGHT NOW.
  - It is not for existing homeowners.
  - Data is county-level median figures — individual properties will vary.
  - The tool does not account for individual mortgage rates, credit scores,
    HOA fees, or homeowner's insurance.

Keep answers concise, practical, and friendly. Use dollar examples when helpful.
Do not give personalized legal or financial advice — explain the tool's logic only."""


# --- Helper ------------------------------------------------------------------

def extract_reply(data):
    """
    Safely pull the assistant's reply text out of the OpenRouter response.
    Returns the FALLBACK_REPLY string if anything in the chain is missing or None.
    """
    try:
        reply = data["choices"][0]["message"]["content"]
        if reply and reply.strip():
            return reply.strip()
    except (KeyError, IndexError, TypeError):
        pass
    return FALLBACK_REPLY


# --- Routes ------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    df = pd.read_csv(DATA_FILE)
    df["fips"] = df["fips"].astype(str).str.zfill(5)
    df = df.dropna(subset=["rent", "median_price"])
    return jsonify({"data": df.to_dict(orient="records")})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = request.get_json()

    if not body or "messages" not in body:
        return jsonify({"success": True, "reply": FALLBACK_REPLY})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + body["messages"]

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Rent vs Buy Advisor",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.7,
            },
            timeout=30,
        )

        response.raise_for_status()
        reply = extract_reply(response.json())
        return jsonify({"success": True, "reply": reply})

    except Exception as e:
        print(f"CHAT ERROR: {type(e).__name__}: {e}")
        return jsonify({"success": True, "reply": FALLBACK_REPLY})


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)