import json
import requests
import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import re

class PulseIntelligence:
    def __init__(self, api_key):
        self.api_key = api_key
        self.industry_maps = {
            "NVDA": ["TSM", "ASML", "AMD", "ARM"],
            "AAPL": ["TSM", "GOOGL", "MSFT", "AMZN"],
            "TSLA": ["BYDDF", "RIVN", "LCID", "PANW"],
            "MSFT": ["GOOGL", "AMZN", "META", "ORCL"],
            "AMZN": ["WMT", "EBAY", "BABA", "MSFT"]
        }

    def _sanitize_error(self, error_msg):
        """Removes API keys from error messages using regex."""
        if not error_msg: return "Unknown Error"
        # Mask common API key patterns (AIza...)
        sanitized = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_KEY]', str(error_msg))
        return sanitized

    def get_whale_conviction(self, ticker_symbol):
        """Analyzes 13F trends to determine institutional conviction."""
        try:
            stock = yf.Ticker(ticker_symbol)
            inst = stock.institutional_holders
            if inst is None or inst.empty:
                return {"score": 50, "status": "NEUTRAL", "signal": "Insufficient Data"}
            
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
        except Exception as e:
            return {"score": 50, "status": "NEUTRAL", "signal": f"Error: {self._sanitize_error(e)}"}

    def get_correlations(self, ticker_symbol):
        """Fetches relative performance of correlated peers."""
        peers = self.industry_maps.get(ticker_symbol, [])
        correlation_data = []
        for peer in peers:
            try:
                p_stock = yf.Ticker(peer)
                p_hist = p_stock.history(period="5d")
                if not p_hist.empty:
                    change = ((p_hist['Close'].iloc[-1] - p_hist['Close'].iloc[-2]) / p_hist['Close'].iloc[-2]) * 100
                    correlation_data.append({"ticker": peer, "change": change})
            except: continue
        return correlation_data

    def get_synthetic_report(self, ticker, stats, tech, adv, news):
        """Multi-persona debate synthesis using Gemini 1.5 Pro."""
        if not self.api_key:
            return "ERROR: Critical Authentication Missing."

        # Corrected & Verified Model ID: gemini-pro-latest
        model_id = "gemini-pro-latest" 
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
            sanitized_e = self._sanitize_error(e)
            return f"INTELLIGENCE_LAYER_ERROR: {sanitized_e}"
