# =============================================================================
# TELA DE UPLOAD — Relatório Mensal de Execução Orçamentária
# =============================================================================

import streamlit as st
import pandas as pd
from core.processamento import processar_relatorio
from storage.google_sheets import (
    salvar_dados_processados,
    salvar_log_upload,
    salvar_erros,
    carregar_log_uploads,
)

st.title("📤 Upload do Relatório Mensal")
st.subheader("IFRS Campus Farroupilha · 2026")
st.markdown("---")

# ── Formulário de upload ──────────────────────────────────────────────────────

st.markdown("### Enviar novo relatório")

col1, col2 = st.columns(2)
with col1:
    mes = st.selectbox("Mês de referência", [
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ])
with col2:
    ano = st.selectbox("Ano de referência", [2026])

arquivo = st.file_uploader(
    "Selecione o arquivo xlsx do relatório mensal",
    type=["xlsx"],
)

if arquivo:
    st.success(f"Arquivo **{arquivo.name}** carregado com sucesso.")

    if st.button("Processar e salvar", type="primary"):
        with st.spinner("Processando o relatório..."):
            try:
                df_completo, df_nao_mapeado = processar_relatorio(arquivo)

                salvar_dados_processados(df_completo)
                salvar_log_upload(
                    nome_arquivo=arquivo.name,
                    mes=mes,
                    ano=ano,
                    total_linhas=len(df_completo),
                    nao_mapeadas=len(df_nao_mapeado),
                )
                salvar_erros(df_nao_mapeado)

                st.success("Relatório processado e salvo com sucesso!")

                # ── Resumo do processamento ───────────────────────────────────
                st.markdown("---")
                st.markdown("### Resumo do processamento")

                col1, col2, col3 = st.columns(3)
                col1.metric("Total de linhas", len(df_completo))
                col2.metric("Linhas classificadas", len(df_completo) - len(df_nao_mapeado))
                col3.metric("Não mapeadas", len(df_nao_mapeado))

                # ── Linhas não mapeadas ───────────────────────────────────────
                if not df_nao_mapeado.empty:
                    st.warning(f"{len(df_nao_mapeado)} despesa(s) não encontrada(s) no mapeamento do plano de ação.")
                    with st.expander("Ver despesas não mapeadas"):
                        st.dataframe(df_nao_mapeado, use_container_width=True, hide_index=True)
                else:
                    st.info("Todas as despesas foram classificadas com sucesso.")

                # ── Preview dos dados ─────────────────────────────────────────
                st.markdown("---")
                st.markdown("### Preview dos dados processados")
                st.dataframe(df_completo, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"Erro ao processar o relatório: {e}")

# ── Histórico de uploads ──────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### Histórico de uploads")

try:
    df_log = carregar_log_uploads()
    if df_log.empty:
        st.info("Nenhum relatório enviado ainda.")
    else:
        st.dataframe(df_log, use_container_width=True, hide_index=True)
except Exception as e:
    st.warning(f"Não foi possível carregar o histórico: {e}")