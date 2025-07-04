import time
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- Dummy News & Sentiment Functions (Replace with actual implementations if needed) ---
def get_headlines(ticker):
    return [f"{ticker} stock update example headline 1", f"{ticker} news article 2"]

def analyze_sentiment(headlines):
    return [{"label": "positive", "score": 0.7} for _ in headlines]

def sentiment_score(results):
    return sum(r["score"] if r["label"] == "positive" else -r["score"] for r in results) / len(results)

# --- Page Config ---
st.set_page_config(layout="wide")
st.title("📈 Global Real-Time Stock Dashboard")

# --- Session Initialization ---
if "ticker" not in st.session_state:
    st.session_state["ticker"] = ""
if "headlines" not in st.session_state:
    st.session_state["headlines"] = None
if "sentiment" not in st.session_state:
    st.session_state["sentiment"] = None
if "balance" not in st.session_state:
    st.session_state.balance = 100000.0  # ₹1L
if "positions" not in st.session_state:
    st.session_state.positions = []

# --- Ticker Input ---
input_ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS, TSLA):")
if input_ticker:
    cleaned = input_ticker.strip().replace("$", "").upper()
    aliases = {
        "APPLE": "AAPL", "GOOGLE": "GOOG", "TESLA": "TSLA",
        "NVIDIA": "NVDA", "RELIANCE": "RELIANCE.NS", "RAYMOND": "RAYMOND.NS"
    }
    cleaned = aliases.get(cleaned, cleaned)
    st.session_state["ticker"] = cleaned
    st.session_state["headlines"] = None
    st.session_state["sentiment"] = None

ticker = st.session_state["ticker"]
is_indian = ticker.endswith(".NS") or ticker.endswith(".BO")

# 🔁 Auto-refresh only chart every 5 seconds
st_autorefresh(interval=5000, key="price_chart_refresh")

# --- News + Sentiment ---
if ticker and st.session_state["headlines"] is None:
    headlines = get_headlines(ticker)
    if headlines:
        st.session_state["headlines"] = headlines
        st.session_state["sentiment"] = analyze_sentiment(headlines)

if st.session_state["headlines"]:
    st.subheader(f"📰 News for {ticker}")
    for hl in st.session_state["headlines"]:
        st.markdown(f"- {hl}")

    st.subheader("🧠 Sentiment Analysis")
    results = st.session_state["sentiment"]
    for hl, res in zip(st.session_state["headlines"], results):
        label = res['label']
        score = res['score']
        st.markdown(f"- **{label.capitalize()}** ({score:.2f}) → _{hl}_")

    avg = sentiment_score(results)

    def interpret(score):
        if score >= 0.5: return "🟢 Strong Positive"
        if score > 0.1: return "🟡 Mild Positive"
        if score > -0.1: return "⚪ Neutral"
        if score > -0.5: return "🟠 Mild Negative"
        return "🔴 Strong Negative"

    st.success(f"📊 Avg Sentiment Score: `{avg:.2f}`")
    st.info(f"🧾 Interpreted: **{interpret(avg)}**")

# --- Price Chart + Simulation ---
if ticker:
    st.subheader(f"📈 {ticker} Price Chart (Auto-refresh every 5s)")

    time_range = st.selectbox(
        "Select Time Range",
        ["1D", "5D", "1M", "6M", "1Y", "5Y", "ALL"],
        index=0,
        key="period_selector"
    )

    period_map = {
        "1D": "1d", "5D": "5d", "1M": "1mo", "6M": "6mo",
        "1Y": "1y", "5Y": "5y", "ALL": "max"
    }

    interval_map = {
        "1D": "5m", "5D": "15m", "1M": "1d", "6M": "1d",
        "1Y": "1d", "5Y": "1wk", "ALL": "1mo"
    }

    selected_period = period_map[time_range]
    selected_interval = interval_map[time_range]

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=selected_period, interval=selected_interval)

        if df.empty:
            st.warning("⚠️ No data available for this time range or stock.")
        else:
            current = df["Close"].iloc[-1]
            open_ = df["Close"].iloc[0]
            pct_change = ((current - open_) / open_) * 100

            st.metric(f"💲 {ticker} Price", f"{current:.2f}", f"{pct_change:.2f}%")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df["Close"],
                mode="lines+markers", name="Price",
                line=dict(color="deepskyblue", width=2)
            ))
            fig.update_layout(
                title=f"{ticker} Price Chart ({time_range})",
                xaxis_title="Time",
                yaxis_title="Price (INR/₹)" if is_indian else "Price (USD)",
                height=450, template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"{ticker}_{time_range}")
            st.caption(f"⏱️ Updated at {time.strftime('%H:%M:%S')}")

            # --- Trading Simulation Section ---
            st.subheader("🎯 Try Simulated Trading")

            col1, col2, col3 = st.columns(3)
            with col1:
                qty = st.number_input("Quantity", min_value=1, value=1, step=1)

            with col2:
                if st.button("💰 Buy"):
                    cost = qty * current
                    if cost <= st.session_state.balance:
                        st.session_state.balance -= cost
                        st.session_state.positions.append({
                            "type": "Buy",
                            "qty": qty,
                            "price": current,
                            "time": time.strftime("%H:%M:%S")
                        })
                        st.success(f"✅ Bought {qty} shares at ₹{current:.2f}")
                    else:
                        st.error("Insufficient funds.")

            with col3:
                if st.button("📤 Sell"):
                    owned = sum(p['qty'] for p in st.session_state.positions if p['type'] == "Buy") - \
                            sum(p['qty'] for p in st.session_state.positions if p['type'] == "Sell")
                    if qty <= owned:
                        st.session_state.balance += qty * current
                        st.session_state.positions.append({
                            "type": "Sell",
                            "qty": qty,
                            "price": current,
                            "time": time.strftime("%H:%M:%S")
                        })
                        st.success(f"✅ Sold {qty} shares at ₹{current:.2f}")
                    else:
                        st.error("Not enough shares to sell.")

            st.markdown(f"💼 **Simulated Wallet Balance:** ₹{st.session_state.balance:,.2f}")

            if st.session_state.positions:
                st.subheader("📒 Trade History with Decision Evaluation")
                for i, t in enumerate(reversed(st.session_state.positions), 1):
                    qty = t["qty"]
                    price = t["price"]
                    action = t["type"]
                    time_ = t["time"]
                    pnl = (current - price) if action == "Buy" else (price - current)
                    status = (
                        "🟢 Good Decision" if pnl > 0.5 else
                        "⚪ Neutral" if abs(pnl) <= 0.5 else
                        "🔴 Bad Decision"
                    )
                    direction = "↑" if pnl >= 0 else "↓"
                    emoji = "🟢" if action == "Buy" else "🔴"
                    st.markdown(
                        f"{emoji} {action} {qty} @ ₹{price:.2f} — {time_}  \n"
                        f"      📊 Now: ₹{current:.2f} | P/L: ₹{pnl:.2f} {direction} → **{status}**"
                    )

    except Exception as e:
        st.error(f"❌ Error loading chart: {e}")
