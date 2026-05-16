# =============================================================================
# APP PRINCIPAL — IFRS Campus Farroupilha
# =============================================================================

import streamlit as st

st.set_page_config(
    page_title="Plano de Ação — IFRS Farroupilha",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Páginas ───────────────────────────────────────────────────────────────────

inicio       = st.Page("pages/inicio.py",       title="Início",       icon="🏠")
upload       = st.Page("pages/upload.py",        title="Upload",       icon="📤")
dashboard    = st.Page("pages/dashboard.py",     title="Dashboard",    icon="📊")
configuracao = st.Page("pages/configuracao.py",  title="Configuração", icon="⚙️")

# ── Navegação ─────────────────────────────────────────────────────────────────

nav = st.navigation([inicio, upload, dashboard, configuracao])

# ── Sidebar ───────────────────────────────────────────────────────────────────

import os

st.sidebar.caption("Sistema de Acompanhamento do Plano de Ação · 2026")

# ── Execução ──────────────────────────────────────────────────────────────────

nav.run()