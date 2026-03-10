import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import get_macro_data, get_stock_data, get_stock_history, get_breaking_news
from styles import apply_terminal_theme, styled_metric
from datetime import datetime
import json
import requests
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="EQUITY_TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Theme
apply_terminal_theme()

# --- SIDEBAR & SETUP ---
st.sidebar.markdown("### TERMINAL_CONTROL")
tickers = st.sidebar.multiselect(
    "ACTIVE_WATCHLIST",
    ["SLS", "^IXIC", "^FTSE", "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "AMD", "META"],
    default=["SLS", "^IXIC", "^FTSE"]
)

# AI Insight API Setup
load_dotenv('.env')
API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY') or st.secrets.get("GOOGLE_CLOUD_API_KEY")

@st.cache_data(ttl=3600)
def get_ai_insight(ticker, data, news):
    prompt = f"""
    Analyze the following data for {ticker} and provide 3-4 factual, professional, and insightful bullet points.
    Context: {json.dumps(data)}
    Recent News: {json.dumps(news)}
    
    Guidelines:
    - Be concise and factual.
    - Focus on Institutional flows, Volume patterns, and Catalysts.
    - No speculation or financial advice.
    - Tone: Institutional Research Analyst.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Insight generation currently unavailable. Check market data for trends."

# --- MAIN DASHBOARD ---
view_option = st.sidebar.selectbox("VIEW_PORT", ["MACRO_OVERVIEW"] + tickers)

if view_option == "MACRO_OVERVIEW":
    st.header("GLOBAL_MARKET_MONITOR")
    
    with st.spinner("SYNCING_MACRO_DATA"):
        macro_df = get_macro_data()
    
    if not macro_df.empty:
        cols = st.columns(len(macro_df))
        for i, row in macro_df.iterrows():
            with cols[i]:
                styled_metric(row['Name'], f"{row['Price']:,.2f}", f"{row['Change']:+.2f}%")
    else:
        st.error("MACRO_SYNC_FAILED: CHECK_RATE_LIMITS")
    
    st.divider()
    
    st.subheader("SECTOR_RELATIVE_STRENGTH")
    sector_data = {"Tech (XLK)": 1.2, "Energy (XLE)": -0.8, "Fin (XLF)": 0.5, "Health (XLV)": 0.1, "Cons (XLY)": 0.9}
    fig = go.Figure(go.Bar(x=list(sector_data.keys()), y=list(sector_data.values()), marker_color=['#3fb950' if v > 0 else '#f85149' for v in sector_data.values()]))
    fig.update_layout(
        template="plotly_dark", 
        paper_bgcolor="#0d1117", 
        plot_bgcolor="#0d1117",
        font=dict(family="JetBrains Mono", size=10),
        height=300,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    ticker = view_option
    st.header(f"TICKER: {ticker}")
    
    # Data Sync
    with st.spinner(f"SYNCING_{ticker}_DATA"):
        stock_info = get_stock_data(ticker)
        history = get_stock_history(ticker)
        news = get_breaking_news(f"{ticker} stock news")
        
    if "error" in stock_info or history.empty:
        st.error(f"SYNC_ERROR: {ticker}")
        if history.empty:
            st.info("API_RATE_LIMIT_EXCEEDED")
            st.stop()

    # 1. Price Action
    fig = go.Figure(data=[go.Candlestick(
        x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'], name='Price'
    )])
    fig.update_layout(
        template="plotly_dark", 
        xaxis_rangeslider_visible=False, 
        height=500,
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(family="JetBrains Mono", size=10)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Key Metrics
    st.subheader("TECHNICAL_FUNDAMENTAL_STATS")
    col1, col2, col3, col4 = st.columns(4)
    stats = stock_info.get('stats', {})
    with col1: styled_metric("LAST_PRICE", f"${history['Close'].iloc[-1]:.2f}")
    with col2: styled_metric("VOLUME", f"{stats.get('Volume', 0):,}")
    with col3: 
        mc = stats.get('Market Cap')
        val = f"${mc/1e9:.2f}B" if mc else "N/A"
        styled_metric("MARKET_CAP", val)
    with col4: 
        earnings_date = "N/A"
        cal = stock_info.get('calendar')
        if cal is not None and 'Earnings Date' in cal:
            earnings_date = cal['Earnings Date'][0].strftime('%Y-%m-%d')
        styled_metric("EARNINGS_DATE", earnings_date)
        
    # 3. Institutional Flows
    st.divider()
    st.subheader("INSTITUTIONAL_RADAR_13F")
    inst_data = stock_info.get('institutional', [])
    if inst_data:
        inst_df = pd.DataFrame(inst_data)
        st.table(inst_df)
    else:
        st.warning("WHALE_DATA_UNAVAILABLE")
        
    # 4. News & Catalysts
    st.subheader("MARKET_NEWS_CATALYSTS")
    if news:
        for item in news:
            st.markdown(f"- **{item['source']}**: [{item['title']}]({item['url']}) ({item['date']})")
    
    # 5. Analysis
    st.divider()
    st.subheader("COPAW_EXECUTIVE_ANALYSIS")
    insight = get_ai_insight(ticker, stats, news)
    st.markdown(f'<div class="analysis-box">{insight}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("SYNC_STAMP: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
