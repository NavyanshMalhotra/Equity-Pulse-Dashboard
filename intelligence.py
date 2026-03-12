import json
import requests
import os
import pandas as pd
import yfinance as yf
from datetime import datetime

class PulseIntelligence:
    def __init__(self, api_key):
        self.api_key = api_key
        # Industry Mapping for Correlation Radar
        self.industry_maps = {
            "NVDA": ["TSM", "ASML", "AMD", "ARM"],
            "AAPL": ["TSM", "GOOGL", "MSFT", "AMZN"],
            "TSLA": ["BYDDF", "RIVN", "LCID", "PANW"],
            "MSFT": ["GOOGL", "AMZN", "META", "ORCL"],
            "AMZN": ["WMT", "EBAY", "BABA", "MSFT"]
        }

    def get_whale_conviction(self, ticker_symbol):
        """Analyzes 13F trends to determine institutional conviction."""
        try:
            stock = yf.Ticker(ticker_symbol)
            inst = stock.institutional_holders
            if inst is None or inst.empty:
                return {"score": 50, "status": "NEUTRAL", "signal": "Insufficient Data"}
            
            # Logic: Analyze the concentration of the top 5
            inst['Shares'] = pd.to_numeric(inst['Shares'], errors='coerce')
            inst = inst.dropna(subset=['Shares'])
            
            total_shares = inst['Shares'].sum()
            if total_shares == 0:
                return {"score": 50, "status": "NEUTRAL", "signal": "Static Float"}
                
            top_5_concentration = (inst['Shares'].head(5).sum() / total_shares) * 100
            
            if top_5_concentration > 70:
                return {"score": 85, "status": "HIGH", "signal": "Concentrated Accumulation"}
            elif top_5_concentration > 40:
                return {"score": 65, "status": "MODERATE", "signal": "Broad Institutional Support"}
            else:
                return {"score": 40, "status": "LOW", "signal": "Fragmented Ownership"}
        except:
            return {"score": 50, "status": "NEUTRAL", "signal": "Data Stream Offline"}

    def get_correlations(self, ticker_symbol):
        """Fetches relative performance of correlated peers/supply chain."""
        peers = self.industry_maps.get(ticker_symbol, [])
        correlation_data = []
        for peer in peers:
            try:
                p_stock = yf.Ticker(peer)
                p_hist = p_stock.history(period="5d")
                if not p_hist.empty:
                    change = ((p_hist['Close'].iloc[-1] - p_hist['Close'].iloc[-2]) / p_hist['Close'].iloc[-2]) * 100
                    correlation_data.append({"ticker": peer, "change": change})
            except:
                continue
        return correlation_data

    def get_synthetic_report(self, ticker, stats, tech, adv, news):
        """Multi-persona debate synthesis using Gemini Pro/Flash."""
        if not self.api_key:
            return "API_KEY_MISSING"

        # Model Routing: Use Pro for Synthesis, Flash for persona generation if needed
        # For simplicity in MVP, we use a single multi-persona prompt on Pro
        model_id = "gemini-1.5-pro-latest" 
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"

        prompt = f"""
        ACT AS AN INSTITUTIONAL INVESTMENT COMMITTEE.
        Perform a high-rigor 'Synthetic Debate' for {ticker}.
        
        DATA CONTEXT:
        - Stats: {json.dumps(stats)}
        - Health: {json.dumps(adv)}
        - News: {json.dumps(news[:5])}
        
        STRUCTURE:
        1. THE BULL CASE: (Technical breakouts, fundamental tailwinds)
        2. THE BEAR CASE: (Risk factors, valuation concerns, macro threats)
        3. SYNTHESIS & CONVICTION: (Final verdict, probability of trend continuation)
        
        TONE: Institutional, Data-Dense, No Fluff.
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
        }

        try:
            response = requests.post(url, json=payload, timeout=25)
            response.raise_for_status()
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"INTELLIGENCE_LAYER_ERROR: {str(e)}"
