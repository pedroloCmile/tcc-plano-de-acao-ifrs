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

ANO = 2026
perspectivas = get_perspectivas(ANO)

def fmt_valor(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if x > 0 else "—"

def fmt_meta(x):
    if isinstance(x, float) and x < 10:
        return f"{x * 100:.1f}%"
    return str(x)

for nome_perspectiva, dados_perspectiva in perspectivas.items():

    st.markdown(f"## {nome_perspectiva}")

    objetivos = dados_perspectiva["objetivos"]
    linhas    = []

    for cod_obj, dados_obj in objetivos.items():

        indicadores = dados_obj["indicadores"]

        if indicadores:
            # Objetivo com indicadores — uma linha por indicador
            for cod_ind, dados_ind in indicadores.items():
                linhas.append({
                    "Objetivo":         cod_obj,
                    "Descrição":        dados_obj["descricao"],
                    "Indicador":        cod_ind,
                    "Meta":             dados_ind["descricao"],
                    "Valor da Meta":    fmt_meta(dados_ind["meta"]),
                    "Valor Orçado (R$)": fmt_valor(dados_obj["valor_orcado"]),
                })
        else:
            # Objetivo sem indicadores — uma linha só com o objetivo
            linhas.append({
                "Objetivo":         cod_obj,
                "Descrição":        dados_obj["descricao"],
                "Indicador":        "—",
                "Meta":             "—",
                "Valor da Meta":    "—",
                "Valor Orçado (R$)": fmt_valor(dados_obj["valor_orcado"]),
            })

    if linhas:
        df = pd.DataFrame(linhas)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")