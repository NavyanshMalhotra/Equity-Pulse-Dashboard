# 📈 EQUITY_TERMINAL
**Institutional-Grade Equity Analysis Dashboard**

EQUITY_TERMINAL is a high-performance, data-dense analytical platform designed for professional-level market monitoring. It combines advanced technical indicators, quantitative health scoring, and AI-driven executive insights into a sleek, terminal-style interface.

## 🚀 Key Features

### 1. **Terminal-Style UI**
*   **Monospaced Visuals**: Designed with a high-contrast, dark-mode terminal aesthetic for a professional trading environment.
*   **Lazy Loading Architecture**: Only fetches data for the active ticker, ensuring high performance and resilience against API rate limits.
*   **Watchlist Management**: Dynamic sidebar controls for navigating between global macro views and specific equity deep-dives.

### 2. **Advanced Technical Engine**
*   **Synchronized Multi-Chart**: Interactive candlestick charts with **SMA 50** and **SMA 200** overlays.
*   **Momentum Oscillators**: Real-time **RSI (14)** and **MACD** sub-charts with overbought/oversold annotations.
*   **Technical Labels**: Every chart includes professional-grade axes, labels, and legends for precise data interpretation.

### 3. **Quantitative Intelligence**
*   **F-Score Rank**: Custom-calculated **Piotroski F-Score** (0-3) analyzing fundamental health trends (Profitability, Leverage, Operating Efficiency).
*   **Earnings Surprise Tracker**: Visual comparison of Estimated vs. Reported EPS for the last 8 quarters.
*   **Institutional Whale Radar (13F)**: Deep-dive into the top 10 institutional holders and their position sizes.
*   **Quantitative Stats**: Mean price targets, short ratios, and beta monitoring.

### 4. **Copaw AI Signal Generator**
*   **Executive Insights**: Powered by **Gemini 1.5 Pro**, providing 4 high-impact, factual bullet points analyzing sentiment, technical setups, and fundamental risks.
*   **Contextual News Feed**: Real-time news aggregation from professional financial sources.

## 🛠️ Technology Stack
*   **Frontend**: Streamlit
*   **Data Aggregation**: yfinance (Yahoo Finance API)
*   **Visualizations**: Plotly (Subplots & Custom Objects)
*   **News Intelligence**: DuckDuckGo Search API
*   **AI Engine**: Google Gemini API

## 📦 Setup & Deployment
1.  **Fork the Repository**: Clone this project to your GitHub.
2.  **Hosting**: Connect the repository to [Streamlit Community Cloud](https://streamlit.io/cloud).
3.  **Secrets Management**: In the Streamlit "Advanced Settings", add your API key in TOML format:
    ```toml
    GOOGLE_CLOUD_API_KEY = "Your_Google_API_Key"
    ```

---
*Developed by Copaw AI*
