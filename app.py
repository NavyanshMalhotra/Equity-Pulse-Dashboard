import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import get_macro_data, get_stock_data, get_stock_history, get_breaking_news
from datetime import datetime
import json
import requests
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Equity Pulse Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode & High Contrast CSS
st.markdown("""
<style>
    /* Main Background & Text Contrast */
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    
    /* Strong Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    /* Metric Card Styling */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #58a6ff;
        box-shadow: 0 8px 25px rgba(88, 166, 255, 0.15);
    }
    
    /* Text Visibility on Dark */
    .stMarkdown p, .stMarkdown li {
        color: #cbd5e0 !important;
        font-size: 16px;
        line-height: 1.6;
    }
    
    .glow-green {
        color: #00ff87 !important;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 255, 135, 0.3);
    }
    .glow-red {
        color: #ff4d4d !important;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(255, 77, 77, 0.3);
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #0d1117;
    }
    
    /* Table Styling */
    div[data-testid="stTable"] {
        background-color: #161b22;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for metrics
def styled_metric(label, value, delta=None):
    delta_class = "glow-green" if delta and float(delta.strip('%')) > 0 else "glow-red" if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <p style="font-size: 14px; color: #9ca3af; margin: 0;">{label}</p>
        <p style="font-size: 28px; font-weight: 700; margin: 0;">{value} <span class="{delta_class}" style="font-size: 16px;">{delta if delta else ""}</span></p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR & SETUP ---
st.sidebar.title("🚀 Equity Control")
tickers = st.sidebar.multiselect(
    "Select Equities to Track",
    ["SLS", "^IXIC", "^FTSE", "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "AMD", "META"],
    default=["SLS", "^IXIC", "^FTSE"]
)

# AI Insight API Setup
load_dotenv('.env')
API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY') or st.secrets.get("GOOGLE_CLOUD_API_KEY")

@st.cache_data(ttl=3600)
def get_ai_insight(ticker, data, news):
    """Generates factual, insightful AI analysis."""
    prompt = f"""
    Analyze the following data for {ticker} and provide 3-4 factual, professional, and insightful bullet points.
    Context: {json.dumps(data)}
    Recent News: {json.dumps(news)}
    
    Guidelines:
    - Be concise and factual.
    - No speculation or financial advice.
    - Highlight key risks or catalysts (earnings, institutional moves, volume trends).
    - Tone: Professional, high-level executive summary.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Insight generation currently unavailable. Check market data for trends."

# --- MAIN DASHBOARD ---
# Use a selectbox for true lazy loading to prevent YFRateLimitError
view_option = st.sidebar.selectbox("Navigate To:", ["🏠 Macro Overview"] + tickers)

if view_option == "🏠 Macro Overview":
    st.title("🌍 Global Macro & Sector Pulse")
    
    # Macro Indicators Row
    with st.spinner("Fetching macro data..."):
        macro_df = get_macro_data()
    
    if not macro_df.empty:
        cols = st.columns(len(macro_df))
        for i, row in macro_df.iterrows():
            with cols[i]:
                styled_metric(row['Name'], f"{row['Price']:,.2f}", f"{row['Change']:+.2f}%")
    else:
        st.error("Macro data currently unavailable due to rate limits. Please try again in a few minutes.")
    
    st.divider()
    
    # Micro Industry Analysis
    st.subheader("📊 Industry Breakdown (Micro View)")
    st.info("Sectors like Semiconductors and AI Infrastructure are showing significant relative strength in the current market regime.")
    
    # Interactive Sector Chart
    sector_data = {"Technology (XLK)": 1.2, "Energy (XLE)": -0.8, "Financials (XLF)": 0.5, "Health Care (XLV)": 0.1, "Consumer Disc (XLY)": 0.9}
    fig = go.Figure(go.Bar(x=list(sector_data.keys()), y=list(sector_data.values()), marker_color=['#00ff87' if v > 0 else '#ff4d4d' for v in sector_data.values()]))
    fig.update_layout(title="Daily Sector Performance (%)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

else:
    ticker = view_option
    st.header(f"💼 {ticker} - Deep Dive")
    
    # Data Fetching
    with st.spinner(f"Aggregating {ticker} data..."):
        stock_info = get_stock_data(ticker)
        history = get_stock_history(ticker)
        news = get_breaking_news(f"{ticker} stock news")
        
    if "error" in stock_info or history.empty:
        st.error(f"⚠️ Rate Limit or Data Error for {ticker}. Showing cached or partial data if available.")
        if history.empty:
            st.info("Yahoo Finance is currently limiting requests from this server. Please check back in a moment.")
            st.stop()

    # 1. Price Chart (The Dopamine Centerpiece)
    fig = go.Figure(data=[go.Candlestick(
        x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'], name='Price'
    )])
    fig.update_layout(title=f"{ticker} Price Action (1 Year)", template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Key Stats & Upcoming Dates
    st.subheader("📉 Technical & Fundamental Pulse")
    col1, col2, col3, col4 = st.columns(4)
    stats = stock_info.get('stats', {})
    with col1: styled_metric("Price", f"${history['Close'].iloc[-1]:.2f}")
    with col2: styled_metric("Volume", f"{stats.get('Volume', 0):,}")
    with col3: 
        mc = stats.get('Market Cap')
        val = f"${mc/1e9:.2f}B" if mc else "N/A"
        styled_metric("Market Cap", val)
    with col4: 
        earnings_date = "N/A"
        cal = stock_info.get('calendar')
        if cal is not None and 'Earnings Date' in cal:
            earnings_date = cal['Earnings Date'][0].strftime('%Y-%m-%d')
        styled_metric("Earnings Date", earnings_date)
        
    # 3. Whale & Institutional Radar
    st.divider()
    st.subheader("🐳 Institutional Whale Radar")
    inst_data = stock_info.get('institutional', [])
    if inst_data:
        inst_df = pd.DataFrame(inst_data)
        st.table(inst_df)
    else:
        st.warning("Institutional data (13F) is currently unavailable or being processed for this ticker.")
        
    # 4. Breaking News
    st.subheader("🗞️ Breaking News & Catalysts")
    if news:
        for item in news:
            st.markdown(f"- **{item['source']}**: [{item['title']}]({item['url']}) ({item['date']})")
    else:
        st.info("No recent news found or search limit reached.")
        
    # 5. AI Executive Insight
    st.divider()
    st.subheader("🧠 Copaw Executive Insight")
    insight = get_ai_insight(ticker, stats, news)
    st.markdown(f'<div style="background: #161b22; padding: 25px; border-left: 5px solid #00ff87; border-radius: 12px; border: 1px solid #30363d;">{insight}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
