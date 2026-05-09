# =============================================================================
# PROCESSAMENTO DO RELATÓRIO MENSAL
# Responsável por ler, limpar e classificar o xlsx do SIAFI.
# Retorna um DataFrame tratado e classificado conforme o mapeamento.
# =============================================================================

import pandas as pd
from core.mapeamento import get_mapeamento_por_pi_nd

# ── Dicionários de decodificação do PI ───────────────────────────────────────

ACOES = {
    "20RG": "Investimento",
    "20RL": "Funcionamento e Aquisição de Livros",
    "21IH": "AEE — Atendimento Educacional Especializado",
    "21IV": "Apoio à Alimentação do Estudante",
    "2994": "Assistência",
    "4572": "Capacitação",
    "21B3": "Ensino, Pesquisa e Extensão",
}

CATEGORIAS_PI = {
    "01": "Gestão Administrativa",
    "15": "Emendas",
    "19": "Ensino",
    "20": "Pesquisa",
    "21": "Extensão",
    "22": "Educação a Distância",
    "23": "Assistência",
    "35": "Tecnologia e Inovação — TI",
    "41": "Obras — Construção",
    "42": "Obras — Ampliação",
    "43": "Obras — Reforma",
    "56": "Formação e Capacitação",
    "57": "Eventos",
    "60": "Aquisições — Material, Mobiliário e Equipamentos",
    "62": "Veículos",
    "95": "Acervo Bibliográfico",
}

PUBLICOS_PI = {
    "I": "Educação Integral",
    "E": "Educação Especial / Acessibilidade",
    "R": "Vulnerabilidade Social",
}

COLUNAS = {
    "col_pi":           "pi",
    "col_pi_descricao": "pi_descricao",
    "col_nd_codigo":    "nd_codigo",
    "col_nd_descricao": "nd_descricao",
    "col_subitem":      "subitem",
    "col_subitem_desc": "subitem_descricao",
    "col_observacao":   "observacao",
    "col_empenhado":    "valor_empenhado",
    "col_liquidado":    "valor_liquidado",
    "col_pago":         "valor_pago",
}


# ── Extração de informações do PI ─────────────────────────────────────────────

def extrair_info_pi(pi: str) -> dict:
    """
    Extrai ação, categoria de apropriação e público a partir do código PI.
    Máscara: L xxxx P yy 00 z
    Exemplo: L20RLP3500I
      ação      = posições 1-4 = 20RL
      categoria = posições 6-7 = 35
      público   = última posição = I
    """
    pi = str(pi).strip()

    if not pi.startswith("L") or len(pi) < 10:
        return {
            "acao_cod":       "—",
            "acao_desc":      "Não identificado",
            "categoria_cod":  "—",
            "categoria_desc": "Não identificado",
            "publico_cod":    "—",
            "publico_desc":   "Não identificado",
        }

    acao_cod      = pi[1:5]
    categoria_cod = pi[6:8]
    publico_cod   = pi[-1]

    return {
        "acao_cod":       acao_cod,
        "acao_desc":      ACOES.get(acao_cod, f"Ação {acao_cod}"),
        "categoria_cod":  categoria_cod,
        "categoria_desc": CATEGORIAS_PI.get(categoria_cod, f"Categoria {categoria_cod}"),
        "publico_cod":    publico_cod,
        "publico_desc":   PUBLICOS_PI.get(publico_cod, f"Público {publico_cod}"),
    }


# ── Detecção automática do mês ────────────────────────────────────────────────

def detectar_mes_relatorio(df: pd.DataFrame) -> str | None:
    """
    Tenta detectar o mês de referência do relatório a partir da linha 3.
    Retorna o nome do mês em português ou None se não encontrar.
    """
    meses_validos = [
        "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL",
        "MAIO", "JUNHO", "JULHO", "AGOSTO",
        "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
    ]

    meses_formatados = {
        "JANEIRO": "Janeiro", "FEVEREIRO": "Fevereiro",
        "MARÇO": "Março", "ABRIL": "Abril",
        "MAIO": "Maio", "JUNHO": "Junho",
        "JULHO": "Julho", "AGOSTO": "Agosto",
        "SETEMBRO": "Setembro", "OUTUBRO": "Outubro",
        "NOVEMBRO": "Novembro", "DEZEMBRO": "Dezembro"
    }

    try:
        linha3 = df.iloc[2, :].tolist()
        for valor in linha3:
            if valor and str(valor).strip().upper() in meses_validos:
                return meses_formatados[str(valor).strip().upper()]
    except Exception:
        pass

    return None


# ── Pipeline de processamento ─────────────────────────────────────────────────

def ler_relatorio(arquivo) -> pd.DataFrame:
    """
    Lê o xlsx ou xls do SIAFI e retorna um DataFrame bruto.
    """
    nome   = arquivo.name if hasattr(arquivo, "name") else str(arquivo)
    engine = "xlrd" if nome.endswith(".xls") else "openpyxl"
    df     = pd.read_excel(arquivo, header=None, engine=engine)
    return df


def validar_estrutura(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Valida se o arquivo tem a estrutura esperada.
    """
    if df.shape[1] < 10:
        return False, f"O arquivo tem apenas {df.shape[1]} colunas. São esperadas pelo menos 10."

    if df.shape[0] < 5:
        return False, "O arquivo tem poucas linhas. Verifique se o relatório está completo."

    df_teste = df.iloc[3:, :10].copy()
    df_teste.columns = [
        "pi", "pi_descricao", "nd_codigo", "nd_descricao",
        "subitem", "subitem_descricao", "observacao",
        "valor_empenhado", "valor_liquidado", "valor_pago",
    ]
    df_teste = df_teste.dropna(how="all")

    nd_valores   = df_teste["nd_codigo"].dropna().astype(str).str.replace(".0", "", regex=False)
    nd_numericos = nd_valores.str.match(r"^\d+$").sum()
    if nd_numericos == 0:
        return False, "A coluna de código ND não contém valores numéricos. Verifique o formato do arquivo."

    valores_numericos = pd.to_numeric(
        df_teste["valor_empenhado"].dropna(), errors="coerce"
    ).dropna()
    if len(valores_numericos) == 0:
        return False, "A coluna de valor empenhado não contém valores numéricos. Verifique o formato do arquivo."

    return True, "Arquivo válido."


def identificar_linhas_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Localiza onde os dados reais começam e retorna
    as linhas de dados com colunas renomeadas.
    """
    df_dados = df.iloc[3:, :10].copy()
    df_dados.columns = [
        "pi",
        "pi_descricao",
        "nd_codigo",
        "nd_descricao",
        "subitem",
        "subitem_descricao",
        "observacao",
        "valor_empenhado",
        "valor_liquidado",
        "valor_pago",
    ]
    df_dados = df_dados.reset_index(drop=True)
    return df_dados


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa, converte e enriquece os dados do DataFrame.
    """
    df = df.dropna(how="all")
    df = df[df["nd_codigo"].notna()]

    df["nd_codigo"] = df["nd_codigo"].astype(str).str.strip().str.replace(".0", "", regex=False)
    df["subitem"]   = df["subitem"].astype(str).str.strip().str.replace(".0", "", regex=False)
    df["pi"]        = df["pi"].astype(str).str.strip()
    df["observacao"] = df["observacao"].fillna("").astype(str).str.strip()

    df["valor_empenhado"] = pd.to_numeric(df["valor_empenhado"], errors="coerce").fillna(0)
    df["valor_liquidado"] = pd.to_numeric(df["valor_liquidado"], errors="coerce").fillna(0)
    df["valor_pago"]      = pd.to_numeric(df["valor_pago"],      errors="coerce").fillna(0)

    df["nd_descricao"]      = df["nd_descricao"].astype(str).str.strip()
    df["subitem_descricao"] = df["subitem_descricao"].astype(str).str.strip()
    df["pi_descricao"]      = df["pi_descricao"].astype(str).str.strip()

    df = df[~((df["valor_empenhado"] == 0) & (df["valor_liquidado"] == 0))]

    info_pi = df["pi"].apply(extrair_info_pi)
    df["acao_cod"]       = info_pi.apply(lambda x: x["acao_cod"])
    df["acao_desc"]      = info_pi.apply(lambda x: x["acao_desc"])
    df["categoria_cod"]  = info_pi.apply(lambda x: x["categoria_cod"])
    df["categoria_desc"] = info_pi.apply(lambda x: x["categoria_desc"])
    df["publico_cod"]    = info_pi.apply(lambda x: x["publico_cod"])
    df["publico_desc"]   = info_pi.apply(lambda x: x["publico_desc"])

    return df


def classificar_despesas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cruza cada linha do relatório com o mapeamento PI + ND.
    """
    objetivos  = []
    categorias = []

    for _, row in df.iterrows():
        resultado = get_mapeamento_por_pi_nd(
            pi=row["pi"],
            nd=row["nd_codigo"],
            observacao=row["observacao"],
        )
        if resultado:
            objetivos.append(resultado["objetivo"])
            categorias.append(resultado["categoria"])
        else:
            objetivos.append("Não mapeado")
            categorias.append("Não mapeado")

    df["objetivo"]  = objetivos
    df["categoria"] = categorias

    return df


def verificar_inconsistencias(df: pd.DataFrame) -> list[str]:
    """
    Verifica inconsistências nos dados processados.
    """
    alertas = []

    if not df[df["valor_empenhado"] < 0].empty:
        alertas.append(f"⚠️ {len(df[df['valor_empenhado'] < 0])} linha(s) com valor empenhado negativo.")
    if not df[df["valor_liquidado"] < 0].empty:
        alertas.append(f"⚠️ {len(df[df['valor_liquidado'] < 0])} linha(s) com valor liquidado negativo.")
    if not df[df["valor_pago"] < 0].empty:
        alertas.append(f"⚠️ {len(df[df['valor_pago'] < 0])} linha(s) com valor pago negativo.")
    if not df[df["valor_liquidado"] > df["valor_empenhado"]].empty:
        alertas.append(f"⚠️ {len(df[df['valor_liquidado'] > df['valor_empenhado']])} linha(s) com liquidado maior que empenhado.")
    if not df[df["valor_pago"] > df["valor_liquidado"]].empty:
        alertas.append(f"⚠️ {len(df[df['valor_pago'] > df['valor_liquidado']])} linha(s) com pago maior que liquidado.")

    return alertas


def processar_relatorio(arquivo, mes: str, ano: int) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    """
    Função principal — executa todo o pipeline de processamento.
    """
    df_bruto = ler_relatorio(arquivo)

    valido, mensagem = validar_estrutura(df_bruto)
    if not valido:
        raise ValueError(mensagem)

    df_dados        = identificar_linhas_dados(df_bruto)
    df_limpo        = limpar_dados(df_dados)
    df_classificado = classificar_despesas(df_limpo)

    df_classificado["mes"] = mes
    df_classificado["ano"] = ano

    df_nao_mapeado = df_classificado[df_classificado["objetivo"] == "Não mapeado"].copy()
    alertas        = verificar_inconsistencias(df_classificado)

    return df_classificado, df_nao_mapeado, alertas