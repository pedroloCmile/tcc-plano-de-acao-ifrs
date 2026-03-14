# =============================================================================
# TELA DE CONFIGURAÇÃO — Plano de Ação 2026
# Exibe as perspectivas, objetivos, metas e valores orçados do plano.
# =============================================================================

import streamlit as st
import pandas as pd
from core.get_plano import get_perspectivas

st.title("⚙️ Configuração do Plano de Ação")
st.subheader("IFRS Campus Farroupilha · 2026")
st.markdown("---")

st.info("As informações abaixo refletem o Plano de Ação 2026 fixado no sistema. Para anos futuros, consulte o administrador do sistema.")

# ── Dados do plano ────────────────────────────────────────────────────────────

ANO = 2026
perspectivas = get_perspectivas(ANO)

# ── Exibição por perspectiva ──────────────────────────────────────────────────

for nome_perspectiva, dados_perspectiva in perspectivas.items():

    st.markdown(f"## {nome_perspectiva}")

    objetivos = dados_perspectiva["objetivos"]
    linhas    = []

    for cod_obj, dados_obj in objetivos.items():

        # Indicadores do objetivo
        for cod_ind, dados_ind in dados_obj["indicadores"].items():
            linhas.append({
                "Objetivo":        cod_obj,
                "Descrição":       dados_obj["descricao"],
                "Indicador":       cod_ind,
                "Meta":            dados_ind["descricao"],
                "Valor da Meta":   dados_ind["meta"],
                "Valor Orçado (R$)": dados_obj["valor_orcado"],
            })

    df = pd.DataFrame(linhas)

    # Formata valor orçado
    df["Valor Orçado (R$)"] = df["Valor Orçado (R$)"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if x > 0 else "—"
    )

    # Formata valor da meta
    df["Valor da Meta"] = df["Valor da Meta"].apply(
        lambda x: f"{x * 100:.1f}%" if isinstance(x, float) and x < 10 else str(x)
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")