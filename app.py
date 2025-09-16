import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# ===============================
# Function to fetch coins
# ===============================
def get_high_volume_coins(vs_currency="usd", per_page=250, pages=4, cap_limit=100_000_000, limit=20):
    """
    Fetch coins where:
      - Market Cap < cap_limit (default: $100M)
      - 24h trading volume >= market cap
      - Only top `limit` coins by ratio are returned
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    high_volume_coins = []

    for page in range(1, pages + 1):
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": False
        }
        response = requests.get(url, params=params)
        data = response.json()

        for coin in data:
            market_cap = coin.get("market_cap", 0) or 0
            volume = coin.get("total_volume", 0) or 0
            if 0 < market_cap < cap_limit and volume >= market_cap:
                ratio = (volume / market_cap) * 100
                high_volume_coins.append({
                    "Name": coin["name"],
                    "Symbol": coin["symbol"].upper(),
                    "Market Cap": market_cap,
                    "24h Volume": volume,
                    "Ratio (%)": ratio
                })

    # Sort by ratio (highest first) and limit results
    high_volume_coins.sort(key=lambda x: x["Ratio (%)"], reverse=True)
    return high_volume_coins[:limit]

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(page_title="Crypto Volume vs Market Cap", layout="wide")

st.title("📊 High-Volume Crypto Screener")
st.caption("Data source: CoinGecko API | Updates live when refreshed")

# Sidebar filters
st.sidebar.header("⚙️ Filters")
cap_limit = st.sidebar.number_input(
    "Max Market Cap ($)", min_value=1_000_000, max_value=1_000_000_000, value=100_000_000, step=1_000_000
)
top_n = st.sidebar.slider(
    "Top N Coins", min_value=5, max_value=50, value=20, step=1
)

# Fetch data
coins = get_high_volume_coins(cap_limit=cap_limit, limit=top_n)

if coins:
    df = pd.DataFrame(coins)
    df["Market Cap"] = df["Market Cap"].apply(lambda x: f"${x:,.0f}")
    df["24h Volume"] = df["24h Volume"].apply(lambda x: f"${x:,.0f}")
    df["Ratio (%)"] = df["Ratio (%)"].apply(lambda x: f"{x:.2f}%")

    st.dataframe(df, use_container_width=True)
else:
    st.warning("⚠️ No coins found matching criteria.")

# Footer
st.markdown(f"✅ Last updated: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
