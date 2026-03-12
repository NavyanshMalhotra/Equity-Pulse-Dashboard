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
        if not error_msg: return "Unknown Error"
        sanitized = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_KEY]', str(error_msg))
        return sanitized

    def get_whale_conviction(self, ticker_symbol):
        """Analyzes 13F trends and generates a high-speed Flash AI signal."""
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
            
            # Use Flash for the signal interpretation to avoid rate limits
            ai_signal = self._get_flash_interpretation(ticker_symbol, inst.head(10).to_json(), top_5_concentration)
            
            score = 50
            if top_5_concentration > 70: score = 85
            elif top_5_concentration > 40: score = 65
            
            return {"score": score, "status": "ACTIVE", "signal": ai_signal}
        except Exception as e:
            return {"score": 50, "status": "ERROR", "signal": f"Radar Offline: {self._sanitize_error(e)}"}

    def _get_flash_interpretation(self, ticker, inst_json, concentration):
        """Internal helper for high-speed Flash signals."""
        model_id = "gemini-flash-latest"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"
        
        prompt = f"Analyze institutional concentration for {ticker}. Top 5 hold {concentration:.1f}% of institutional float. Data: {inst_json}. Provide a 1-sentence institutional signal."
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 100}
        }
        
        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        except:
            return "Stable Institutional Holding"

    def get_correlations(self, ticker_symbol):
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
        """Expanded Synthesis using Gemini Pro with higher token limit."""
        if not self.api_key: return "AUTH_REQUIRED"

        model_id = "gemini-pro-latest" 
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={self.api_key}"

        prompt = f"""
        ACT AS AN INSTITUTIONAL INVESTMENT COMMITTEE.
        Perform a high-rigor 'Synthetic Debate' for {ticker}.
        
        DATA: Stats: {json.dumps(stats)}, Health: {json.dumps(adv)}, News: {json.dumps(news[:5])}
        
        OUTPUT SECTIONS (DO NOT CUT OFF):
        1. THE BULL CASE: (Technical/Fundamental)
        2. THE BEAR CASE: (Risk/Macro)
        3. SYNTHESIS: (Final verdict & Conviction Score)
        
        Constraint: Use markdown headers. Be comprehensive but data-dense.
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2, 
                "maxOutputTokens": 4096  # Increased to prevent cutoff
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"ANALYTICS_FAILED: {self._sanitize_error(e)}"
