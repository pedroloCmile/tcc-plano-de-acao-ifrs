# =============================================================================
# DASHBOARD DO PLANO DE AÇÃO 2026 — IFRS Campus Farroupilha
# Redesign: clean, moderno, organizado em abas
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from storage.google_sheets import carregar_dados_processados
from core.indicadores import (
    calcular_resumo_geral,
    calcular_execucao_por_acao,
    calcular_execucao_por_perspectiva,
    calcular_execucao_por_objetivo,
    calcular_execucao_por_categoria,
    calcular_todos_indicadores,
)
from core.get_plano import get_plano

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# Deve ser a primeira chamada Streamlit do script.
# layout="wide" ocupa toda a largura da tela.
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plano de Ação 2026 · IFRS Farroupilha",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# PALETA DE CORES
# Definidas uma vez aqui e reutilizadas em todos os gráficos.
# Baseada no verde institucional do IFRS, com neutros modernos.
# ─────────────────────────────────────────────────────────────────────────────
COR_PRIMARIA   = "#2D8C4E"   # verde IFRS — barras principais, destaques
COR_ESCURA     = "#1B4D2E"   # verde escuro — segundo nível de barra
COR_CLARA      = "#81C784"   # verde claro — terceiro nível / liquidado
COR_PAGO       = "#C8E6C9"   # verde muito claro — pago
COR_VERMELHO   = "#E53935"   # vermelho — meta não atingida
COR_AMARELO    = "#F9A825"   # amarelo — linha de referência / aviso
COR_NEUTRO     = "#E0E0E0"   # cinza claro — fundo de barra orçada
FUNDO_CARD     = "#F8FAF8"   # fundo levemente esverdeado para cards

# Sequência para gráficos de categoria / pizza
PALETA = [
    "#2D8C4E",  # verde IFRS
    "#1565C0",  # azul
    "#EF6C00",  # laranja
    "#8E24AA",  # roxo
    "#D81B60",  # rosa
    "#00897B",  # teal
    "#6D4C41",  # marrom
    "#546E7A",  # azul acinzentado
    "#C62828",  # vermelho
    "#F9A825",  # amarelo ouro
]

ANO = 2026

# ─────────────────────────────────────────────────────────────────────────────
# CSS GLOBAL
# st.markdown com unsafe_allow_html injeta CSS diretamente no <head>.
# Aqui controlamos fonte, espaçamento dos cards, badges e o separador.
# Usamos DM Sans — moderna, legível, institucional sem ser genérica.
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* Aplica a fonte em toda a aplicação */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Remove o padding padrão do Streamlit no topo */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* Cabeçalho da página — título principal */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 0.25rem;
}
.page-title {
    font-size: 1.7rem;
    font-weight: 700;
    color: #1B4D2E;
    letter-spacing: -0.03em;
    margin: 0;
}
.page-subtitle {
    font-size: 0.9rem;
    font-weight: 400;
    color: #6B7280;
    margin: 0 0 1.25rem 0;
}

/* Badge de mês selecionado — aparece ao lado do título */
.badge-mes {
    display: inline-block;
    background: #E8F5E9;
    color: #1B4D2E;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.02em;
    border: 1px solid #C8E6C9;
}

/* Cards de KPI — usados no Resumo Geral */
.kpi-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    height: 100%;
    transition: box-shadow 0.2s;
}
.kpi-card:hover {
    box-shadow: 0 4px 16px rgba(27,77,46,0.10);
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.45rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.02em;
    font-family: 'DM Mono', monospace;
}
.kpi-value.destaque {
    color: #1B4D2E;
}
.kpi-sub {
    font-size: 0.72rem;
    color: #9CA3AF;
    margin-top: 0.2rem;
}

/* Separador horizontal elegante */
.divider {
    height: 1px;
    background: linear-gradient(to right, #E5E7EB, transparent);
    margin: 1.5rem 0;
}

/* Rótulo de seção — substitui os st.markdown("## ...") */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #9CA3AF;
    margin-bottom: 0.6rem;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 1rem 0;
    letter-spacing: -0.01em;
}

/* Card de indicador do plano */
.ind-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.ind-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.ind-card.ok::before  { background: #2D8C4E; }
.ind-card.nok::before { background: #E53935; }
.ind-cod {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 0.2rem;
}
.ind-desc {
    font-size: 0.82rem;
    color: #374151;
    margin-bottom: 0.6rem;
    line-height: 1.3;
}
.ind-valor {
    font-size: 1.6rem;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.02em;
}
.ind-valor.ok  { color: #1B4D2E; }
.ind-valor.nok { color: #E53935; }
.ind-meta {
    font-size: 0.75rem;
    color: #9CA3AF;
    margin-top: 0.15rem;
}

/* Barra de progresso customizada usada nos maiores gastos */
.prog-wrap { margin-bottom: 0.85rem; }
.prog-label {
    font-size: 0.82rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.2rem;
}
.prog-bar-bg {
    background: #F3F4F6;
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
}
.prog-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #2D8C4E 0%, #3FA861 100%);
    transition: width 0.6s ease;
}
.prog-caption {
    font-size: 0.72rem;
    color: #9CA3AF;
    margin-top: 0.15rem;
    font-family: 'DM Mono', monospace;
}

/* Tabela de dados completos — estiliza o dataframe nativo */
.stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def fmt(valor: float) -> str:
    """Formata número como moeda brasileira: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(valor: float) -> str:
    """Formata percentual com 1 casa decimal"""
    return f"{valor:.1f}%"

def layout_grafico(**overrides) -> dict:
    """
    Retorna o dict de layout padrão para todos os gráficos Plotly.
    Aceita **overrides para sobrescrever qualquer chave sem conflito.
    Exemplo: layout_grafico(margin=dict(l=5, r=5, t=5, b=5), height=55)
    """
    base = dict(
        font=dict(family="DM Sans, sans-serif", size=12, color="#374151"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=40, t=20, b=10),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="DM Sans, sans-serif",
        ),
    )
    base.update(overrides)  # overrides sobrescrevem as chaves do base
    return base


# ─────────────────────────────────────────────────────────────────────────────
# ORDEM DOS MESES — usada para ordenar o selectbox cronologicamente
# ─────────────────────────────────────────────────────────────────────────────
ORDEM_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro",
]


# ─────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# spinner mostra feedback enquanto a planilha do Sheets é lida.
# Se vazio, para tudo com st.stop() — não faz sentido renderizar o resto.
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    df_completo = carregar_dados_processados()

if df_completo.empty:
    st.warning("Nenhum dado encontrado. Envie o relatório mensal pela tela de **Upload**.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# CABEÇALHO DA PÁGINA
# HTML direto para ter controle total sobre tipografia e espaçamento.
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# CABEÇALHO DA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
import base64
import os

def get_logo_base64():
    logo_path = "assets/logo_ifrs.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:150px;object-fit:contain">' if logo_b64 else ""

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1B4D2E 0%, #2D8C4E 100%);
    border-radius: 14px;
    padding: 1.2rem 1.8rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(27,77,46,0.18);
">
    {logo_html}
    <div style="width:1px;height:52px;background:rgba(255,255,255,0.25)"></div>
    <div>
        <div style="font-size:1.4rem;font-weight:700;color:white;letter-spacing:-0.02em;line-height:1.2">
            Plano de Ação · IFRS Campus Farroupilha
        </div>
        <div style="font-size:0.85rem;color:rgba(255,255,255,0.75);margin-top:0.2rem;font-weight:400">
            Monitoramento da execução orçamentária — 2026
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FILTROS — linha única com 4 colunas
# Proporcões [2,3,3,3]: mês menor (label curto), demais maiores.
# ─────────────────────────────────────────────────────────────────────────────

# Monta lista de opções ordenada cronologicamente
meses_disp = df_completo[["ano", "mes"]].drop_duplicates().copy()
meses_disp["_ord"] = meses_disp["mes"].apply(
    lambda x: ORDEM_MESES.index(x) if x in ORDEM_MESES else 99
)
meses_disp = meses_disp.sort_values(["ano", "_ord"])
opcoes_mes = [f"{r['mes']}/{r['ano']}" for _, r in meses_disp.iterrows()]

col_mes, col_acao, col_cat, col_obj = st.columns([2, 3, 3, 3])

with col_mes:
    # Padrão: último mês disponível (index=len-1)
    selecao = st.selectbox("Mês", opcoes_mes, index=len(opcoes_mes) - 1, label_visibility="visible")

mes_sel, ano_sel = selecao.split("/")
ano_sel = int(ano_sel)

# DataFrame filtrado por mês — base para todos os cálculos
df_mes = df_completo[
    (df_completo["mes"] == mes_sel) & (df_completo["ano"] == ano_sel)
].copy()

with col_acao:
    acoes = (["Todas"] + sorted(df_mes["acao_desc"].dropna().unique().tolist())
             if "acao_desc" in df_mes.columns else ["Todas"])
    acao_sel = st.selectbox("Ação", acoes)

with col_cat:
    cats = ["Todas"] + sorted(df_mes["categoria"].dropna().unique().tolist())
    cat_sel = st.selectbox("Categoria", cats)

with col_obj:
    objs = ["Todos"] + sorted(df_mes["objetivo"].dropna().unique().tolist())
    obj_sel = st.selectbox("Objetivo", objs)

# df é o DataFrame com todos os filtros aplicados — usado nos blocos de detalhe.
# df_mes (sem filtros de ação/cat/obj) é usado nos KPIs e indicadores do plano,
# para que eles sempre mostrem o total do mês, independente do filtro.
df = df_mes.copy()
if acao_sel != "Todas" and "acao_desc" in df.columns:
    df = df[df["acao_desc"] == acao_sel]
if cat_sel != "Todas":
    df = df[df["categoria"] == cat_sel]
if obj_sel != "Todos":
    df = df[df["objetivo"] == obj_sel]

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ABAS PRINCIPAIS
# Organiza o conteúdo em 4 abas para evitar o scroll infinito.
# tab_resumo  → KPIs + indicadores do plano
# tab_exec    → gráficos de execução (perspectiva, objetivo, categoria)
# tab_evolucao → série histórica mês a mês
# tab_dados   → tabela completa dos registros
# ─────────────────────────────────────────────────────────────────────────────
tab_resumo, tab_exec, tab_evolucao, tab_dados = st.tabs([
    "📊  Visão Geral",
    "📂  Execução",
    "📅  Evolução",
    "🗂️  Dados",
])


# ═════════════════════════════════════════════════════════════════════════════
# ABA 1 — VISÃO GERAL
# ═════════════════════════════════════════════════════════════════════════════
with tab_resumo:

    # ── KPIs ──────────────────────────────────────────────────────────────────
    # calcular_resumo_geral recebe df_mes (sem filtros) para sempre mostrar
    # o total do mês, não a fatia filtrada.
    resumo = calcular_resumo_geral(df_mes, ANO)

    # 5 cards em linha. HTML puro para controle total do layout.
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Orçado</div>
            <div class="kpi-value">{fmt(resumo['total_orcado'])}</div>
            <div class="kpi-sub">Plano de Ação 2026</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Empenhado</div>
            <div class="kpi-value">{fmt(resumo['total_empenhado'])}</div>
            <div class="kpi-sub">{fmt_pct(resumo['perc_execucao'])} do orçado</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Liquidado</div>
            <div class="kpi-value">{fmt(resumo['total_liquidado'])}</div>
            <div class="kpi-sub">&nbsp;</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Pago</div>
            <div class="kpi-value">{fmt(resumo['total_pago'])}</div>
            <div class="kpi-sub">&nbsp;</div>
        </div>""", unsafe_allow_html=True)

    with c5:
        # Card de % execução com cor destacada no valor
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">% Execução Geral</div>
            <div class="kpi-value destaque">{fmt_pct(resumo['perc_execucao'])}</div>
            <div class="kpi-sub">{mes_sel} · {ano_sel}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Barra de progresso visual da execução ────────────────────────────────
    # Mostra visualmente quanto do orçamento anual já foi empenhado.
    # Usa go.Figure com Bar horizontal para ter controle total da aparência.
    perc = min(resumo["perc_execucao"], 100)  # limita em 100% para não vazar

    fig_prog = go.Figure()

    # Barra de fundo (orçado = 100%)
    fig_prog.add_trace(go.Bar(
        x=[100], y=["Execução"],
        orientation="h",
        marker_color=COR_NEUTRO,
        showlegend=False,
        hoverinfo="skip",
    ))
    # Barra de frente (empenhado = perc%)
    fig_prog.add_trace(go.Bar(
        x=[perc], y=["Execução"],
        orientation="h",
        marker_color=COR_PRIMARIA,
        showlegend=False,
        text=f"{perc:.1f}%",
        textposition="inside",
        insidetextanchor="end",
        textfont=dict(color="white", size=13, family="DM Mono"),
    ))

    fig_prog.update_layout(
        **layout_grafico(margin=dict(l=10, r=10, t=5, b=5)),
        barmode="overlay",
        height=55,
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False),
    )
    st.markdown('<p class="section-label">Progresso do orçamento anual</p>', unsafe_allow_html=True)
    st.plotly_chart(fig_prog, use_container_width=True, config={"displayModeBar": False})

 # Valores abaixo da barra
    falta_valor = resumo["total_orcado"] - resumo["total_empenhado"]
    falta_pct   = 100 - resumo["perc_execucao"]

    st.markdown(f"""
            <div style="font-size:0.78rem;color:#6B7280">
                <span style="color:#2D8C4E;font-weight:600">●</span>
                Empenhado: <b style="font-family:'DM Mono',monospace">{fmt(resumo['total_empenhado'])}</b>
                <span style="color:#9CA3AF">({fmt_pct(resumo['perc_execucao'])})</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"""
            <div style="font-size:0.78rem;color:#6B7280;text-align:left">
                <span style="color:#E0E0E0;font-weight:600">●</span>
                Faltante: <b style="font-family:'DM Mono',monospace">{fmt(max(falta_valor, 0))}</b>
                <span style="color:#9CA3AF">({fmt_pct(max(falta_pct, 0))})</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

  # ── Indicadores do Plano ─────────────────────────────────────────────────
    st.markdown('<p class="section-title">Indicadores do Plano</p>', unsafe_allow_html=True)

    # Monta df acumulado do ano até o mês selecionado
    meses_ate_sel = [
        m for m in ORDEM_MESES
        if ORDEM_MESES.index(m) <= ORDEM_MESES.index(mes_sel)
    ]
    df_acumulado = df_completo[
        (df_completo["ano"] == ano_sel) &
        (df_completo["mes"].isin(meses_ate_sel))
    ].copy()

    n_meses = len(df_acumulado["mes"].unique())

    indicadores = calcular_todos_indicadores(df_mes, df_acumulado, ANO)
    cols_ind = st.columns(len(indicadores))

    for col, ind in zip(cols_ind, indicadores):
        status = "ok" if ind["atingido"] else "nok"
        icone  = "✓" if ind["atingido"] else "↑"

        # Barra de progresso dentro do card
        pct_barra = min(ind["realizado"] / ind["meta"] * 100, 100) if ind["meta"] > 0 else 0

        with col:
            st.markdown(f"""
            <div class="ind-card {status}">
                <div class="ind-cod">{ind['indicador']}</div>
                <div class="ind-desc">{ind['descricao']}</div>
                <div class="ind-valor {status}">{ind['realizado']:.2f}%</div>
                <div class="ind-meta">Meta anual: {ind['meta']:.2f}%</div>
                <div style="margin: 0.5rem 0 0.2rem 0">
                    <div style="background:#F3F4F6;border-radius:4px;height:5px;overflow:hidden">
                        <div style="width:{pct_barra:.1f}%;height:100%;border-radius:4px;background:{'#2D8C4E' if ind['atingido'] else '#E53935'}"></div>
                    </div>
                </div>
                <div class="ind-meta" style="display:flex;justify-content:space-between">
                    <span>{icone} {'Atingido' if ind['atingido'] else f"Falta {ind['falta']:.2f}%"}</span>
                    <span style="color:#9CA3AF">{n_meses} {'mês' if n_meses == 1 else 'meses'} acum.</span>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Distribuição por Categoria ────────────────────────────────────────────
    # Donut + lista lateral. Aqui usa df (filtrado) pois é detalhe.
    st.markdown('<p class="section-title">Distribuição por Categoria</p>', unsafe_allow_html=True)

    df_cat = calcular_execucao_por_categoria(df)

    if df_cat.empty:
        st.info("Nenhuma categoria identificada nos dados filtrados.")
    else:
        col_pizza, col_detalhe = st.columns([3, 2])

        with col_pizza:
            cores_usadas = PALETA[:len(df_cat)]
            fig_pizza = go.Figure(go.Pie(
                labels=df_cat["categoria"],
                values=df_cat["total_empenhado"],
                hole=0.52,   
                sort=False,

                marker=dict(colors=PALETA[:len(df_cat)], line=dict(color="white", width=2)),

                textinfo="none",
                textposition="outside",

                pull=[
                    0.02 if v < 5 else 0
                    for v in (
                        df_cat["total_empenhado"] /
                        df_cat["total_empenhado"].sum() * 100
                    )
                ],

                textfont=dict(size=11, family="DM Mono"),
                hovertemplate="<b>%{label}</b><br>%{value:,.2f}<br>%{percent}<extra></extra>",
            ))
            # Texto central do donut — total empenhado
            fig_pizza.update_layout(
                **layout_grafico(margin=dict(l=0, r=0, t=10, b=10)),
                height=320,
                showlegend=False,
                annotations=[dict(
                    text=f"<b>{fmt_pct(resumo['perc_execucao'])}</b><br><span style='font-size:10px'>execução</span>",
                    x=0.5, y=0.5,
                    font=dict(size=14, family="DM Sans"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig_pizza, use_container_width=True, config={"displayModeBar": False})

        with col_detalhe:
            # Lista com barras de progresso customizadas em HTML
            total_emp = df_cat["total_empenhado"].sum()
            st.markdown("<br>", unsafe_allow_html=True)

            for i, (_, row) in enumerate(df_cat.iterrows()):
                pct = row["total_empenhado"] / total_emp * 100 if total_emp > 0 else 0

                # largura da barra limitada em 100% para não vazar no CSS
                st.markdown(f"""
                <div class="prog-wrap">
                    <div class="prog-label">{row['categoria']}</div>
                    <div class="prog-bar-bg">
                        <div class="prog-bar-fill" style=" width:{min(pct,100):.1f}%; background:{PALETA[i % len(PALETA)]};"></div>
                    </div>
                    <div class="prog-caption">{fmt(row['total_empenhado'])} · {pct:.1f}%</div>
                </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ABA 2 — EXECUÇÃO
# ═════════════════════════════════════════════════════════════════════════════
with tab_exec:

    # ── Execução por Perspectiva ──────────────────────────────────────────────
    st.markdown('<p class="section-title">Por Perspectiva Estratégica</p>', unsafe_allow_html=True)

    df_persp = calcular_execucao_por_perspectiva(df, ANO)

    if df_persp.empty:
        st.info("Nenhuma perspectiva identificada.")
    else:
        # Ordena do maior para o menor para leitura natural
        df_persp = df_persp.sort_values("total_empenhado", ascending=True)

        fig_persp = go.Figure(go.Bar(
            x=df_persp["total_empenhado"],
            y=df_persp["perspectiva"],
            orientation="h",
            marker_color=COR_PRIMARIA,
            text=[fmt(v) for v in df_persp["total_empenhado"]],
            textposition="outside",
            textfont=dict(size=11, family="DM Mono"),
            hovertemplate="<b>%{y}</b><br>%{x:,.2f}<extra></extra>",
        ))
        fig_persp.update_layout(
            **layout_grafico(margin=dict(l=10, r=120, t=10, b=10)),
            height=max(200, len(df_persp) * 52),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=12)),
        )
        st.plotly_chart(fig_persp, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Execução por Objetivo ─────────────────────────────────────────────────
    # Gráfico de barras agrupadas: orçado / empenhado / liquidado / pago.
    # Filtra apenas objetivos com valor orçado > 0 para não poluir.
    st.markdown('<p class="section-title">Por Objetivo Estratégico</p>', unsafe_allow_html=True)

    df_obj = calcular_execucao_por_objetivo(df, ANO)
    df_obj_f = df_obj[df_obj["valor_orcado"] > 0].copy()

    if df_obj_f.empty:
        st.info("Nenhum objetivo com valor orçado nos dados filtrados.")
    else:
        fig_obj = go.Figure()

        # Cada trace é uma série; barmode="group" coloca lado a lado
        for serie, cor, nome in [
            ("valor_orcado",    COR_NEUTRO,   "Orçado"),
            ("total_empenhado", COR_PRIMARIA, "Empenhado"),
            ("total_liquidado", COR_CLARA,    "Liquidado"),
            ("total_pago",      COR_PAGO,     "Pago"),
        ]:
            fig_obj.add_trace(go.Bar(
                name=nome,
                x=df_obj_f["objetivo"],
                y=df_obj_f[serie],
                marker_color=cor,
                marker_line_width=0,
                hovertemplate=f"<b>%{{x}}</b> · {nome}<br>R$ %{{y:,.2f}}<extra></extra>",
            ))

        fig_obj.update_layout(
            **layout_grafico(),
            barmode="group",
            height=380,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right",  x=1,
                font=dict(size=11),
            ),
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F3F4F6",
                tickprefix="R$ ",
                tickformat=",.0f",
                tickfont=dict(size=10, family="DM Mono"),
            ),
        )
        st.plotly_chart(fig_obj, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Execução por Ação ─────────────────────────────────────────────────────
    # Aqui o problema anterior era a escala: uma ação domina.
    # Solução: mostrar % do total em vez de valor absoluto, e limitar ao top 10.
    st.markdown('<p class="section-title">Por Ação (Top 10)</p>', unsafe_allow_html=True)

    if "acao_desc" not in df.columns:
        st.info("Dados sem informação de ação.")
    else:
        df_acao = calcular_execucao_por_acao(df)

        if df_acao.empty:
            st.info("Nenhuma ação identificada.")
        else:
            total_acoes = df_acao["total_empenhado"].sum()
            df_acao["pct"] = df_acao["total_empenhado"] / total_acoes * 100

            # Top 10 ordenado crescente para o gráfico horizontal ficar com maior em cima
            top10 = df_acao.nlargest(10, "total_empenhado").sort_values("pct", ascending=True)

            fig_acao = go.Figure(go.Bar(
                x=top10["pct"],
                y=top10["acao_desc"],
                orientation="h",
                marker=dict(
                    # Gradiente de cor: barras maiores ficam mais escuras
                    color=top10["pct"],
                    colorscale=[[0, COR_CLARA], [1, COR_ESCURA]],
                    showscale=False,
                ),
                text=[f"{v:.1f}%" for v in top10["pct"]],
                textposition="outside",
                textfont=dict(size=11, family="DM Mono"),
                customdata=top10["total_empenhado"],
                hovertemplate="<b>%{y}</b><br>%{customdata:,.2f} (%{x:.1f}%)<extra></extra>",
            ))
            fig_acao.update_layout(
                **layout_grafico(margin=dict(l=10, r=80, t=10, b=10)),
                height=max(300, len(top10) * 42),
                xaxis=dict(
                    showticklabels=False, showgrid=False, zeroline=False,
                    range=[0, top10["pct"].max() * 1.25],
                ),
                yaxis=dict(tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_acao, use_container_width=True, config={"displayModeBar": False})


# ═════════════════════════════════════════════════════════════════════════════
# ABA 3 — EVOLUÇÃO HISTÓRICA
# ═════════════════════════════════════════════════════════════════════════════
with tab_evolucao:

    st.markdown('<p class="section-title">Evolução da Execução Orçamentária</p>', unsafe_allow_html=True)

    # Usa df_completo sem filtros de mês para ver toda a série histórica
    df_hist = df_completo.copy()

    if df_hist.empty or "mes" not in df_hist.columns:
        st.info("Nenhum histórico disponível ainda.")
    else:
        # Agrega por mês/ano
        df_evo = df_hist.groupby(["ano", "mes"]).agg(
            total_empenhado=("valor_empenhado", "sum"),
        ).reset_index()
        df_evo["_ord"] = df_evo["mes"].apply(
            lambda x: ORDEM_MESES.index(x) if x in ORDEM_MESES else 99
        )
        df_evo = df_evo.sort_values(["ano", "_ord"])
        df_evo["mes_ano"] = df_evo["mes"] + "/" + df_evo["ano"].astype(str)

        # Calcula total orçado para o percentual
        plano = get_plano(ANO)
        total_orcado_ano = sum(
            obj["valor_orcado"]
            for persp in plano["perspectivas"].values()
            for obj in persp["objetivos"].values()
        )

        df_evo["empenhado_acum"] = df_evo["total_empenhado"].cumsum()
        df_evo["perc_acum"]     = (df_evo["empenhado_acum"] / total_orcado_ano * 100).round(1)
        df_evo["perc_mensal"]   = (df_evo["total_empenhado"] / total_orcado_ano * 100).round(1)

        col_linha, col_barra = st.columns(2)

        # ── Gráfico de linha: % acumulado ──────────────────────────────────
        with col_linha:
            st.markdown('<p class="section-label">% Acumulado do orçamento anual</p>', unsafe_allow_html=True)

            n = len(df_evo)
            # Linha de meta proporcional: divide 100% pelos 12 meses
            meta_prop = round(100 / 12 * n, 1)

            fig_linha = go.Figure()

            # Área preenchida abaixo da linha de execução
            fig_linha.add_trace(go.Scatter(
                x=df_evo["mes_ano"],
                y=df_evo["perc_acum"],
                mode="lines+markers+text",
                name="Acumulado",
                line=dict(color=COR_PRIMARIA, width=2.5),
                marker=dict(size=8, color=COR_PRIMARIA, symbol="circle"),
                fill="tozeroy",
                fillcolor="rgba(45,140,78,0.08)",
                text=[f"{v}%" for v in df_evo["perc_acum"]],
                textposition="top center",
                textfont=dict(size=10, family="DM Mono"),
                hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>",
            ))

            # Linha tracejada de meta proporcional
            fig_linha.add_hline(
                y=meta_prop,
                line_dash="dot",
                line_color=COR_AMARELO,
                line_width=1.5,
                annotation_text=f"Meta proporcional: {meta_prop}%",
                annotation_position="bottom right",
                annotation_font=dict(size=10, color=COR_AMARELO),
            )

            fig_linha.update_layout(
                **layout_grafico(),
                height=300,
                showlegend=False,
                xaxis=dict(tickfont=dict(size=10), tickangle=-30),
                yaxis=dict(
                    ticksuffix="%",
                    showgrid=True,
                    gridcolor="#F3F4F6",
                    range=[0, max(df_evo["perc_acum"].max() * 1.2, meta_prop * 1.2)],
                    tickfont=dict(size=10, family="DM Mono"),
                ),
            )
            st.plotly_chart(fig_linha, use_container_width=True, config={"displayModeBar": False})

        # ── Gráfico de barras: % por mês ───────────────────────────────────
        with col_barra:
            st.markdown('<p class="section-label">% empenhado por mês</p>', unsafe_allow_html=True)

            fig_barra = go.Figure(go.Bar(
                x=df_evo["mes_ano"],
                y=df_evo["perc_mensal"],
                marker_color=COR_PRIMARIA,
                marker_line_width=0,
                text=[f"{v}%" for v in df_evo["perc_mensal"]],
                textposition="outside",
                textfont=dict(size=10, family="DM Mono"),
                hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>",
            ))
            fig_barra.update_layout(
                **layout_grafico(),
                height=300,
                xaxis=dict(tickfont=dict(size=10), tickangle=-30),
                yaxis=dict(
                    ticksuffix="%",
                    showgrid=True,
                    gridcolor="#F3F4F6",
                    tickfont=dict(size=10, family="DM Mono"),
                ),
            )
            st.plotly_chart(fig_barra, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # ── Tabela resumo da evolução ──────────────────────────────────────
        st.markdown('<p class="section-label">Resumo mensal</p>', unsafe_allow_html=True)

        df_tab = df_evo[["mes_ano", "total_empenhado", "perc_mensal", "perc_acum"]].copy()
        df_tab.columns = ["Mês/Ano", "Total Empenhado", "% Mensal", "% Acumulado"]
        df_tab["Total Empenhado"] = df_tab["Total Empenhado"].apply(fmt)
        df_tab["% Mensal"]        = df_tab["% Mensal"].apply(lambda x: f"{x:.1f}%")
        df_tab["% Acumulado"]     = df_tab["% Acumulado"].apply(lambda x: f"{x:.1f}%")

        st.dataframe(df_tab, use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# ABA 4 — DADOS COMPLETOS
# ═════════════════════════════════════════════════════════════════════════════
with tab_dados:

    st.markdown('<p class="section-title">Registros Classificados</p>', unsafe_allow_html=True)

    # Estatísticas rápidas acima da tabela
    total_lin  = len(df)
    nao_mapeadas = len(df[df["objetivo"] == "Não mapeado"]) if "objetivo" in df.columns else 0
    pct_mapeadas = (1 - nao_mapeadas / total_lin) * 100 if total_lin > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de linhas", f"{total_lin:,}".replace(",", "."))
    m2.metric("Não mapeadas", f"{nao_mapeadas:,}".replace(",", "."))
    m3.metric("% Mapeado", f"{pct_mapeadas:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)