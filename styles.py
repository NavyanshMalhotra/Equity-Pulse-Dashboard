import streamlit as st

def apply_terminal_theme():
    st.markdown("""
    <style>
        /* Base Background and Font */
        .stApp {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
        }
        
        /* Strong Headers */
        h1, h2, h3 {
            color: #f0f6fc !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            border-bottom: 1px solid #30363d;
            padding-bottom: 10px;
        }

        /* Metric Card Styling - Bloomberg Terminal Style */
        .metric-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 20px;
            box-shadow: none;
        }
        
        .metric-label {
            color: #8b949e;
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 500;
        }
        
        .metric-value {
            color: #f0f6fc;
            font-size: 24px;
            font-weight: 700;
            margin-top: 5px;
        }
        
        .glow-green {
            color: #3fb950 !important;
            font-weight: 600;
        }
        .glow-red {
            color: #f85149 !important;
            font-weight: 600;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #010409 !important;
            border-right: 1px solid #30363d;
        }
        
        /* Table Styling */
        div[data-testid="stTable"] {
            background-color: #0d1117;
            border-radius: 0px;
            border: 1px solid #30363d;
        }
        
        /* Analysis Box */
        .analysis-box {
            background: #0d1117;
            padding: 20px;
            border-left: 3px solid #58a6ff;
            border-top: 1px solid #30363d;
            border-right: 1px solid #30363d;
            border-bottom: 1px solid #30363d;
            border-radius: 0px;
        }
    </style>
    """, unsafe_allow_html=True)

def styled_metric(label, value, delta=None):
    delta_class = "glow-green" if delta and "+" in delta else "glow-red" if delta and "-" in delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value} <span class="{delta_class}" style="font-size: 14px;">{delta if delta else ""}</span></div>
    </div>
    """, unsafe_allow_html=True)
