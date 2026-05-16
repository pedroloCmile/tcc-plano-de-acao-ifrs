# =============================================================================
# MAPEAMENTO: PI + ND × Plano de Ação 2026
# Liga cada combinação PI + ND do relatório mensal ao objetivo estratégico
# e à categoria agregada correspondente no plano de ação.
#
# REGRA ESPECIAL O1:
# PI L20RLP0100I + ND 339039 e PI L20RLP6000I + ND 339030:
# Se a coluna 'observacao' contém a palavra 'MANUTENÇÃO' (case insensitive)
# → objetivo O1, categoria Infraestrutura e Manutenção
# Caso contrário
# → objetivo FUNC, categoria Funcionamento e Contratos
# =============================================================================

MAPEAMENTO_PI_ND = [

    # ── P4 — Tecnologia da Informação ─────────────────────────────────────────
    {"pi": "L20RLP3500I", "nd": "339039", "objetivo": "P4",  "categoria": "Tecnologia da Informação"},
    {"pi": "L20RGP3500I", "nd": "449052", "objetivo": "P4",  "categoria": "Tecnologia da Informação"},
    {"pi": "L20RLP3500I", "nd": "339040", "objetivo": "P4", "categoria": "Tecnologia da Informação"},


    # ── P5 — Assistência Estudantil ───────────────────────────────────────────
    {"pi": "L21IHP1900E", "nd": "339039", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2994P1900I", "nd": "339030", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2994P1900I", "nd": "339039", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2994P1900I", "nd": "449052", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2294P2300R", "nd": "339030", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2294P2300R", "nd": "339039", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2294P2300R", "nd": "449052", "objetivo": "P5",  "categoria": "Assistência Estudantil"},
    {"pi": "L2994P2300R", "nd": "339018", "objetivo": "P5", "categoria": "Assistência Estudantil"},

    # ── P6 — Alimentação ──────────────────────────────────────────────────────
    {"pi": "L21IVP2300R", "nd": "339032", "objetivo": "P6",  "categoria": "Alimentação"},
    {"pi": "FNDE",        "nd": "339032", "objetivo": "P6",  "categoria": "Alimentação"},

    # ── O1 — Infraestrutura e Manutenção ──────────────────────────────────────
    # L20RLP0100I + 339039 e L20RLP6000I + 339030 têm regra especial
    # tratada na função get_mapeamento_por_pi_nd() abaixo
    {"pi": "L20RLP9500I", "nd": "449052", "objetivo": "O1",  "categoria": "Infraestrutura e Manutenção"},
    {"pi": "L20RGP6000I", "nd": "449052", "objetivo": "O1",  "categoria": "Infraestrutura e Manutenção"},

    # ── RC — Resolução CONSUP ─────────────────────────────────────────────────
    {"pi": "L21B3P1900I", "nd": "339018", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P1900I", "nd": "339020", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P1900I", "nd": "449020", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P2000I", "nd": "339018", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P2000I", "nd": "339020", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P2000I", "nd": "449020", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P2100I", "nd": "339018", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P2100I", "nd": "339020", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L21B3P2100I", "nd": "449020", "objetivo": "RC",  "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"pi": "L4572P5600I", "nd": "339039", "objetivo": "RC",  "categoria": "Capacitação e Desenvolvimento"},
    {"pi": "L4572P5600I", "nd": "339014", "objetivo": "RC",  "categoria": "Capacitação e Desenvolvimento"},
    {"pi": "L4572P5600I", "nd": "339033", "objetivo": "RC",  "categoria": "Capacitação e Desenvolvimento"},

    # ── FUNC — Funcionamento e Contratos ──────────────────────────────────────
    # L20RLP0100I + 339039 tem regra especial tratada abaixo
    # L20RLP6000I + 339030 tem regra especial tratada abaixo
    {"pi": "L20RLP0100I", "nd": "339014", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP0100I", "nd": "339040", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP0100I", "nd": "339033", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP0100I", "nd": "339047", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP0100I", "nd": "339093", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP0100I", "nd": "339092", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP1900I", "nd": "339030", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP1900I", "nd": "339039", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},
    {"pi": "L20RLP2300I", "nd": "339092", "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"},

]

# PIs e NDs com regra especial baseada na observação
REGRA_ESPECIAL = [
    {"pi": "L20RLP0100I", "nd": "339039"},
    {"pi": "L20RLP6000I", "nd": "339030"},
]


def get_mapeamento():
    """Retorna o mapeamento completo como lista de dicionários."""
    return MAPEAMENTO_PI_ND


def get_mapeamento_por_pi_nd(pi: str, nd: str, observacao: str = "") -> dict | None:
    """
    Recebe um PI, uma ND e opcionalmente uma observação.
    Retorna o objetivo e categoria correspondentes.
    Retorna None se não encontrar correspondência.

    Regra especial O1:
    - L20RLP0100I + 339039
    - L20RLP6000I + 339030
    Se observação contém 'MANUTENÇÃO' → O1 / Infraestrutura e Manutenção
    Caso contrário → FUNC / Funcionamento e Contratos
    """
    pi  = str(pi).strip()
    nd  = str(nd).strip()
    obs = str(observacao).upper() if observacao else ""

    # Verifica regra especial primeiro
    for regra in REGRA_ESPECIAL:
        if regra["pi"] == pi and regra["nd"] == nd:
            if "MANUT" in obs:
                return {"pi": pi, "nd": nd, "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"}
            else:
                return {"pi": pi, "nd": nd, "objetivo": "FUNC", "categoria": "Funcionamento e Contratos"}

    # Busca no mapeamento padrão
    for item in MAPEAMENTO_PI_ND:
        if item["pi"] == pi and item["nd"] == nd:
            return item

    return None