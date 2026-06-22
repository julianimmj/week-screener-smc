"""
Week Screener SMC - Streamlit App
Screener Institucional para Ações da B3 com lógica SMC (Smart Money Concepts) - Timeframe Semanal (W1)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

import importlib
import screener_logic
importlib.reload(screener_logic)
from screener_logic import run_screener, detect_smc_signals

# ─── Keep-Alive: impede o Streamlit Cloud de adormecer enquanto o usuário está na página
components.html("""
<script>
(function keepAlive() {
    setInterval(function() {
        fetch(window.location.href, {method: 'HEAD', mode: 'no-cors'}).catch(function(){});
    }, 300000); // 5 minutos
})();
</script>
""", height=0)

try:
    _tickers_df = pd.read_csv('tickers_b3.csv')
    TOTAL_TICKERS = len(_tickers_df)
except Exception:
    TOTAL_TICKERS = 194

st.set_page_config(
    page_title="Week Screener SMC",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

:root {
  --bg:       #07071a;
  --bg-mid:   #0c0c24;
  --glass:    rgba(255,255,255,0.045);
  --glass2:   rgba(255,255,255,0.08);
  --accent:   #4f8ef7;
  --accent2:  #8b5cf6;
  --green:    #10d9a0;
  --red:      #f4436c;
  --gold:     #f5c842;
  --purple:   #a78bfa;
  --t1:       #f1f1fa;
  --t2:       #8b8baa;
  --t3:       #4a4a68;
  --border:   rgba(255,255,255,0.07);
  --border-a: rgba(79,142,247,0.28);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--t1);
}
.block-container {
    padding-top: 0 !important;
    max-width: 100% !important;
}
/* Streamlit branding — gerenciado pelo bloco hide_streamlit_style */
.stApp {
    background:
        radial-gradient(ellipse 100% 50% at 50% -5%, rgba(79,142,247,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 90% 80%, rgba(139,92,246,0.09) 0%, transparent 55%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-mid) 100%) !important;
}

/* ══════════ NAVBAR ══════════ */
.nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 52px;
    background: rgba(7,7,26,0.92);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 999;
}
.nav-brand {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.98rem; font-weight: 800; color: var(--t1);
}
.nav-brand .ac {
    background: linear-gradient(90deg, var(--accent), var(--purple));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.nav-pills { display: flex; gap: 7px; }
.pill {
    font-size: 0.63rem; font-weight: 600; letter-spacing: 0.9px;
    text-transform: uppercase; padding: 3px 10px;
    border-radius: 999px; border: 1px solid var(--border); color: var(--t3);
}
.pill.bl { color: var(--accent);  border-color: rgba(79,142,247,0.3);  background: rgba(79,142,247,0.06); }
.pill.gr { color: var(--green);   border-color: rgba(16,217,160,0.3);  background: rgba(16,217,160,0.06); }
.pill.pu { color: var(--purple);  border-color: rgba(167,139,250,0.3); background: rgba(167,139,250,0.06); }

/* ══════════ HERO ══════════ */
.hero {
    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 44px;
    align-items: center;
    padding: 48px 52px 40px;
    max-width: 1360px;
    margin: 0 auto;
}
.eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--accent);
    background: rgba(79,142,247,0.08); border: 1px solid rgba(79,142,247,0.25);
    padding: 4px 12px; border-radius: 999px; margin-bottom: 18px;
}
.h1 {
    font-size: 3rem; font-weight: 900; letter-spacing: -1.8px;
    line-height: 1.05; color: var(--t1); margin-bottom: 5px;
}
.h1 .g {
    background: linear-gradient(130deg, #82b4ff 0%, #c4a4ff 50%, #82b4ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shim 5s linear infinite;
}
@keyframes shim { to { background-position: 200% center; } }
.ver { font-size: 0.76rem; color: var(--t3); margin-bottom: 14px; display: block; }
.hdesc { font-size: 0.95rem; color: var(--t2); line-height: 1.72; max-width: 460px; margin-bottom: 20px; }
.hdesc strong { color: var(--t1); font-weight: 600; }

/* Inline checks */
.checks { display: flex; flex-wrap: wrap; gap: 7px 16px; margin-bottom: 24px; }
.ck {
    display: flex; align-items: center; gap: 7px;
    font-size: 0.8rem; color: var(--t2);
}
.ck::before {
    content: '✓'; width: 17px; height: 17px; border-radius: 5px;
    background: rgba(16,217,160,0.12); border: 1px solid rgba(16,217,160,0.28);
    color: var(--green); font-size: 0.65rem; font-weight: 800;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

/* Panel */
.panel {
    background: var(--glass); border: 1px solid var(--border);
    border-radius: 16px; overflow: hidden;
    backdrop-filter: blur(24px); box-shadow: 0 6px 40px rgba(0,0,0,0.3);
    position: relative;
}
.panel::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(79,142,247,0.5) 40%, rgba(139,92,246,0.5) 60%, transparent);
}
.pbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 11px 16px; border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,0.02);
}
.ptitle { font-size: 0.65rem; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; color: var(--t3); }
.live { display: flex; align-items: center; gap: 5px; font-size: 0.63rem; font-weight: 600; color: var(--green); }
.dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); animation: blink 2s ease infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.pbody { padding: 10px 12px 8px; }
.prow {
    display: grid; grid-template-columns: 72px 58px 1fr 84px;
    align-items: center; gap: 8px; padding: 8px 10px;
    border-radius: 8px; margin-bottom: 4px; transition: background 0.15s;
}
.prow:hover { background: rgba(255,255,255,0.03); }
.tk { font-size: 0.84rem; font-weight: 800; color: var(--t1); }
.st { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.4px; padding: 2px 7px; border-radius: 4px; text-align: center; }
.st.b { color: var(--accent);  background: rgba(79,142,247,0.13); }
.st.c { color: var(--purple);  background: rgba(167,139,250,0.13); }
.dr { font-size: 0.7rem; font-weight: 600; }
.up { color: var(--green); } .dn { color: var(--red); }
.zn { font-size: 0.65rem; color: var(--t3); text-align: right; }
.pfoot {
    display: flex; justify-content: space-between;
    padding: 9px 12px; border-top: 1px solid var(--border);
    font-size: 0.63rem; color: var(--t3); background: rgba(255,255,255,0.02);
}

/* ══════════ STATS BAR ══════════ */
.stats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,0.015);
}
.stat { padding: 22px 16px; text-align: center; border-right: 1px solid var(--border); transition: background 0.2s; }
.stat:last-child { border-right: none; }
.stat:hover { background: rgba(255,255,255,0.02); }
.snum {
    font-size: 2rem; font-weight: 900; letter-spacing: -1px; line-height: 1;
    background: linear-gradient(130deg, var(--accent), var(--purple));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    display: block; margin-bottom: 5px;
}
.slbl { font-size: 0.67rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.9px; color: var(--t3); margin-bottom: 2px; }
.ssub { font-size: 0.62rem; color: rgba(74,74,104,0.7); }

/* ══════════ MTF FLOW (destaque) ══════════ */
.flow-band {
    background: rgba(79,142,247,0.05);
    border-top: 1px solid rgba(79,142,247,0.15);
    border-bottom: 1px solid rgba(79,142,247,0.15);
    padding: 32px 52px;
}
.flow-inner { max-width: 1360px; margin: 0 auto; }
.flow-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 26px;
}
.flow-badge {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 1.3px;
    text-transform: uppercase; color: var(--accent);
    background: rgba(79,142,247,0.1); border: 1px solid rgba(79,142,247,0.25);
    padding: 3px 10px; border-radius: 6px; flex-shrink: 0;
}
.flow-ttl {
    font-size: 1rem; font-weight: 700; color: var(--t1); letter-spacing: -0.2px;
}
.flow-ttl span { color: var(--accent); }
.steps {
    display: grid; grid-template-columns: repeat(6, 1fr);
    gap: 0; position: relative;
}
.steps::before {
    content: ''; position: absolute;
    top: 18px; left: 5%; right: 5%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-a) 20%, var(--border-a) 80%, transparent);
}
.step { text-align: center; padding: 0 8px; }
.scir {
    width: 36px; height: 36px; border-radius: 50%;
    background: var(--bg-mid); border: 1px solid var(--border-a);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 800; color: var(--accent);
    margin: 0 auto 12px; position: relative; z-index: 1;
}
.snam { font-size: 0.72rem; font-weight: 700; color: var(--t1); margin-bottom: 4px; line-height: 1.25; }
.sdsc { font-size: 0.62rem; color: var(--t3); line-height: 1.4; }

/* ══════════ FEATURE CARDS ══════════ */
.feat-section { padding: 32px 52px 28px; max-width: 1360px; margin: 0 auto; }
.feat-sec-head { margin-bottom: 20px; }
.feat-ey { font-size: 0.62rem; font-weight: 700; letter-spacing: 1.8px; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }
.feat-ttl { font-size: 1.2rem; font-weight: 800; letter-spacing: -0.3px; color: var(--t1); }

/* Small feature card rendered in columns */
.fcard {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 20px;
    backdrop-filter: blur(20px);
    position: relative; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    height: 100%;
}
.fcard:hover {
    transform: translateY(-3px);
    border-color: var(--border-a);
    box-shadow: 0 12px 36px rgba(79,142,247,0.09);
}
.fcard::after {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(79,142,247,0.05), transparent);
    pointer-events: none;
}
.fiw {
    width: 38px; height: 38px; border-radius: 10px;
    background: var(--glass2); border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; margin-bottom: 13px;
}
.fttl { font-size: 0.95rem; font-weight: 700; color: var(--t1); margin-bottom: 7px; }
.fdsc { font-size: 0.83rem; color: var(--t2); line-height: 1.6; }
.fstp { margin-top: 12px; font-size: 0.65rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--accent); opacity: 0.6; }

/* ══════════ CTA FOOTER ══════════ */
.disc-bar {
    font-size: 0.71rem; color: rgba(245,200,66,0.5);
    background: rgba(245,200,66,0.03);
    border-top: 1px solid rgba(245,200,66,0.08);
    padding: 12px 40px; text-align: center; line-height: 1.6;
}

/* ══════════ SCREENER PAGE ══════════ */
.mtf-note {
    background: rgba(79,142,247,0.07); border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0; padding: 12px 16px;
    font-size: 0.82rem; color: var(--t2); margin-top: 12px; line-height: 1.65;
}
div[data-testid="metric-container"] {
    background: var(--glass) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; padding: 16px !important;
}
/* ══ CTA principal ══ */
.stButton > button {
    background: linear-gradient(130deg, var(--accent), var(--accent2)) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 12px 28px !important; transition: opacity 0.2s, transform 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover { opacity: 0.86 !important; transform: translateY(-1px) !important; }

/* ══ Sidebar nav buttons ══ */
.btn-nav [data-testid="stButton"] button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    color: var(--t1) !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    padding: 10px 14px !important;
    transition: background 0.18s, border-color 0.18s !important;
    background-image: none !important; box-shadow: none !important;
}
.btn-nav [data-testid="stButton"] button:hover {
    opacity: 1 !important; background: rgba(79,142,247,0.1) !important;
    border-color: rgba(79,142,247,0.35) !important; transform: none !important;
}

/* ══ Back button (topo da página) ══ */
.btn-back [data-testid="stButton"] button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    color: var(--t2) !important; border-radius: 8px !important;
    font-size: 0.8rem !important; padding: 7px 14px !important;
    width: auto !important; font-weight: 600 !important;
    background-image: none !important; box-shadow: none !important;
}
.btn-back [data-testid="stButton"] button:hover {
    opacity: 1 !important; border-color: var(--accent) !important;
    color: var(--accent) !important; transform: none !important;
}

/* ══ Filter tabs — base ══ */
.filter-tab [data-testid="stButton"] button {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: var(--t2) !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.8rem !important;
    padding: 10px 6px !important;
    transition: all 0.18s !important;
    background-image: none !important; box-shadow: none !important;
}
.filter-tab [data-testid="stButton"] button:hover {
    opacity: 1 !important;
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.18) !important;
    color: var(--t1) !important; transform: none !important;
}
/* Ativas */
.filter-tab.ft-all.active [data-testid="stButton"] button {
    background: rgba(79,142,247,0.16) !important;
    border-color: rgba(79,142,247,0.55) !important;
    color: var(--accent) !important; font-weight: 800 !important;
}
.filter-tab.ft-bull.active [data-testid="stButton"] button {
    background: rgba(16,217,160,0.13) !important;
    border-color: rgba(16,217,160,0.5) !important;
    color: var(--green) !important; font-weight: 800 !important;
}
.filter-tab.ft-bear.active [data-testid="stButton"] button {
    background: rgba(244,67,108,0.13) !important;
    border-color: rgba(244,67,108,0.5) !important;
    color: var(--red) !important; font-weight: 800 !important;
}
.filter-tab.ft-bos.active [data-testid="stButton"] button {
    background: rgba(79,142,247,0.13) !important;
    border-color: rgba(79,142,247,0.45) !important;
    color: var(--accent) !important; font-weight: 800 !important;
}
.filter-tab.ft-choch.active [data-testid="stButton"] button {
    background: rgba(167,139,250,0.13) !important;
    border-color: rgba(167,139,250,0.45) !important;
    color: var(--purple) !important; font-weight: 800 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07071a, #0c0c24) !important;
    border-right: 1px solid var(--border) !important;
}

/* ══════════ MOBILE RESPONSIVNESS ══════════ */
@media (max-width: 768px) {
    .h1 { font-size: 2.5rem; line-height: 1.1; }
    .nav { flex-direction: column; align-items: flex-start; gap: 12px; }
    .nav-pills { flex-wrap: wrap; justify-content: flex-start; }
    .stats { grid-template-columns: repeat(2, 1fr); }
    .stat { border-bottom: 1px solid var(--border); }
    .stat:nth-child(2n) { border-right: none; }
    .flow-band, .feat-section { padding: 20px 15px; }
    .steps { grid-template-columns: repeat(2, 1fr); gap: 25px; }
    .steps::before { display: none; }
    .prow { grid-template-columns: auto auto; justify-content: space-between; row-gap: 8px; }
    .zn { text-align: right; }
}
</style>
""", unsafe_allow_html=True)


# ─── Session state ───────────────────────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'signals_df' not in st.session_state:
    st.session_state.signals_df = None
if 'last_run' not in st.session_state:
    st.session_state.last_run = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'all'
if 'filter_zone' not in st.session_state:
    st.session_state.filter_zone = 'Todas'
if 'max_dist_poi' not in st.session_state:
    st.session_state.max_dist_poi = 15
if 'min_rr' not in st.session_state:
    st.session_state.min_rr = 0.0


# ─── Landing Page ────────────────────────────────────────────────────────────────
def landing_page():

    # 1 ── Navbar ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="nav">
        <div class="nav-brand">📅&nbsp;&nbsp;<span class="ac">Week Screener SMC</span></div>
        <div class="nav-pills">
            <span class="pill bl">B3 · Bovespa</span>
            <span class="pill pu">ICT / SMC 2025–2026 · W1</span>
            <span class="pill gr">● Ao Vivo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2 ── Hero: 2 colunas Streamlit nativas (botão alinhado com o título)
    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        # Título e descrição em HTML puro — sem padding-left manual
        st.markdown(f"""
        <div style="padding: 40px 0 20px 0;">
          <div class="eyebrow">⚡ Smart Money Concepts · Institucional</div>
          <div class="h1">Week Screener<br><span class="g">SMC para a B3</span></div>
          <span class="ver">W1 &nbsp;·&nbsp; Yahoo Finance &nbsp;·&nbsp; Timeframe Semanal</span>
          <div class="hdesc">
            Varredura diária de <strong>{TOTAL_TICKERS} ativos</strong> da B3 — ações, ETFs, BDRs e FIIs —
            com lógica institucional: sweep confirmado, BOS/CHOCH validado, OBs, FVGs e Fibonacci.
          </div>
          <div class="checks">
            <div class="ck">Sweep de liquidez obrigatório</div>
            <div class="ck">BOS/CHOCH por close de corpo</div>
            <div class="ck">Order Blocks + FVG confluentes</div>
            <div class="ck">Fibonacci Discount/Premium</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_right:
        st.markdown(f"""
        <div style="padding: 40px 0 20px 24px;">
          <div class="panel">
            <div class="pbar" style="position: relative;">
              <span class="ptitle">📊 Sinais Ativos — W1</span>
              <span style="position: absolute; left: 50%; transform: translateX(-50%); font-size: 0.55rem; color: #f4436c; font-weight: 800; background: rgba(244,67,108,0.1); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(244,67,108,0.3); text-transform: uppercase; white-space: nowrap;">⚠️ Modelo Ilustrativo</span>
              <div class="live"><div class="dot"></div> Atualizado hoje</div>
            </div>
            <div class="pbody">
              <div class="prow"><span class="tk">PETR4</span><span class="st b">BOS</span><span class="dr up">▲ Alta</span><span class="zn">🔵 Discount</span></div>
              <div class="prow"><span class="tk">VALE3</span><span class="st c">CHOCH</span><span class="dr dn">▼ Baixa</span><span class="zn">🟡 Premium</span></div>
              <div class="prow"><span class="tk">WEGE3</span><span class="st b">BOS</span><span class="dr up">▲ Alta</span><span class="zn">🔵 Discount</span></div>
              <div class="prow"><span class="tk">ITUB4</span><span class="st b">BOS</span><span class="dr dn">▼ Baixa</span><span class="zn">🟡 Premium</span></div>
              <div class="prow"><span class="tk">BBDC4</span><span class="st c">CHOCH</span><span class="dr up">▲ Alta</span><span class="zn">🔵 Discount</span></div>
            </div>
            <div class="pfoot">
              <span>{TOTAL_TICKERS} ativos verificados</span><span>Ações · ETFs · BDRs · FIIs</span><span>W1 semanal</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # 3 ── Botões de Ação Centralizados ───────────────────────────────────────────
    st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)
    bcol_spacer1, bcol_mid1, bcol_mid2, bcol_spacer2 = st.columns([1, 1.2, 1.2, 1])
    with bcol_mid1:
        if st.button("🚀  Realizar Novo Screener", key="btn_start", use_container_width=True):
            st.session_state.signals_df = None   # sempre força novo scan 
            st.session_state.active_tab = 'all'
            st.session_state.page = 'screener'
            st.rerun()
    with bcol_mid2:
        if st.button("⏱️ Ver Último Resultado", key="btn_quick", use_container_width=True):
            loaded = False
            
            # Se já está na memória, não precisa ler de arquivo
            if st.session_state.signals_df is not None:
                loaded = True
            else:
                # 1. Tenta carregar localmente (funciona se o container não reiniciou)
                try:
                    import os
                    if os.path.exists("latest_scan.csv"):
                        df_saved = pd.read_csv("latest_scan.csv")
                        if not df_saved.empty:
                            st.session_state.signals_df = df_saved
                            loaded = True
                            if os.path.exists("latest_run.txt"):
                                with open("latest_run.txt", "r") as f:
                                    st.session_state.last_run = datetime.datetime.fromisoformat(f.read().strip())
                except Exception:
                    pass
                
                # 2. Tenta carregar do GitHub (dados commitados pelo Actions ou manualmente)
                if not loaded:
                    try:
                        import io
                        from github import Github
                        
                        # Usa token se disponível; caso contrário tenta acesso público
                        gh_token = st.secrets.get("GITHUB_TOKEN", None) if hasattr(st, 'secrets') else None
                        g = Github(gh_token) if gh_token else Github()
                        repo = g.get_repo("julianimmj/week-screener-smc")
                        
                        # Tenta branch 'main' primeiro, depois 'master' como fallback
                        csv_data = None
                        for branch in ["main", "master"]:
                            try:
                                contents = repo.get_contents("latest_scan.csv", ref=branch)
                                csv_data = contents.decoded_content.decode('utf-8')
                                break  # Encontrou, sai do loop
                            except Exception:
                                continue  # Tenta próximo branch
                        
                        if csv_data:
                            df_saved = pd.read_csv(io.StringIO(csv_data))
                            if not df_saved.empty:
                                st.session_state.signals_df = df_saved
                                loaded = True
                                # Cache local para evitar re-download
                                df_saved.to_csv("latest_scan.csv", index=False)
                                
                                # Carrega o timestamp da última execução
                                for branch in ["main", "master"]:
                                    try:
                                        contents_run = repo.get_contents("latest_run.txt", ref=branch)
                                        run_data = contents_run.decoded_content.decode('utf-8').strip()
                                        st.session_state.last_run = datetime.datetime.fromisoformat(run_data)
                                        with open("latest_run.txt", "w") as f:
                                            f.write(run_data)
                                        break
                                    except Exception:
                                        continue
                    except Exception as ex:
                        # Silencia erros de rede/API — o toast abaixo já informa o usuário
                        pass
            
            if loaded:
                if st.session_state.last_run:
                    st.toast(f"✅ Resultado carregado — {st.session_state.last_run.strftime('%d/%m/%Y às %H:%M')}", icon="✅")
                st.session_state.active_tab = 'all'
                st.session_state.page = 'screener'
                st.rerun()
            else:
                st.toast("⚠️ Nenhum resultado prévio encontrado. Use 'Realizar Novo Screener'.", icon="⚠️")


    # 4 ── Email Registration Form ────────────────────────────────────────────────
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:var(--border);margin: 0 0 40px 0;"></div>', unsafe_allow_html=True)
    
    ecol1, ecol2, ecol3 = st.columns([1, 2, 1])
    with ecol2:
        st.markdown("""
        <div style="text-align:center; margin-bottom: 20px;">
            <div style="font-size: 1.3rem; font-weight: 800; color:var(--t1);">Assinar Alerta Semanal SMC 📩</div>
            <div style="font-size: 0.85rem; color:var(--t3); margin-top: 5px;">Receba um e-mail toda semana sempre que um sinal institucional de alta probabilidade for formado na B3.</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_email_footer"):
            email_input = st.text_input("Endereço de E-mail", placeholder="exemplo@gmail.com", label_visibility="collapsed")
            submitted = st.form_submit_button("🔔  Me avisar quando houver sinais", use_container_width=True)
            if submitted and email_input:
                import json
                email_added = False

                # Tenta salvar no GitHub (produção)
                try:
                    if "GITHUB_TOKEN" not in st.secrets:
                        st.warning("⚠️ Token do GitHub ausente! O e-mail será salvo apenas na memória provisória até o reinício do servidor.")
                        raise KeyError("Missing GITHUB_TOKEN")
                        
                    from github import Github
                    gh_token = st.secrets["GITHUB_TOKEN"]
                    g = Github(gh_token)
                    repo = g.get_repo("julianimmj/week-screener-smc")
                    contents = repo.get_contents("emails.json", ref="main")
                    data_gh = json.loads(contents.decoded_content.decode())

                    if email_input not in data_gh.get("emails", []):
                        data_gh.setdefault("emails", []).append(email_input)
                        repo.update_file(contents.path, f"subs: add {email_input}", json.dumps(data_gh, indent=2), contents.sha, branch="main")
                        email_added = True
                    else:
                        st.info("📧 E-mail já está na lista.")
                except Exception as ex:
                    if "Missing GITHUB_TOKEN" not in str(ex):
                        st.error(f"Erro ao salvar e-mail na nuvem (GitHub): {ex}")
                        
                    # Fallback: salva localmente
                    try:
                        with open("emails.json", "r") as f:
                            data = json.load(f)
                        if email_input not in data.get("emails", []):
                            data.setdefault("emails", []).append(email_input)
                            with open("emails.json", "w") as f:
                                json.dump(data, f)
                            email_added = True
                        else:
                            st.info("📧 E-mail já está na lista provisória.")
                    except Exception as e:
                        st.error(f"Erro fatal ao salvar e-mail localmente: {e}")

                if email_added:
                    st.success("✅ E-mail cadastrado com sucesso! Te avisaremos do próximo setup.")
                    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    # ── Stats bar compacta ────────────────────────────────────────────────────────
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f'<div style="text-align:center;padding:8px 0;"><span class="snum" style="font-size:1.4rem;">{TOTAL_TICKERS}</span><div class="slbl">Ativos</div></div>', unsafe_allow_html=True)
    with col_s2:
        st.markdown('<div style="text-align:center;padding:8px 0;"><span class="snum" style="font-size:1.4rem;">W1</span><div class="slbl">Timeframe</div></div>', unsafe_allow_html=True)
    with col_s3:
        st.markdown('<div style="text-align:center;padding:8px 0;"><span class="snum" style="font-size:1.4rem;">6</span><div class="slbl">Validações</div></div>', unsafe_allow_html=True)
    with col_s4:
        st.markdown('<div style="text-align:center;padding:8px 0;"><span class="snum" style="font-size:1.4rem;">RR≥0</span><div class="slbl">Todos Sinais</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:2px;background:linear-gradient(90deg,transparent,rgba(79,142,247,0.2),transparent);margin:0 0 4px;"></div>', unsafe_allow_html=True)

    # 3 ── Fluxo MTF em destaque ──────────────────────────────────────────────────
    st.markdown("""
    <div class="flow-band">
      <div class="flow-inner">
        <div class="flow-header">
          <span class="flow-badge">📋 Metodologia MTF</span>
          <div class="flow-ttl">Fluxo de Execução <span>Multi-Timeframe</span> — como usar os sinais</div>
        </div>
        <div class="steps">
          <div class="step"><div class="scir">01</div><div class="snam">Sinal no W1</div><div class="sdsc">BOS ou CHOCH com close de corpo confirmado</div></div>
          <div class="step"><div class="scir">02</div><div class="snam">POI Mapeado</div><div class="sdsc">OB, FVG ou Fibonacci 50% como zona alvo</div></div>
          <div class="step"><div class="scir">03</div><div class="snam">Aguarde o Preço</div><div class="sdsc">Espere retorno ao POI no W1</div></div>
          <div class="step"><div class="scir">04</div><div class="snam">Confirme no LTF</div><div class="sdsc">CHOCH interno no D1 ou H4</div></div>
          <div class="step"><div class="scir">05</div><div class="snam">Entrada e SL</div><div class="sdsc">Início do OB. SL no strong level</div></div>
          <div class="step"><div class="scir">06</div><div class="snam">Alvo e Parciais</div><div class="sdsc">TP no weak high/low oposto</div></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 ── Feature Cards (compactos, 2 linhas de 3) ───────────────────────────────
    st.markdown("""
    <div class="feat-section">
      <div class="feat-sec-head">
        <div class="feat-ey">O que é analisado</div>
        <div class="feat-ttl">6 Camadas de Validação — Sinal ou Descarte</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    CARDS = [
        ("💧", "Liquidity Sweeps",
         "Wick valida topo/fundo. Estruturas sem sweep são descartadas automaticamente.",
         "→ Passo 1"),
        ("🏗️", "Strong High / Low",
         "Apenas níveis protegidos por sweep servem de referência para BOS/CHOCH.",
         "→ Passo 2"),
        ("🎯", "BOS & CHOCH",
         "BOS = continuação. CHOCH = reversão. Ambos exigem close de corpo confirmado.",
         "→ Passo 3"),
        ("📐", "Fibonacci 50%",
         "Discount abaixo de 50% (compra). Premium acima (venda). Filtro automático.",
         "→ Passo 4"),
        ("🧱", "Order Blocks + FVG",
         "Última vela contrária + Fair Value Gap de 3 velas. POIs de alta confluência.",
         "→ Passo 5"),
        ("📊", "Gráfico SMC",
         "Candlestick interativo com marks de sweeps, BOS/CHOCH, OBs e Fibonacci.",
         "→ Visualização"),
    ]

    st.markdown('<div style="padding: 0 52px 0;">', unsafe_allow_html=True)
    r1 = st.columns(3, gap="medium")
    for idx, (icon, title, desc, step) in enumerate(CARDS[:3]):
        with r1[idx]:
            st.markdown(f"""
            <div class="fcard">
                <div class="fiw">{icon}</div>
                <div class="fttl">{title}</div>
                <div class="fdsc">{desc}</div>
                <div class="fstp">{step}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # espaçamento entre linhas de cards
    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 52px 28px;">', unsafe_allow_html=True)
    r2 = st.columns(3, gap="medium")
    for idx, (icon, title, desc, step) in enumerate(CARDS[3:]):
        with r2[idx]:
            st.markdown(f"""
            <div class="fcard">
                <div class="fiw">{icon}</div>
                <div class="fttl">{title}</div>
                <div class="fdsc">{desc}</div>
                <div class="fstp">{step}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 5 ── Disclaimer ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="disc-bar">
        ⚠️&nbsp; <strong>Isenção de Responsabilidade:</strong>&nbsp;
        Ferramenta exclusivamente de análise técnica. Não constitui aconselhamento financeiro
        nem recomendação de investimento. Sempre consulte um profissional habilitado antes de operar.
    </div>
    """, unsafe_allow_html=True)


# ─── Chart Builder ───────────────────────────────────────────────────────────────
def build_chart(df: pd.DataFrame, ticker: str, trade_info: dict = None) -> go.Figure:
    df_plot = df.tail(200).copy().reset_index(drop=True)
    x_axis = (pd.to_datetime(df_plot['Date']).dt.strftime('%Y-%m-%d')
               if 'Date' in df_plot.columns else list(range(len(df_plot))))

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        row_heights=[0.75, 0.25],
                        subplot_titles=[f"📅 {ticker} — SMC Chart (W1)", "Volume"])

    fig.add_trace(go.Candlestick(
        x=x_axis, open=df_plot['Open'], high=df_plot['High'],
        low=df_plot['Low'], close=df_plot['Close'], name='Preço',
        increasing_line_color='#10d9a0', decreasing_line_color='#f4436c',
        increasing_fillcolor='rgba(16,217,160,0.7)',
        decreasing_fillcolor='rgba(244,67,108,0.7)',
    ), row=1, col=1)

    colors_vol = ['#10d9a0' if c >= o else '#f4436c'
                  for c, o in zip(df_plot['Close'], df_plot['Open'])]
    fig.add_trace(go.Bar(x=x_axis, y=df_plot['Volume'], name='Volume',
                         marker_color=colors_vol, opacity=0.55), row=2, col=1)

    # Apenas os BOS/CHOCH dos últimos 60 candles visíveis (evita poluição de sinais antigos)
    recent_start = max(0, len(df_plot) - 60)
    for col_name, label, color, dash in [
        ('bos_bull',   'BOS ▲',   'rgba(16,217,160,0.65)', 'dash'),
        ('bos_bear',   'BOS ▼',   'rgba(244,67,108,0.65)', 'dash'),
        ('choch_bull', 'CHOCH ▲', 'rgba(167,139,250,0.8)', 'dot'),
        ('choch_bear', 'CHOCH ▼', 'rgba(167,139,250,0.8)', 'dot'),
    ]:
        if col_name in df_plot.columns:
            events = df_plot[(df_plot[col_name] == True) & (df_plot.index >= recent_start)]
            for idx in events.index:
                x_val = x_axis[idx]
                fig.add_shape(type="line", x0=x_val, x1=x_val, y0=0, y1=1, xref='x', yref='paper',
                              line=dict(color=color, width=1.5, dash=dash))
                fig.add_annotation(x=x_val, y=0.96, yref='paper', text=label,
                                   showarrow=False, font=dict(color=color, size=10))

    if 'bull_sweep' in df_plot.columns:
        sw = df_plot[(df_plot['bull_sweep'] == True) & (df_plot.index >= recent_start)]
        if not sw.empty:
            fig.add_trace(go.Scatter(
                x=[x_axis[i] for i in sw.index], y=sw['Low'] * 0.9975,
                mode='markers', marker=dict(symbol='triangle-up', size=9, color='#10d9a0'),
                name='Bull Sweep'), row=1, col=1)

    if 'bear_sweep' in df_plot.columns:
        sw = df_plot[(df_plot['bear_sweep'] == True) & (df_plot.index >= recent_start)]
        if not sw.empty:
            fig.add_trace(go.Scatter(
                x=[x_axis[i] for i in sw.index], y=sw['High'] * 1.0025,
                mode='markers', marker=dict(symbol='triangle-down', size=9, color='#f4436c'),
                name='Bear Sweep'), row=1, col=1)

    # Apenas o ÚLTIMO strong_low e strong_high ativos (não todos os históricos)
    if 'strong_low' in df_plot.columns:
        sl_rows = df_plot[df_plot['strong_low'] == True]
        if not sl_rows.empty:
            last_sl = sl_rows.iloc[-1]
            fig.add_hline(y=last_sl['Low'], line_width=1, line_dash='dot',
                          line_color='rgba(16,217,160,0.4)',
                          annotation_text=f" Strong Low ({last_sl['Low']:.2f})",
                          annotation_position="bottom right",
                          annotation_font=dict(color='rgba(16,217,160,0.6)', size=9))

    if 'strong_high' in df_plot.columns:
        sh_rows = df_plot[df_plot['strong_high'] == True]
        if not sh_rows.empty:
            last_sh = sh_rows.iloc[-1]
            fig.add_hline(y=last_sh['High'], line_width=1, line_dash='dot',
                          line_color='rgba(244,67,108,0.4)',
                          annotation_text=f" Strong High ({last_sh['High']:.2f})",
                          annotation_position="top right",
                          annotation_font=dict(color='rgba(244,67,108,0.6)', size=9))

    if trade_info:
        entry = trade_info.get('entry')
        sl = trade_info.get('sl')
        tp = trade_info.get('tp')
        signal_dir = trade_info.get('signal', 'bull')
        
        # Invisible points to force Plotly to scale the Y-axis to include SL and TP
        last_x = x_axis.iloc[-1] if hasattr(x_axis, 'iloc') else x_axis[-1]
        fig.add_trace(go.Scatter(x=[last_x, last_x], y=[sl, tp], mode='markers', 
                                 marker=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'), row=1, col=1)
        
        entry_label = "⏳ Entrada POI" if signal_dir == 'bull' else "⏳ Entrada POI"
        fig.add_hline(y=entry, line_width=1.5, line_dash='dashdot', line_color='#4f8ef7',
                      annotation_text=f" {entry_label} ({entry:.2f})", annotation_position="top left",
                      annotation_font=dict(color='#4f8ef7', size=11, family='Inter'))
        fig.add_hline(y=sl, line_width=1.5, line_color='#f4436c',
                      annotation_text=f" 🛑 Stop Loss ({sl:.2f})", annotation_position="bottom left",
                      annotation_font=dict(color='#f4436c', size=11, family='Inter'))
        fig.add_hline(y=tp, line_width=1.5, line_color='#10d9a0',
                      annotation_text=f" 🎯 Alvo ({tp:.2f})", annotation_position="top left",
                      annotation_font=dict(color='#10d9a0', size=11, family='Inter'))

    fig.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(7,7,26,0)', plot_bgcolor='rgba(7,7,26,0)',
        font=dict(family='Inter', color='#f1f1fa', size=12),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
                    bgcolor='rgba(7,7,26,0.5)', bordercolor='rgba(79,142,247,0.25)'),
        margin=dict(l=10, r=40, t=50, b=10), height=540)
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.04)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.04)', side='right', row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.04)', side='right', row=2, col=1)
    return fig


# ─── Screener Page ───────────────────────────────────────────────────────────────
def screener_page():

    # ─── SIDEBAR ──────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding:4px 0 12px;">
            <div style="font-size:1rem;font-weight:800;color:var(--t1);letter-spacing:-0.2px;">
                📅 Week <span style="background:linear-gradient(90deg,var(--accent),var(--purple));
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;">Screener SMC</span>
            </div>
            <div style="font-size:0.68rem;color:var(--t3);margin-top:3px;">W1 · B3 · ICT/SMC 2025-2026</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Navegação</div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-nav">', unsafe_allow_html=True)
        if st.button("🏠  Página Inicial", key="btn_home", use_container_width=True):
            st.session_state.page = 'landing'
            st.session_state.active_tab = 'all'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-nav">', unsafe_allow_html=True)
        if st.button("🔄  Novo Scan", key="btn_rescan", use_container_width=True):
            st.session_state.signals_df = None
            st.session_state.active_tab = 'all'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("<div style='font-size:0.72rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>📋 Execução MTF</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="mtf-note" style="font-size:0.77rem;">
        1️⃣ Aguarde preço no POI (W1)<br>
        2️⃣ Mude para LTF D1/H4<br>
        3️⃣ Espere CHOCH interno no LTF<br>
        4️⃣ Entre com fluxo W1 alinhado<br>
        5️⃣ SL: strong level protegido<br>
        6️⃣ TP: weak high/low oposto
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        if st.session_state.last_run:
            st.caption(f"🕐 Última varredura: {st.session_state.last_run.strftime('%d/%m/%Y às %H:%M')}")
        else:
            st.caption("Sem varredura recente")

    # ─── CABEÇALHO ─────────────────────────────────────────────────────────────────
    hcol_l, hcol_r = st.columns([3, 1])
    with hcol_l:
        st.markdown("""
        <div style="padding:18px 4px 6px;">
            <h1 style="font-size:1.5rem;font-weight:800;letter-spacing:-0.3px;
                       background:linear-gradient(130deg,#f1f1fa,#8b8baa);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                       background-clip:text;margin:0;">
                📅 Week Screener SMC — Sinais Ativos
            </h1>
            <p style="color:var(--t3);margin-top:4px;font-size:0.74rem;letter-spacing:0.3px;">
                Varredura W1 &nbsp;·&nbsp; ICT/SMC 2025-2026 &nbsp;·&nbsp; Sweep Confirmado &nbsp;·&nbsp; Filtros Dinâmicos
            </p>

<div style="margin-top: 16px; margin-bottom: 8px; padding: 14px 18px; background: rgba(79,142,247,0.06); border-left: 3px solid #4f8ef7; border-radius: 6px; font-size: 0.82rem; color: #c6c6d3; line-height: 1.55;">
<strong style="color: #4f8ef7; font-size: 0.88rem;">🔍 Lógica Single-Fractal (W1):</strong><br>
Este algoritmo não possui uma "Visão Bifocal" (Macro vs Micro) simultânea. Ele enxerga o <b>Gráfico Semanal (W1)</b> como a Estrutura Macro absoluta.<br>
<div style="margin-top: 6px;">
<strong style="color: #f1f1fa;">O que isso significa na prática?</strong> Se o preço no W1 formar um topo, descer para corrigir, e durante a queda realizar um CHOCH Bearish no W1, o robô não pensará: <i>"Ah, isso é só um CHOCH interno de pullback da estrutura de alta"</i>. Ele vai <b>literalmente virar a mão</b>! Inverterá a tendência global para baixa e passará a procurar vendas.
</div>
</div>
        </div>
        """, unsafe_allow_html=True)
    with hcol_r:
        st.markdown('<div style="padding:22px 0 0;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-back">', unsafe_allow_html=True)
        if st.button("← Página Inicial", key="btn_back_top"):
            st.session_state.page = 'landing'
            st.session_state.active_tab = 'all'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:var(--border);margin:4px 0 16px;"></div>', unsafe_allow_html=True)

    # ─── CARREGAMENTO DE DADOS ──────────────────────────────────────────────────────
    if st.session_state.signals_df is None:
        with st.spinner(f"🔍 Varrendo {TOTAL_TICKERS} ativos no W1 (Ações · ETFs · BDRs · FIIs)... Aguarde (2-5 minutos)"):
            try:
                signals = run_screener('tickers_b3.csv')
                st.session_state.signals_df = signals
                st.session_state.last_run = datetime.datetime.now()
                
                # Salva localmente
                signals.to_csv("latest_scan.csv", index=False)
                with open("latest_run.txt", "w") as f:
                    f.write(st.session_state.last_run.isoformat())
                
                # Salva no GitHub se o token existir
                try:
                    if "GITHUB_TOKEN" in st.secrets:
                        from github import Github
                        gh_token = st.secrets["GITHUB_TOKEN"]
                        g = Github(gh_token)
                        repo = g.get_repo("julianimmj/week-screener-smc")
                        
                        csv_content = signals.to_csv(index=False)
                        run_content = st.session_state.last_run.isoformat()
                        
                        # Atualiza/Cria latest_scan.csv no GitHub
                        try:
                            contents = repo.get_contents("latest_scan.csv", ref="main")
                            repo.update_file(contents.path, f"chore: update latest_scan.csv [skip ci]", csv_content, contents.sha, branch="main")
                        except Exception:
                            repo.create_file("latest_scan.csv", "chore: create latest_scan.csv [skip ci]", csv_content, branch="main")
                            
                        # Atualiza/Cria latest_run.txt no GitHub
                        try:
                            contents_run = repo.get_contents("latest_run.txt", ref="main")
                            repo.update_file(contents_run.path, f"chore: update latest_run.txt [skip ci]", run_content, contents_run.sha, branch="main")
                        except Exception:
                            repo.create_file("latest_run.txt", "chore: create latest_run.txt [skip ci]", run_content, branch="main")
                except Exception as gh_ex:
                    print(f"Erro ao salvar cache no GitHub: {gh_ex}")
                    
            except Exception as e:
                st.error(f"Erro ao executar screener: {e}")
                st.session_state.signals_df = pd.DataFrame()

    signals_df = st.session_state.signals_df

    # Base dataset — todos os sinais válidos
    if signals_df is not None and not signals_df.empty:
        min_rr = st.session_state.get('min_rr', 0.0)
        base_df = signals_df[signals_df['RR'] >= min_rr].copy()
    else:
        base_df = pd.DataFrame()

    # Contagens totais por categoria (sempre do base_df completo)
    total_count = len(base_df)
    bull_count  = int((base_df['Sinal'] == 'bull').sum()) if not base_df.empty else 0
    bear_count  = int((base_df['Sinal'] == 'bear').sum()) if not base_df.empty else 0
    bos_count   = int((base_df['Tipo']  == 'BOS' ).sum()) if not base_df.empty else 0
    choch_count = int((base_df['Tipo']  == 'CHOCH').sum()) if not base_df.empty else 0

    # ─── ABAS DE FILTRO RÁPIDO ──────────────────────────────────────────────────────
    active_tab = st.session_state.get('active_tab', 'all')
    def set_tab(t): st.session_state.active_tab = t

    tab_defs = [
        ('all',   '🎯', 'Todos',  total_count,  'ft-all'),
        ('bull',  '🟢', 'Alta',   bull_count,   'ft-bull'),
        ('bear',  '🔴', 'Baixa',  bear_count,   'ft-bear'),
        ('bos',   '📈', 'BOS',    bos_count,    'ft-bos'),
        ('choch', '🔄', 'CHOCH',  choch_count,  'ft-choch'),
    ]
    col_tabs = st.columns(5, gap="small")
    for i, (tab_key, icon, label, count, css_cls) in enumerate(tab_defs):
        active_cls = 'active' if active_tab == tab_key else ''
        with col_tabs[i]:
            st.markdown(f'<div class="filter-tab {css_cls} {active_cls}">', unsafe_allow_html=True)
            st.button(f"{icon} {label} · {count}", key=f"ftab_{tab_key}",
                      on_click=set_tab, args=(tab_key,), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:var(--border);margin:14px 0 12px;"></div>', unsafe_allow_html=True)

    # ─── FILTROS RÁPIDOS (inline na tela principal) ────────────────────────────────
    fcol1, fcol2, fcol3 = st.columns(3, gap="medium")
    with fcol1:
        st.selectbox("Zona Fibonacci", ["Todas", "Discount", "Premium"],
                     key="filter_zone", label_visibility="visible")
    with fcol2:
        st.slider("Risco Retorno Mínimo", min_value=0.0, max_value=10.0,
                  step=0.5, key="min_rr", label_visibility="visible")
    with fcol3:
        st.slider("Dist. Máx. POI (%)", min_value=5, max_value=50,
                  step=5, key="max_dist_poi", label_visibility="visible",
                  help="Exibe apenas ativos cujo preço atual está próximo do POI")

    st.markdown('<div style="height:1px;background:var(--border);margin:4px 0 12px;"></div>', unsafe_allow_html=True)

    # ─── APLICAR FILTROS ────────────────────────────────────────────────────────────
    filtered = base_df.copy()
    if   active_tab == 'bull':  filtered = filtered[filtered['Sinal'] == 'bull']
    elif active_tab == 'bear':  filtered = filtered[filtered['Sinal'] == 'bear']
    elif active_tab == 'bos':   filtered = filtered[filtered['Tipo']  == 'BOS']
    elif active_tab == 'choch': filtered = filtered[filtered['Tipo']  == 'CHOCH']

    filter_zone = st.session_state.get('filter_zone', 'Todas')
    if filter_zone != 'Todas':
        zm = {'Discount': 'discount', 'Premium': 'premium', 'Reversal': 'reversal'}
        filtered = filtered[filtered['Zona'] == zm.get(filter_zone, filter_zone)]

    # Filtro de distância máxima ao POI
    max_dist = st.session_state.get('max_dist_poi', 15)
    if 'Dist. POI' in filtered.columns and not filtered.empty:
        dist_abs = filtered['Dist. POI'].str.replace('%', '', regex=False).str.replace('+', '', regex=False).astype(float).abs()
        filtered = filtered[dist_abs <= max_dist]

    # ─── TABELA DE RESULTADOS ───────────────────────────────────────────────────────
    if filtered.empty:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;">
            <div style="font-size:2.4rem;margin-bottom:12px;">🔍</div>
            <div style="font-size:1rem;color:var(--t2);">Nenhum sinal encontrado com os filtros aplicados.</div>
            <div style="font-size:0.78rem;color:var(--t3);margin-top:6px;">
                Tente outra aba ou altere a Zona Fibonacci no menu lateral.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab_label = {'all': 'Todos', 'bull': '🟢 Alta', 'bear': '🔴 Baixa',
                     'bos': 'BOS', 'choch': 'CHOCH'}.get(active_tab, 'Todos')
        zone_label = f" · Zona: {filter_zone}" if filter_zone != 'Todas' else ''
        st.markdown(
            f'<div style="font-size:0.77rem;color:var(--t3);margin-bottom:8px;">'
            f'Exibindo <strong style="color:var(--t1);">{len(filtered)}</strong> sinal(is) '
            f'— Filtro: <span style="color:var(--accent);">{tab_label}{zone_label}</span>'
            f'&nbsp;·&nbsp;RR &ge; {min_rr:.1f}</div>',
            unsafe_allow_html=True
        )

        display_df = filtered.drop(columns=['Nota MTF'], errors='ignore').copy()
        if 'Sinal' in display_df.columns:
            display_df['Sinal'] = display_df['Sinal'].apply(
                lambda x: '🟢 Bull' if x == 'bull' else '🔴 Bear')
        if 'Zona' in display_df.columns:
            display_df['Zona'] = display_df['Zona'].apply(
                lambda x: '🔵 Discount' if x == 'discount'
                else ('🟡 Premium' if x == 'premium'
                      else ('🟣 Reversal' if x == 'reversal' else (x or '—'))))

        st.dataframe(
            display_df,
            use_container_width=True,
            height=min(520, 80 + 38 * len(display_df)),
            hide_index=True,
            column_config={
                "Ticker":    st.column_config.TextColumn("Ticker",     width="small"),
                "Sinal":     st.column_config.TextColumn("Sinal",      width="small"),
                "Tipo":      st.column_config.TextColumn("Tipo",       width="small"),
                "Preço":     st.column_config.NumberColumn("Preço",    format="R$%.2f", width="small"),
                "POI":       st.column_config.TextColumn("POI",        width="medium"),
                "POI Preço": st.column_config.NumberColumn("POI Preço",format="R$%.2f", width="small"),
                "Zona":      st.column_config.TextColumn("Zona",       width="medium"),
                "SL":        st.column_config.NumberColumn("Stop Loss", format="R$%.2f", width="small"),
                "TP1":       st.column_config.NumberColumn("Alvo",      format="R$%.2f", width="small"),
                "RR":        st.column_config.NumberColumn("RR",        format="%.2fx",  width="small"),
                "Dist. POI": st.column_config.TextColumn("Dist. POI",  width="small"),
            }
        )

        st.divider()
        st.markdown("### 📊 Gráfico Interativo")
        tickers_available = filtered['Ticker'].unique().tolist()
        if tickers_available:
            selected_ticker = st.selectbox("Selecione o ativo para visualizar",
                                           tickers_available, key="chart_ticker")
            with st.spinner(f"Carregando gráfico de {selected_ticker}..."):
                try:
                    import yfinance as yf
                    ticker_obj = yf.Ticker(f"{selected_ticker}.SA")
                    df_raw = ticker_obj.history(period='5y', interval='1wk', auto_adjust=True)
                    df_raw = df_raw[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                    df_raw.dropna(inplace=True)
                    df_raw.reset_index(inplace=True)
                    if 'Date' not in df_raw.columns and 'Datetime' in df_raw.columns:
                        df_raw.rename(columns={'Datetime': 'Date'}, inplace=True)
                    df_raw.reset_index(drop=True, inplace=True)
                    df_analyzed = detect_smc_signals(df_raw)

                    mtf_row = filtered[filtered['Ticker'] == selected_ticker].iloc[0]
                    trade_info = {
                        'entry': float(mtf_row['POI Preço']),
                        'sl':    float(mtf_row['SL']),
                        'tp':    float(mtf_row['TP1']),
                        'signal': mtf_row['Sinal'],
                        'tipo':   mtf_row['Tipo']
                    }
                    fig = build_chart(df_analyzed, selected_ticker, trade_info=trade_info)
                    st.plotly_chart(fig, use_container_width=True)

                    dir_label = "📈 Alta (Bull)" if mtf_row['Sinal'] in ['bull', '🟢 Bull'] else "📉 Baixa (Bear)"
                    st.markdown(f"""
                    <div class="mtf-note">
                        <strong>{selected_ticker}</strong> — {dir_label}
                        | {mtf_row.get('Tipo', '—')} | Zona: {mtf_row.get('Zona', '—')}<br>
                        ⚠️ <em>Aguardar CHOCH interno no LTF (15min/1min) + alinhamento antes de operar.</em>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro ao gerar gráfico: {e}")


# ─── Router ─────────────────────────────────────────────────────────────────────
if st.session_state.page == 'landing':
    landing_page()
else:
    screener_page()
