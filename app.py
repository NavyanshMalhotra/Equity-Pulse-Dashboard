import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_macro_data, get_stock_data, get_technical_analysis, get_breaking_news, get_advanced_stats, get_earnings_history
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
st.sidebar.markdown("### TERMINAL CONTROL")
tickers = st.sidebar.multiselect(
    "ACTIVE WATCHLIST",
    ["SLS", "^IXIC", "^FTSE", "AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "AMZN", "AMD", "META"],
    default=["SLS", "^IXIC", "^FTSE"]
)

# AI Insight API Setup
load_dotenv('.env')
API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY') or st.secrets.get("GOOGLE_CLOUD_API_KEY")

@st.cache_data(ttl=3600)
def get_ai_insight(ticker, stats, tech, adv, news):
    prompt = f"""
    Perform a professional deep-dive analysis for {ticker}.
    
    Data Provided:
    - Fundamentals: {json.dumps(stats)}
    - Quantitative Health: {json.dumps(adv)}
    - Recent Price/Technical Summary (Last Close): {tech.iloc[-1].to_json() if not tech.empty else 'N/A'}
    - Recent News: {json.dumps(news[:3])}
    
    Task:
    Provide 4 concise, institutional-grade analytical bullet points. 
    Include:
    1. Sentiment based on News & Institutional flow.
    2. Technical setup (RSI/SMA/MACD crossover).
    3. Fundamental/Quant Health risk (F-score/Debt/Margins).
    4. Catalyst/Short-term Outlook.
    
    Tone: Institutional Analyst (Fact-based, No fluff, High impact).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "ANALYTICS OFFLINE: CHECK API KEY"

# --- MAIN DASHBOARD ---
view_option = st.sidebar.selectbox("VIEW PORT", ["MACRO OVERVIEW"] + tickers)

if view_option == "MACRO OVERVIEW":
    st.header("GLOBAL MARKET MONITOR")
    with st.spinner("SYNCING MACRO DATA..."):
        macro_df = get_macro_data()
    
    if not macro_df.empty:
        cols = st.columns(len(macro_df))
        for i, row in macro_df.iterrows():
            with cols[i]:
                styled_metric(row['Name'], f"{row['Price']:,.2f}", f"{row['Change']:+.2f}%")
    
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("SECTOR STRENGTH INDEX")
        # Real sector data logic could go here
        sectors = {"XLK": 1.2, "XLY": 0.8, "XLV": 0.3, "XLF": -0.4, "XLE": -1.1}
        fig = go.Figure(go.Bar(x=list(sectors.keys()), y=list(sectors.values()), marker_color=['#3fb950' if v > 0 else '#f85149' for v in sectors.values()]))
        fig.update_layout(
            template="plotly_dark", 
            paper_bgcolor="#0d1117", 
            plot_bgcolor="#0d1117", 
            height=300, 
            margin=dict(l=40, r=20, t=30, b=40),
            xaxis_title="Sector ETF",
            yaxis_title="Daily Change (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("MARKET SENTIMENT QUICK READ")
        st.info("Institutional appetite remains focused on high-margin tech despite macro headwinds in energy. VIX suggests low-complacency risk premium.")

else:
    ticker = view_option
    st.header(f"TICKER TERMINAL: {ticker}")
    
    with st.spinner(f"PROCESSING {ticker} INTEL..."):
        stock_info = get_stock_data(ticker)
        tech_data = get_technical_analysis(ticker)
        adv_stats = get_advanced_stats(ticker)
        news = get_breaking_news(f"{ticker} stock news")
        earnings = get_earnings_history(ticker)
        
    if tech_data.empty:
        st.error(f"SYNC FAILED: {ticker}")
        st.stop()

    # 1. Advanced Technical Chart
    st.subheader("TECHNICAL PRICE ACTION & MOMENTUM")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2])
    
    currency = stock_info.get('stats', {}).get('Currency', 'USD')
    y_label = "Points" if ticker.startswith("^") else f"Price ({currency})"

    # Candle + SMAs
    fig.add_trace(go.Candlestick(x=tech_data.index, open=tech_data['Open'], high=tech_data['High'], low=tech_data['Low'], close=tech_data['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['SMA_50'], name="SMA 50", line=dict(color='#58a6ff', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['SMA_200'], name="SMA 200", line=dict(color='#d29922', width=1.5)), row=1, col=1)
    fig.update_yaxes(title_text=y_label, row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['RSI'], name="RSI", line=dict(color='#bc8cff', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#f85149", row=2, col=1, annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dot", line_color="#3fb950", row=2, col=1, annotation_text="Oversold")
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    
    # MACD
    fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['MACD'], name="MACD", line=dict(color='#58a6ff', width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=tech_data.index, y=tech_data['Signal'], name="Signal", line=dict(color='#d29922', width=1.5)), row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)
    
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=800, paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", showlegend=True, margin=dict(l=60, r=40, t=20, b=60))
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Key Stats & Quant Health
    st.subheader("QUANTITATIVE & FUNDAMENTAL HEALTH")
    c1, c2, c3, c4 = st.columns(4)
    stats = stock_info.get('stats', {})
    with c1: styled_metric("LAST CLOSE", f"{tech_data['Close'].iloc[-1]:.2f} {currency}")
    with c2: styled_metric("F-SCORE RANK", f"{adv_stats['health_score']}/3", "TREND" if str(adv_stats['health_score']) == "N/A" or (isinstance(adv_stats['health_score'], int) and adv_stats['health_score'] > 1) else "RISK")
    with c3: styled_metric("MEAN TARGET", f"{adv_stats['target_mean']:.2f} {currency}")
    with c4: styled_metric("SHORT RATIO", f"{adv_stats['short_ratio']:.1f}")

    # 3. Institutional Flows & Earnings History
    col_x, col_y = st.columns([1, 1])
    with col_x:
        st.subheader("INSTITUTIONAL HOLDERS (13F)")
        inst_data = stock_info.get('institutional', [])
        if inst_data: st.table(pd.DataFrame(inst_data))
        else: st.warning("NO WHALE DATA FOUND")
    with col_y:
        st.subheader("EARNINGS SURPRISE TRACKER")
        if earnings is not None and not earnings.empty:
            earning_fig = go.Figure()
            # Plot using standardized column names from utils.py
            if 'Reported' in earnings.columns:
                earning_fig.add_trace(go.Bar(x=earnings.index, y=earnings['Reported'], name='Actual', marker_color='#3fb950'))
            if 'Estimate' in earnings.columns:
                earning_fig.add_trace(go.Bar(x=earnings.index, y=earnings['Estimate'], name='Estimate', marker_color='#8b949e'))
            
            earning_fig.update_layout(
                template="plotly_dark", barmode='group', height=400, 
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", 
                margin=dict(l=40, r=20, t=40, b=40),
                xaxis_title="Date Reported",
                yaxis_title=f"EPS ({currency})",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(earning_fig, use_container_width=True)
        else:
            st.info("EARNINGS HISTORY DATA RESTRICTED OR UNAVAILABLE")

    # 4. News Catalysts & Executive Analysis
    st.subheader("MARKET CATALYSTS & SENTIMENT ENGINE")
    n_col, a_col = st.columns([1, 1.5])
    with n_col:
        if news:
            for item in news[:5]:
                st.markdown(f"- **{item['source']}**: [{item['title']}]({item['url']})")
    with a_col:
        insight = get_ai_insight(ticker, stats, tech_data, adv_stats, news)
        st.markdown(f'<div class="analysis-box"><strong>COPAW SIGNAL GENERATOR:</strong><br><br>{insight}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("SYNC_STAMP: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

