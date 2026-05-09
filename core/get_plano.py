# =============================================================================
# PORTA DE ENTRADA DO PLANO DE AÇÃO
# Toda vez que o sistema precisar de dados do plano, passa por aqui.
# Nunca acesse config/plano_acao.py diretamente nas outras partes do sistema.
#
# =============================================================================
# 
# FLUXO ENTRE get_plano E mapeamento.py:
# relatório: ND 339018, subitem 1
#          ↓
#  get_mapeamento_por_nd("339018", "1")
#          ↓ -- descobre que é objetivo "R2"
#  get_objetivo(2026, "R2")
#          ↓ -- descobre que R2 tem meta 10% e orçamento R$21.000
#  indicadores.py calcula o % de 
#
# =============================================================================
#
# IMPLEMENTAÇÃO FUTURA: quando houver suporte a múltiplos anos,
# esta função será o único lugar a ser modificado — ela passará a
# ler o arquivo do plano enviado pelo setor em vez de retornar dados fixos.
# =============================================================================

from config.plano_acao import PLANO_2026


def get_plano(ano: int) -> dict:
    """
    Retorna os dados completos do plano de ação para o ano informado.
    """
    planos = {
        2026: PLANO_2026,
    }

    if ano not in planos:
        raise ValueError(f"Plano de ação para o ano {ano} não encontrado. Anos disponíveis: {list(planos.keys())}")

    return planos[ano]


def get_perspectivas(ano: int) -> dict:
    """
    Retorna as perspectivas do plano para o ano informado.
    """
    return get_plano(ano)["perspectivas"]


def get_objetivo(ano: int, cod_objetivo: str) -> dict:
    """
    Retorna os dados de um objetivo específico.
    Exemplo: get_objetivo(2026, "R2")
    """
    perspectivas = get_perspectivas(ano)

    for perspectiva in perspectivas.values():
        objetivos = perspectiva["objetivos"]
        if cod_objetivo in objetivos:
            return objetivos[cod_objetivo]

    raise ValueError(f"Objetivo '{cod_objetivo}' não encontrado no plano {ano}.")


def get_meta_indicador(ano: int, cod_objetivo: str, cod_indicador: str) -> float:
    """
    Retorna a meta numérica de um indicador específico.
    Exemplo: get_meta_indicador(2026, "R2", "R2.1") → 0.10
    """
    objetivo = get_objetivo(ano, cod_objetivo)

    indicadores = objetivo["indicadores"]
    if cod_indicador not in indicadores:
        raise ValueError(f"Indicador '{cod_indicador}' não encontrado no objetivo '{cod_objetivo}'.")

    return indicadores[cod_indicador]["meta"]


def get_valor_orcado(ano: int, cod_objetivo: str) -> float:
    """
    Retorna o valor orçado para um objetivo específico.
    Exemplo: get_valor_orcado(2026, "P5") → 288504.32
    """
    return get_objetivo(ano, cod_objetivo)["valor_orcado"]