# =============================================================================
# TELA DE DASHBOARD — Indicadores do Plano de Ação 2026
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
    calcular_execucao_por_categoria_pi,
    calcular_todos_indicadores,
)

st.title("📊 Dashboard do Plano de Ação")
st.subheader("IFRS Campus Farroupilha · 2026")
st.markdown("---")

ANO = 2026

# ── Carrega dados ─────────────────────────────────────────────────────────────

with st.spinner("Carregando dados..."):
    df = carregar_dados_processados()

if df.empty:
    st.warning("Nenhum dado encontrado. Envie o relatório mensal pela tela de **Upload**.")
    st.stop()

# ── Filtros ───────────────────────────────────────────────────────────────────

ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

meses_disponiveis = df[["ano", "mes"]].drop_duplicates().copy()
meses_disponiveis["mes_ordem"] = meses_disponiveis["mes"].apply(
    lambda x: ordem_meses.index(x) if x in ordem_meses else 99
)
meses_disponiveis = meses_disponiveis.sort_values(["ano", "mes_ordem"])
opcoes = [f"{row['mes']}/{row['ano']}" for _, row in meses_disponiveis.iterrows()]

col1, col2, col3, col4 = st.columns([2, 2, 3, 3])

with col1:
    selecao = st.selectbox("Mês de referência", opcoes, index=len(opcoes) - 1)

mes_sel, ano_sel = selecao.split("/")
ano_sel = int(ano_sel)
df = df[(df["mes"] == mes_sel) & (df["ano"] == ano_sel)]

with col2:
    acoes_disponiveis = ["Todas"] + sorted(df["acao_desc"].dropna().unique().tolist()) if "acao_desc" in df.columns else ["Todas"]
    acao_sel = st.selectbox("Ação", acoes_disponiveis)

with col3:
    categorias_disponiveis = ["Todas"] + sorted(df["categoria"].dropna().unique().tolist())
    categoria_sel = st.selectbox("Categoria", categorias_disponiveis)

with col4:
    objetivos_disponiveis = ["Todos"] + sorted(df["objetivo"].dropna().unique().tolist())
    objetivo_sel = st.selectbox("Objetivo", objetivos_disponiveis)

# Aplica filtros
if acao_sel != "Todas" and "acao_desc" in df.columns:
    df = df[df["acao_desc"] == acao_sel]
if categoria_sel != "Todas":
    df = df[df["categoria"] == categoria_sel]
if objetivo_sel != "Todos":
    df = df[df["objetivo"] == objetivo_sel]

# ── Bloco 1 — Resumo Geral ────────────────────────────────────────────────────

st.markdown("## Resumo Geral")

resumo = calcular_resumo_geral(df, ANO)

def fmt(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Orçado",     fmt(resumo["total_orcado"]))
col2.metric("Total Empenhado",  fmt(resumo["total_empenhado"]))
col3.metric("Total Liquidado",  fmt(resumo["total_liquidado"]))
col4.metric("Total Pago",       fmt(resumo["total_pago"]))
col5.metric("% Execução Geral", f"{resumo['perc_execucao']:.1f}%")

st.markdown("---")

# ── Bloco 2 — Execução por Ação ───────────────────────────────────────────────

st.markdown("## Execução por Ação")

if "acao_desc" not in df.columns:
    st.info("Dados sem informação de ação. Reenvie o relatório para atualizar.")
else:
    df_acao = calcular_execucao_por_acao(df)

    if df_acao.empty:
        st.info("Nenhuma ação identificada nos dados.")
    else:
        fig_acao = px.bar(
            df_acao,
            x="total_empenhado",
            y="acao_desc",
            orientation="h",
            text="total_empenhado",
            labels={
                "total_empenhado": "Total Empenhado (R$)",
                "acao_desc":       "Ação",
            },
            color="acao_desc",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_acao.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
        fig_acao.update_layout(showlegend=False, xaxis_title="Total Empenhado (R$)", yaxis_title="", height=350)
        st.plotly_chart(fig_acao, use_container_width=True)

st.markdown("---")

# ── Bloco 3 — Execução por Perspectiva ───────────────────────────────────────

st.markdown("## Execução por Perspectiva")

df_persp = calcular_execucao_por_perspectiva(df, ANO)

if df_persp.empty:
    st.info("Nenhuma perspectiva identificada nos dados filtrados.")
else:
    fig_persp = px.bar(
        df_persp,
        x="total_empenhado",
        y="perspectiva",
        orientation="h",
        text="total_empenhado",
        labels={
            "total_empenhado": "Total Empenhado (R$)",
            "perspectiva":     "Perspectiva",
        },
        color="perspectiva",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_persp.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
    fig_persp.update_layout(showlegend=False, xaxis_title="Total Empenhado (R$)", yaxis_title="", height=350)
    st.plotly_chart(fig_persp, use_container_width=True)

st.markdown("---")

# ── Bloco 4 — Indicadores do Plano ───────────────────────────────────────────

st.markdown("## Indicadores do Plano")

indicadores = calcular_todos_indicadores(df, ANO)
cols = st.columns(len(indicadores))

for col, ind in zip(cols, indicadores):
    icone = "✅" if ind["atingido"] else "❌"
    col.metric(
        label=f"{icone} {ind['indicador']} — {ind['descricao']}",
        value=f"{ind['realizado']:.2f}%",
        delta=f"Meta: {ind['meta']:.2f}%",
        delta_color="normal" if ind["atingido"] else "inverse",
    )

st.markdown("---")

# ── Bloco 5 — Execução por Objetivo ──────────────────────────────────────────

st.markdown("## Execução por Objetivo Estratégico")

df_obj = calcular_execucao_por_objetivo(df, ANO)
df_obj_filtrado = df_obj[df_obj["valor_orcado"] > 0].copy()

if df_obj_filtrado.empty:
    st.info("Nenhum objetivo com valor orçado nos dados filtrados.")
else:
    fig_obj = go.Figure()
    fig_obj.add_trace(go.Bar(name="Orçado",    x=df_obj_filtrado["objetivo"], y=df_obj_filtrado["valor_orcado"],    marker_color="#a8d8ea"))
    fig_obj.add_trace(go.Bar(name="Empenhado", x=df_obj_filtrado["objetivo"], y=df_obj_filtrado["total_empenhado"], marker_color="#2e75b6"))
    fig_obj.add_trace(go.Bar(name="Liquidado", x=df_obj_filtrado["objetivo"], y=df_obj_filtrado["total_liquidado"], marker_color="#1a4a7a"))
    fig_obj.add_trace(go.Bar(name="Pago",      x=df_obj_filtrado["objetivo"], y=df_obj_filtrado["total_pago"],      marker_color="#0d2137"))
    fig_obj.update_layout(barmode="group", xaxis_title="Objetivo", yaxis_title="Valor (R$)", legend_title="Legenda", height=400)
    st.plotly_chart(fig_obj, use_container_width=True)

st.markdown("---")

# ── Bloco 6 — Distribuição por Categoria ─────────────────────────────────────

st.markdown("## Distribuição por Categoria")

df_cat = calcular_execucao_por_categoria(df)

if df_cat.empty:
    st.info("Nenhuma categoria identificada nos dados filtrados.")
else:
    fig_cat = px.pie(
        df_cat,
        names="categoria",
        values="total_empenhado",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4,
    )
    fig_cat.update_traces(textposition="inside", textinfo="percent+label")
    fig_cat.update_layout(height=500, showlegend=True)
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# ── Bloco 7 — Dados Completos ─────────────────────────────────────────────────

st.markdown("## Dados Completos")

with st.expander("Ver todos os registros classificados"):
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Bloco 8 — Comparativo Mensal ──────────────────────────────────────────────

st.markdown("---")
st.markdown("## Comparativo Mensal")

df_historico = carregar_dados_processados()

if df_historico.empty or "mes" not in df_historico.columns:
    st.info("Nenhum histórico disponível ainda.")
else:
    df_comp = df_historico.groupby(["ano", "mes"]).agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
        total_pago     =("valor_pago",      "sum"),
    ).reset_index()

    df_comp["mes_ordem"] = df_comp["mes"].apply(
        lambda x: ordem_meses.index(x) if x in ordem_meses else 99
    )
    df_comp = df_comp.sort_values(["ano", "mes_ordem"])
    df_comp["mes_ano"] = df_comp["mes"] + "/" + df_comp["ano"].astype(str)

    st.markdown("### Evolução do Total Empenhado")
    fig_linha = px.line(
        df_comp, x="mes_ano", y="total_empenhado", markers=True,
        labels={"mes_ano": "Mês/Ano", "total_empenhado": "Total Empenhado (R$)"},
        color_discrete_sequence=["#2e75b6"],
    )
    fig_linha.update_layout(height=350, xaxis_title="Mês", yaxis_title="Total Empenhado (R$)")
    st.plotly_chart(fig_linha, use_container_width=True)

    st.markdown("### Empenhado vs Liquidado vs Pago por Mês")
    fig_barras = go.Figure()
    fig_barras.add_trace(go.Bar(name="Empenhado", x=df_comp["mes_ano"], y=df_comp["total_empenhado"], marker_color="#2e75b6"))
    fig_barras.add_trace(go.Bar(name="Liquidado", x=df_comp["mes_ano"], y=df_comp["total_liquidado"], marker_color="#1a4a7a"))
    fig_barras.add_trace(go.Bar(name="Pago",      x=df_comp["mes_ano"], y=df_comp["total_pago"],      marker_color="#0d2137"))
    fig_barras.update_layout(barmode="group", height=350, xaxis_title="Mês", yaxis_title="Valor (R$)", legend_title="Legenda")
    st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown("### Resumo por Mês")
    df_tabela = df_comp[["mes_ano", "total_empenhado", "total_liquidado", "total_pago"]].copy()
    df_tabela["total_empenhado"] = df_tabela["total_empenhado"].apply(fmt)
    df_tabela["total_liquidado"] = df_tabela["total_liquidado"].apply(fmt)
    df_tabela["total_pago"]      = df_tabela["total_pago"].apply(fmt)
    df_tabela.columns = ["Mês/Ano", "Total Empenhado", "Total Liquidado", "Total Pago"]
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)