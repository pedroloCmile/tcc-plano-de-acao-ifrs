# =============================================================================
# TELA DE UPLOAD — Relatório Mensal de Execução Orçamentária
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from core.processamento import processar_relatorio, ler_relatorio, detectar_mes_relatorio
from storage.google_sheets import (
    salvar_dados_processados,
    salvar_log_upload,
    salvar_erros,
    carregar_log_uploads,
    excluir_dados_mes, 
    excluir_log_upload
)

st.title("📤 Upload do Relatório Mensal")
st.subheader("IFRS Campus Farroupilha · 2026")
st.markdown("---")

st.markdown("### Enviar novo relatório")

lista_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

arquivo = st.file_uploader(
    "Selecione o arquivo do relatório mensal (.xlsx ou .xls)",
    type=["xlsx", "xls"],
)

if arquivo:
    st.success(f"Arquivo **{arquivo.name}** carregado com sucesso.")

    # Detecta mês automaticamente
    df_bruto     = ler_relatorio(arquivo)
    mes_detectado = detectar_mes_relatorio(df_bruto)

    col1, col2 = st.columns(2)

    with col1:
        idx_mes = lista_meses.index(mes_detectado) if mes_detectado else 0
        mes     = st.selectbox("Mês de referência", lista_meses, index=idx_mes)

        if mes_detectado:
            if mes_detectado == mes:
                st.success(f"✅ Mês detectado automaticamente: **{mes_detectado}**")
            else:
                st.warning(f"⚠️ O arquivo parece ser de **{mes_detectado}** mas você selecionou **{mes}**. Confirme antes de processar.")

    with col2:
        ano_atual       = datetime.now().year
        anos_disponiveis = list(range(2026, ano_atual + 2))
        ano             = st.selectbox(
            "Ano de referência",
            anos_disponiveis,
            index=anos_disponiveis.index(ano_atual) if ano_atual in anos_disponiveis else 0
        )

    if st.button("Processar e salvar", type="primary"):
        with st.spinner("Processando o relatório..."):
            try:
                df_completo, df_nao_mapeado, alertas = processar_relatorio(arquivo, mes, ano)

                salvar_dados_processados(df_completo, mes, ano)
                salvar_log_upload(
                    nome_arquivo=arquivo.name,
                    mes=mes,
                    ano=ano,
                    total_linhas=len(df_completo),
                    nao_mapeadas=len(df_nao_mapeado),
                )
                salvar_erros(df_nao_mapeado)

                st.success("Relatório processado e salvo com sucesso!")

                st.markdown("---")
                st.markdown("### Resumo do processamento")

                col1, col2, col3 = st.columns(3)
                col1.metric("Total de linhas",     len(df_completo))
                col2.metric("Linhas classificadas", len(df_completo) - len(df_nao_mapeado))
                col3.metric("Não mapeadas",         len(df_nao_mapeado))

                if not df_nao_mapeado.empty:
                    st.warning(f"{len(df_nao_mapeado)} despesa(s) não encontrada(s) no mapeamento do plano de ação.")
                    with st.expander("Ver despesas não mapeadas"):
                        st.dataframe(df_nao_mapeado, use_container_width=True, hide_index=True)
                else:
                    st.info("Todas as despesas foram classificadas com sucesso.")

                if alertas:
                    st.markdown("---")
                    st.markdown("### ⚠️ Inconsistências detectadas")
                    for alerta in alertas:
                        st.warning(alerta)
                else:
                    st.success("Nenhuma inconsistência detectada nos valores financeiros.")

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
        # Cabeçalho
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])
        col1.markdown("**Arquivo**")
        col2.markdown("**Mês**")
        col3.markdown("**Ano**")
        col4.markdown("**Total linhas**")
        col5.markdown("**Não mapeadas**")
        col6.markdown("**Excluir**")

        for _, row in df_log.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])
            col1.write(row["nome_arquivo"])
            col2.write(row["mes"])
            col3.write(row["ano"])
            col4.write(f"{row['total_linhas']} linhas")
            col5.write(f"{row['nao_mapeadas']} não mapeadas")

            if col6.button("🗑️", key=f"del_{row['mes']}_{row['ano']}"):
                with st.spinner(f"Excluindo {row['mes']}/{row['ano']}..."):
                    try:
                        excluir_dados_mes(str(row["mes"]), str(row["ano"]))
                        excluir_log_upload(str(row["mes"]), str(row["ano"]))
                        st.success(f"Relatório de {row['mes']}/{row['ano']} excluído com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")

except Exception as e:
    st.warning(f"Não foi possível carregar o histórico: {e}")