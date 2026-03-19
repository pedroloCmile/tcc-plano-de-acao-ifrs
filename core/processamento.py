# =============================================================================
# PROCESSAMENTO DO RELATÓRIO MENSAL
# Responsável por ler, limpar e classificar o xlsx do SIAFI.
# Retorna um DataFrame tratado e classificado conforme o mapeamento.
# =============================================================================

import pandas as pd
from core.mapeamento import get_mapeamento_por_nd


# Colunas esperadas no relatório após renomeação
COLUNAS = {
    "col_nd_descricao": "nd_descricao",
    "col_nd_codigo":    "nd_codigo",
    "col_subitem":      "subitem",
    "col_subitem_desc": "subitem_descricao",
    "col_empenhado":    "valor_empenhado",
    "col_liquidado":    "valor_liquidado",
}


def ler_relatorio(arquivo) -> pd.DataFrame:
    """
    Lê o xlsx do SIAFI e retorna um DataFrame bruto.
    O parâmetro 'arquivo' pode ser um caminho ou um objeto de arquivo
    (como o retornado pelo st.file_uploader do Streamlit).
    """
    df = pd.read_excel(arquivo, header=None)
    return df


def identificar_linhas_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    O relatório do SIAFI tem cabeçalhos nas primeiras linhas.
    Esta função localiza onde os dados reais começam e
    retorna apenas as linhas de dados, já com colunas renomeadas.
    """
    # No relatório de dezembro/2024, os dados começam na linha 6 (índice 6)
    # e as colunas relevantes são 0, 1, 2, 3, 4, 5
    df_dados = df.iloc[6:, :6].copy()
    df_dados.columns = [
        "nd_descricao",
        "nd_codigo",
        "subitem",
        "subitem_descricao",
        "valor_empenhado",
        "valor_liquidado",
    ]
    df_dados = df_dados.reset_index(drop=True)
    return df_dados


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e converte os tipos de dados do DataFrame.
    """
    # Remove linhas completamente vazias
    df = df.dropna(how="all")

    # Remove a última linha se for de totais (sem nd_codigo)
    df = df[df["nd_codigo"].notna()]

    # Converte nd_codigo e subitem para string sem decimais
    df["nd_codigo"] = df["nd_codigo"].astype(str).str.strip().str.replace(".0", "", regex=False)
    df["subitem"]   = df["subitem"].astype(str).str.strip().str.replace(".0", "", regex=False)

    # Converte valores para numérico — erros viram 0
    df["valor_empenhado"] = pd.to_numeric(df["valor_empenhado"], errors="coerce").fillna(0)
    df["valor_liquidado"] = pd.to_numeric(df["valor_liquidado"], errors="coerce").fillna(0)

    # Remove espaços extras nas descrições
    df["nd_descricao"]       = df["nd_descricao"].astype(str).str.strip()
    df["subitem_descricao"]  = df["subitem_descricao"].astype(str).str.strip()

    # Remove linhas com empenhado e liquidado ambos zerados
    df = df[~((df["valor_empenhado"] == 0) & (df["valor_liquidado"] == 0))]

    return df


def classificar_despesas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cruza cada linha do relatório com o mapeamento
    e adiciona as colunas 'objetivo' e 'categoria'.
    Linhas não mapeadas recebem 'Não mapeado'.
    """
    objetivos  = []
    categorias = []

    for _, row in df.iterrows():
        resultado = get_mapeamento_por_nd(row["nd_codigo"], row["subitem"])
        if resultado:
            objetivos.append(resultado["objetivo"])
            categorias.append(resultado["categoria"])
        else:
            objetivos.append("Não mapeado")
            categorias.append("Não mapeado")

    df["objetivo"]  = objetivos
    df["categoria"] = categorias

    return df


def processar_relatorio(arquivo, mes: str, ano: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Função principal — executa todo o pipeline de processamento.
    Retorna dois DataFrames:
      - df_completo: todas as linhas classificadas
      - df_nao_mapeado: apenas as linhas que não encontraram correspondência
    """
    df_bruto        = ler_relatorio(arquivo)
    df_dados        = identificar_linhas_dados(df_bruto)
    df_limpo        = limpar_dados(df_dados)
    df_classificado = classificar_despesas(df_limpo)

    # Adiciona mês e ano como colunas
    df_classificado["mes"] = mes
    df_classificado["ano"] = ano

    df_nao_mapeado = df_classificado[df_classificado["objetivo"] == "Não mapeado"].copy()

    return df_classificado, df_nao_mapeado

