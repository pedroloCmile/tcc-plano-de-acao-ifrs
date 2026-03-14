# =============================================================================
# MAPEAMENTO: Natureza de Despesa (ND) × Plano de Ação 2026
# Liga cada ND + subitem do relatório mensal ao objetivo estratégico
# e à categoria agregada correspondente no plano de ação.
# =============================================================================

MAPEAMENTO_ND = [

    # ── RESULTADOS INSTITUCIONAIS ─────────────────────────────────────────────

    {"nd": "339018", "subitem": "4",  "objetivo": "R2", "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"nd": "339018", "subitem": "1",  "objetivo": "R2", "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"nd": "339020", "subitem": "1",  "objetivo": "R2", "categoria": "Bolsas e Auxílios Acadêmicos"},
    {"nd": "449020", "subitem": "1",  "objetivo": "R2", "categoria": "Bolsas e Auxílios Acadêmicos"},

    # ── PROCESSOS — Assistência Estudantil ────────────────────────────────────

    {"nd": "339032", "subitem": "3",  "objetivo": "P5", "categoria": "Assistência Estudantil"},
    {"nd": "339039", "subitem": "65", "objetivo": "P5", "categoria": "Assistência Estudantil"},
    {"nd": "339039", "subitem": "3",  "objetivo": "P5", "categoria": "Assistência Estudantil"},

    # ── PROCESSOS — Alimentação ───────────────────────────────────────────────

    {"nd": "339030", "subitem": "21", "objetivo": "P6", "categoria": "Alimentação"},
    {"nd": "339030", "subitem": "4",  "objetivo": "P6", "categoria": "Alimentação"},
    {"nd": "339039", "subitem": "46", "objetivo": "P6", "categoria": "Alimentação"},

    # ── PROCESSOS — Tecnologia da Informação ──────────────────────────────────

    {"nd": "339030", "subitem": "17", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "339039", "subitem": "47", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "339039", "subitem": "58", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "339040", "subitem": "11", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "339040", "subitem": "12", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "339040", "subitem": "16", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "339139", "subitem": "90", "objetivo": "P4", "categoria": "Tecnologia da Informação"},
    {"nd": "449052", "subitem": "35", "objetivo": "P4", "categoria": "Tecnologia da Informação"},

    # ── PROCESSOS — Sustentabilidade e Utilidades ─────────────────────────────

    {"nd": "339039", "subitem": "43", "objetivo": "P2", "categoria": "Sustentabilidade e Utilidades"},
    {"nd": "339039", "subitem": "44", "objetivo": "P2", "categoria": "Sustentabilidade e Utilidades"},
    {"nd": "339047", "subitem": "22", "objetivo": "P2", "categoria": "Sustentabilidade e Utilidades"},

    # ── PESSOAS E CONHECIMENTO — Capacitação ─────────────────────────────────

    {"nd": "339014", "subitem": "14", "objetivo": "PC3", "categoria": "Capacitação e Desenvolvimento"},
    {"nd": "339033", "subitem": "1",  "objetivo": "PC3", "categoria": "Capacitação e Desenvolvimento"},
    {"nd": "339039", "subitem": "48", "objetivo": "PC3", "categoria": "Capacitação e Desenvolvimento"},

    # ── ORÇAMENTO — Infraestrutura e Manutenção ───────────────────────────────

    {"nd": "339030", "subitem": "24", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "339030", "subitem": "25", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "339030", "subitem": "26", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "339030", "subitem": "42", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "339030", "subitem": "28", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "339039", "subitem": "16", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "339039", "subitem": "17", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "449052", "subitem": "12", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "449052", "subitem": "33", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},
    {"nd": "449052", "subitem": "34", "objetivo": "O1", "categoria": "Infraestrutura e Manutenção"},

    # ── ORÇAMENTO — Funcionamento e Contratos ─────────────────────────────────

    {"nd": "339039", "subitem": "78", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339039", "subitem": "77", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339039", "subitem": "79", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339039", "subitem": "84", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339030", "subitem": "22", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339030", "subitem": "33", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339030", "subitem": "11", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339030", "subitem": "35", "objetivo": "O1", "categoria": "Funcionamento e Contratos"},
    {"nd": "339047", "subitem": "8",  "objetivo": "O1", "categoria": "Funcionamento e Contratos"},

    # ── ORÇAMENTO — Restos a Pagar ────────────────────────────────────────────

    {"nd": "339092", "subitem": "39", "objetivo": "O3", "categoria": "Restos a Pagar / Ajustes"},
    {"nd": "339093", "subitem": "2",  "objetivo": "O3", "categoria": "Restos a Pagar / Ajustes"},

]


def get_mapeamento():
    """Retorna o mapeamento completo como lista de dicionários."""
    return MAPEAMENTO_ND


def get_mapeamento_por_nd(nd: str, subitem: str) -> dict | None:
    """
    Recebe uma ND e um subitem e retorna o objetivo e categoria correspondentes.
    Retorna None se não encontrar o par ND + subitem no mapeamento.
    """
    for item in MAPEAMENTO_ND:
        if item["nd"] == nd and item["subitem"] == subitem:
            return item
    return None