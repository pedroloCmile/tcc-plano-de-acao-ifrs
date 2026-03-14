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
    Agrupa os valores empenhados e liquidados por objetivo estratégico.
    Cruza com o valor orçado do plano e calcula o percentual de execução.
    """
    # Remove linhas não mapeadas
    df_mapeado = df[df["objetivo"] != "Não mapeado"].copy()

    # Agrupa por objetivo
    agrupado = df_mapeado.groupby("objetivo").agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
    ).reset_index()

    # Adiciona valor orçado e percentual de execução
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

    agrupado["descricao"]          = descricoes
    agrupado["valor_orcado"]       = valores_orcados
    agrupado["perc_empenhado"]     = percentual_empenh
    agrupado["perc_liquidado"]     = percentual_liquid

    return agrupado


# ── Execução por Categoria ────────────────────────────────────────────────────

def calcular_execucao_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os valores empenhados e liquidados por categoria agregada.
    """
    df_mapeado = df[df["categoria"] != "Não mapeado"].copy()

    agrupado = df_mapeado.groupby("categoria").agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
    ).reset_index()

    agrupado = agrupado.sort_values("total_empenhado", ascending=False)

    return agrupado


# ── Execução por Perspectiva ──────────────────────────────────────────────────

def calcular_execucao_por_perspectiva(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """
    Agrupa os valores por perspectiva estratégica.
    """
    perspectivas = get_perspectivas(ano)

    # Monta dicionário objetivo → perspectiva
    obj_para_perspectiva = {}
    for nome_persp, dados_persp in perspectivas.items():
        for cod_obj in dados_persp["objetivos"]:
            obj_para_perspectiva[cod_obj] = nome_persp

    df_mapeado = df[df["objetivo"] != "Não mapeado"].copy()
    df_mapeado["perspectiva"] = df_mapeado["objetivo"].map(obj_para_perspectiva)

    agrupado = df_mapeado.groupby("perspectiva").agg(
        total_empenhado=("valor_empenhado", "sum"),
        total_liquidado=("valor_liquidado", "sum"),
    ).reset_index()

    return agrupado


# ── Resumo Geral ──────────────────────────────────────────────────────────────

def calcular_resumo_geral(df: pd.DataFrame, ano: int) -> dict:
    """
    Retorna um dicionário com os números gerais do relatório.
    Usado para os cards de resumo no topo do dashboard.
    """
    total_empenhado = df["valor_empenhado"].sum()
    total_liquidado = df["valor_liquidado"].sum()
    total_linhas    = len(df)
    nao_mapeadas    = len(df[df["objetivo"] == "Não mapeado"])

    # Total orçado — soma de todos os objetivos do plano
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
        "perc_execucao":   perc_execucao,
        "total_linhas":    total_linhas,
        "nao_mapeadas":    nao_mapeadas,
    }


# ── Indicadores Específicos do Plano ─────────────────────────────────────────

def calcular_indicador_ti(df: pd.DataFrame, ano: int) -> dict:
    """
    P4.1 — Percentual da execução orçamentária em despesas de TI.
    Meta: 0,70% do total empenhado.
    """
    total_empenhado = df["valor_empenhado"].sum()
    ti = df[df["categoria"] == "Tecnologia da Informação"]["valor_empenhado"].sum()

    perc_realizado = round(ti / total_empenhado * 100, 4) if total_empenhado > 0 else 0
    meta           = get_meta_indicador(ano, "P4", "P4.1") * 100

    return {
        "indicador":    "P4.1",
        "descricao":    "% execução orçamentária em TI",
        "meta":         meta,
        "realizado":    perc_realizado,
        "atingido":     perc_realizado >= meta,
    }


def calcular_indicador_alimentacao(df: pd.DataFrame, ano: int) -> dict:
    """
    P6.1 — Percentual da execução orçamentária em despesas de alimentos.
    Meta: 3% do total empenhado.
    """
    total_empenhado = df["valor_empenhado"].sum()
    alim = df[df["categoria"] == "Alimentação"]["valor_empenhado"].sum()

    perc_realizado = round(alim / total_empenhado * 100, 4) if total_empenhado > 0 else 0
    meta           = get_meta_indicador(ano, "P6", "P6.1") * 100

    return {
        "indicador":    "P6.1",
        "descricao":    "% execução orçamentária em alimentos",
        "meta":         meta,
        "realizado":    perc_realizado,
        "atingido":     perc_realizado >= meta,
    }


def calcular_indicador_infraestrutura(df: pd.DataFrame, ano: int) -> dict:
    """
    O1.1 — Percentual de investimento em infraestrutura.
    Meta: 3,60% do total empenhado.
    """
    total_empenhado = df["valor_empenhado"].sum()
    infra = df[df["categoria"] == "Infraestrutura e Manutenção"]["valor_empenhado"].sum()

    perc_realizado = round(infra / total_empenhado * 100, 4) if total_empenhado > 0 else 0
    meta           = get_meta_indicador(ano, "O1", "O1.1") * 100

    return {
        "indicador":    "O1.1",
        "descricao":    "% investimento em infraestrutura",
        "meta":         meta,
        "realizado":    perc_realizado,
        "atingido":     perc_realizado >= meta,
    }


def calcular_todos_indicadores(df: pd.DataFrame, ano: int) -> list:
    """
    Executa todos os indicadores calculáveis a partir do relatório mensal.
    Retorna uma lista de dicionários — um por indicador.
    """
    return [
        calcular_indicador_ti(ano=ano, df=df),
        calcular_indicador_alimentacao(ano=ano, df=df),
        calcular_indicador_infraestrutura(ano=ano, df=df),
    ]