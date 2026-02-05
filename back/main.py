from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
import random
import statistics
from transformers import pipeline

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- AI MODEL (CORRECT PIPELINE FOR FLAN-T5) ----------
analyzer = pipeline(
    "text-generation",
    model="google/flan-t5-base",
    max_new_tokens=120
)

# ---------- ROOT ----------
@app.get("/")
def root():
    return {"message": "RealTicker backend running"}

# ---------- MOCK TOP 10 (TODAY SNAPSHOT) ----------
stocks = [
    {"ticker": "AAPL", "company": "Apple Inc", "price": 185.40, "change_percent": "+1.2%", "volume": "78M"},
    {"ticker": "MSFT", "company": "Microsoft", "price": 412.30, "change_percent": "+0.8%", "volume": "45M"},
    {"ticker": "GOOGL", "company": "Alphabet", "price": 152.10, "change_percent": "-0.4%", "volume": "32M"},
    {"ticker": "AMZN", "company": "Amazon", "price": 168.50, "change_percent": "+0.6%", "volume": "51M"},
    {"ticker": "META", "company": "Meta", "price": 487.90, "change_percent": "+1.9%", "volume": "29M"},
    {"ticker": "TSLA", "company": "Tesla", "price": 238.20, "change_percent": "-1.1%", "volume": "96M"},
    {"ticker": "NFLX", "company": "Netflix", "price": 612.40, "change_percent": "+0.3%", "volume": "18M"},
    {"ticker": "NVDA", "company": "NVIDIA", "price": 875.60, "change_percent": "+2.4%", "volume": "64M"},
    {"ticker": "INTC", "company": "Intel", "price": 43.20, "change_percent": "-0.7%", "volume": "41M"},
    {"ticker": "ORCL", "company": "Oracle", "price": 118.90, "change_percent": "+0.5%", "volume": "22M"},
]

@app.get("/api/stocks/top10")
def get_top_10_stocks():
    return stocks

# ---------- STOCK HISTORY CACHE (IMPORTANT FIX) ----------
stock_history_cache = {}

def generate_stock_history(ticker: str):
    if ticker in stock_history_cache:
        return stock_history_cache[ticker]

    history = []
    today = date.today()
    price = random.uniform(100, 500)

    for i in range(180):  # 6 months
        price += random.uniform(-5, 5)
        history.append({
            "date": str(today - timedelta(days=i)),
            "price": round(price, 2)
        })

    history.reverse()
    stock_history_cache[ticker] = history
    return history

# ---------- ANALYZE STOCK ----------
@app.post("/api/stocks/{ticker}/analyze")
def analyze_stock(ticker: str, months: int = 6):
    history = generate_stock_history(ticker)
    days = months * 30

    prices = [p["price"] for p in history[-days:]]

    start = prices[0]
    end = prices[-1]
    change_percent = ((end - start) / start) * 100
    volatility = statistics.stdev(prices)

    # ----- TREND -----
    if change_percent > 2:
        trend = "Upward"
    elif change_percent < -1:
        trend = "Downward"
    else:
        trend = "Sideways"

    # ----- RISK -----
    if volatility < 2:
        risk = "Low"
    elif volatility < 5:
        risk = "Medium"
    else:
        risk = "High"

    # ----- ACTION -----
    if trend == "Upward" and risk == "Low":
        action = "Long-term Investment"
        reason = "Consistent upward movement with low volatility."
    elif trend == "Downward":
        action = "Avoid"
        reason = "Sustained decline over the selected time period."
    else:
        action = "Short-term Watch"
        reason = "No clear long-term trend detected."

    return {
        "ticker": ticker.upper(),
        "analysis_period": f"Last {months} month(s)",
        "trend": trend,
        "risk_level": risk,
        "suggested_action": action,
        "reason": reason,
        "disclaimer": "This is AI-generated analysis and not financial advice."
    }
