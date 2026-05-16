# =============================================================================
# CÁLCULO DOS INDICADORES DO PLANO DE AÇÃO
# Recebe o DataFrame processado e retorna os indicadores calculados
# para alimentar os dashboards.
# =============================================================================

import pandas as pd
from core.get_plano import (
    get_plano,
    get_perspectivas,
    get_objetivo,
    get_valor_orcado,
    get_meta_indicador,
)


# ── Execução por Objetivo ─────────────────────────────────────────────────────

def calcular_execucao_por_objetivo(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """
    Agrupa os valores empenhados, liquidados e pagos por objetivo estratégico.
    Cruza com o valor orçado do plano e calcula o percentual de execução.
    """
    df_mapeado = df[df["objetivo"] != "Não mapeado"].copy()

    agrupado = df_mapeado.groupby("objetivo").agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
        total_pago     =("valor_pago",      "sum"),
    ).reset_index()

    valores_orcados   = []
    percentual_empenh = []
    percentual_liquid = []
    descricoes        = []

    for _, row in agrupado.iterrows():
        cod = row["objetivo"]
        try:
            orcado = get_valor_orcado(ano, cod)
            obj    = get_objetivo(ano, cod)
            desc   = obj["descricao"]
        except ValueError:
            orcado = 0
            desc   = cod

        valores_orcados.append(orcado)
        descricoes.append(desc)

        if orcado > 0:
            percentual_empenh.append(round(row["total_empenhado"] / orcado * 100, 2))
            percentual_liquid.append(round(row["total_liquidado"] / orcado * 100, 2))
        else:
            percentual_empenh.append(None)
            percentual_liquid.append(None)

    agrupado["descricao"]      = descricoes
    agrupado["valor_orcado"]   = valores_orcados
    agrupado["perc_empenhado"] = percentual_empenh
    agrupado["perc_liquidado"] = percentual_liquid

    return agrupado


# ── Execução por Categoria ────────────────────────────────────────────────────

def calcular_execucao_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os valores por categoria agregada.
    """
    df_mapeado = df[df["categoria"] != "Não mapeado"].copy()

    agrupado = df_mapeado.groupby("categoria").agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
        total_pago     =("valor_pago",      "sum"),
    ).reset_index()

    agrupado = agrupado.sort_values("total_empenhado", ascending=False)

    return agrupado


# ── Execução por Perspectiva ──────────────────────────────────────────────────

def calcular_execucao_por_perspectiva(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """
    Agrupa os valores por perspectiva estratégica.
    """
    perspectivas = get_perspectivas(ano)

    obj_para_perspectiva = {}
    for nome_persp, dados_persp in perspectivas.items():
        for cod_obj in dados_persp["objetivos"]:
            obj_para_perspectiva[cod_obj] = nome_persp

    df_mapeado = df[df["objetivo"] != "Não mapeado"].copy()
    df_mapeado["perspectiva"] = df_mapeado["objetivo"].map(obj_para_perspectiva)

    agrupado = df_mapeado.groupby("perspectiva").agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
        total_pago     =("valor_pago",      "sum"),
    ).reset_index()

    return agrupado


# ── Execução por Ação ─────────────────────────────────────────────────────────

def calcular_execucao_por_acao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os valores por ação (extraída do PI).
    É o nível mais alto de agrupamento do sistema.
    """
    df_mapeado = df[df["acao_desc"] != "Não identificado"].copy()

    agrupado = df_mapeado.groupby(["acao_cod", "acao_desc"]).agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
        total_pago     =("valor_pago",      "sum"),
    ).reset_index()

    agrupado = agrupado.sort_values("total_empenhado", ascending=False)

    return agrupado


# ── Execução por Categoria de Apropriação ────────────────────────────────────

def calcular_execucao_por_categoria_pi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os valores por categoria de apropriação do PI.
    Nível intermediário entre ação e objetivo.
    """
    df_valido = df[df["categoria_desc"] != "Não identificado"].copy()

    agrupado = df_valido.groupby(["categoria_cod", "categoria_desc"]).agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
        total_pago     =("valor_pago",      "sum"),
    ).reset_index()

    agrupado = agrupado.sort_values("total_empenhado", ascending=False)

    return agrupado


# ── Resumo Geral ──────────────────────────────────────────────────────────────

def calcular_resumo_geral(df: pd.DataFrame, ano: int) -> dict:
    """
    Retorna os números gerais do relatório para os cards do dashboard.
    """
    total_empenhado  = df["valor_empenhado"].sum()
    total_liquidado  = df["valor_liquidado"].sum()
    total_pago       = df["valor_pago"].sum() if "valor_pago" in df.columns else 0
    total_linhas     = len(df)
    nao_mapeadas     = len(df[df["objetivo"] == "Não mapeado"])
    total_acoes      = df["acao_cod"].nunique() if "acao_cod" in df.columns else 0

    plano = get_plano(ano)
    total_orcado = sum(
        obj["valor_orcado"]
        for persp in plano["perspectivas"].values()
        for obj in persp["objetivos"].values()
    )

    perc_execucao = round(total_empenhado / total_orcado * 100, 2) if total_orcado > 0 else 0

    return {
        "total_orcado":    total_orcado,
        "total_empenhado": total_empenhado,
        "total_liquidado": total_liquidado,
        "total_pago":      total_pago,
        "perc_execucao":   perc_execucao,
        "total_linhas":    total_linhas,
        "nao_mapeadas":    nao_mapeadas,
        "total_acoes":     total_acoes,
    }


# ── Indicadores Específicos do Plano ─────────────────────────────────────────

def calcular_indicador_ti(df_mes: pd.DataFrame, df_acumulado: pd.DataFrame, ano: int) -> dict:
    """
    P4.1 — % execução orçamentária em TI.
    Calcula sobre o acumulado do ano.
    """
    total_acumulado = df_acumulado["valor_empenhado"].sum()
    ti_acumulado    = df_acumulado[df_acumulado["categoria"] == "Tecnologia da Informação"]["valor_empenhado"].sum()

    perc_realizado = round(ti_acumulado / total_acumulado * 100, 4) if total_acumulado > 0 else 0
    meta           = get_meta_indicador(ano, "P4", "P4.1") * 100
    falta          = round(meta - perc_realizado, 4)

    return {
        "indicador":   "P4.1",
        "descricao":   "% execução orçamentária em TI",
        "meta":        meta,
        "realizado":   perc_realizado,
        "falta":       max(falta, 0),
        "atingido":    perc_realizado >= meta,
        "base":        "acumulado",
    }


def calcular_indicador_alimentacao(df_mes: pd.DataFrame, df_acumulado: pd.DataFrame, ano: int) -> dict:
    """
    P6.1 — % execução orçamentária em alimentos.
    Calcula sobre o acumulado do ano.
    """
    total_acumulado = df_acumulado["valor_empenhado"].sum()
    alim_acumulado  = df_acumulado[df_acumulado["categoria"] == "Alimentação"]["valor_empenhado"].sum()

    perc_realizado = round(alim_acumulado / total_acumulado * 100, 4) if total_acumulado > 0 else 0
    meta           = get_meta_indicador(ano, "P6", "P6.1") * 100
    falta          = round(meta - perc_realizado, 4)

    return {
        "indicador":   "P6.1",
        "descricao":   "% execução orçamentária em alimentos",
        "meta":        meta,
        "realizado":   perc_realizado,
        "falta":       max(falta, 0),
        "atingido":    perc_realizado >= meta,
        "base":        "acumulado",
    }


def calcular_indicador_infraestrutura(df_mes: pd.DataFrame, df_acumulado: pd.DataFrame, ano: int) -> dict:
    """
    O1.1 — % investimento em infraestrutura.
    Calcula sobre o acumulado do ano.
    """
    total_acumulado = df_acumulado["valor_empenhado"].sum()
    infra_acumulado = df_acumulado[df_acumulado["categoria"] == "Infraestrutura e Manutenção"]["valor_empenhado"].sum()

    perc_realizado = round(infra_acumulado / total_acumulado * 100, 4) if total_acumulado > 0 else 0
    meta           = get_meta_indicador(ano, "O1", "O1.1") * 100
    falta          = round(meta - perc_realizado, 4)

    return {
        "indicador":   "O1.1",
        "descricao":   "% investimento em infraestrutura",
        "meta":        meta,
        "realizado":   perc_realizado,
        "falta":       max(falta, 0),
        "atingido":    perc_realizado >= meta,
        "base":        "acumulado",
    }


def calcular_todos_indicadores(df_mes: pd.DataFrame, df_acumulado: pd.DataFrame, ano: int) -> list:
    """
    Executa todos os indicadores usando o acumulado do ano.
    """
    return [
        calcular_indicador_ti(df_mes, df_acumulado, ano),
        calcular_indicador_alimentacao(df_mes, df_acumulado, ano),
        calcular_indicador_infraestrutura(df_mes, df_acumulado, ano),
    ]