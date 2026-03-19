# =============================================================================
# INTEGRAÇÃO COM GOOGLE SHEETS
# Responsável por ler e escrever dados na planilha do projeto.
# Nunca chame este arquivo diretamente nas pages — use as funções abaixo.
# =============================================================================

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# ── Configurações ─────────────────────────────────────────────────────────────

CREDENTIALS_FILE = "credentials-dash-ifrs.json"
SPREADSHEET_ID   = "1kpwubw1XdvPoaScLwAM1dCOXPmQhhU1zWH6JgFfaPfU"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Nomes das abas
ABA_DADOS       = "dados_processados"
ABA_UPLOADS_LOG = "uploads_log"
ABA_LOGS_ERROS  = "logs_erros"
ABA_CONFIG      = "config"


# ── Conexão ───────────────────────────────────────────────────────────────────

def conectar() -> gspread.Spreadsheet:
    """
    Autentica com a API do Google e retorna o objeto da planilha.
    """
    creds  = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


# ── Escrita ───────────────────────────────────────────────────────────────────

def salvar_dados_processados(df: pd.DataFrame, mes: str, ano: int) -> None:
    """
    Acumula os dados processados na aba dados_processados.
    Remove registros do mesmo mês/ano antes de inserir os novos
    para evitar duplicatas em caso de reenvio.
    """
    sh  = conectar()
    aba = sh.worksheet(ABA_DADOS)

    # Carrega dados existentes
    dados_existentes = aba.get_all_records()

    if dados_existentes:
        df_existente = pd.DataFrame(dados_existentes)
        # Remove registros do mesmo mês e ano para evitar duplicata
        df_existente = df_existente[
            ~((df_existente["mes"] == mes) & (df_existente["ano"].astype(str) == str(ano)))
        ]
    else:
        df_existente = pd.DataFrame()

    # Prepara novo df para salvar
    df_export = df.copy()
    df_export["valor_empenhado"] = df_export["valor_empenhado"].apply(lambda x: str(round(float(x), 2)))
    df_export["valor_liquidado"] = df_export["valor_liquidado"].apply(lambda x: str(round(float(x), 2)))

    # Combina existente com novo
    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_export], ignore_index=True)
    else:
        df_final = df_export

    # Reescreve tudo
    aba.clear()
    aba.update([df_final.columns.tolist()] + df_final.values.tolist())

def salvar_log_upload(nome_arquivo: str, mes: str, ano: int, total_linhas: int, nao_mapeadas: int) -> None:
    """
    Registra cada upload realizado na aba uploads_log.
    """
    sh  = conectar()
    aba = sh.worksheet(ABA_UPLOADS_LOG)
    aba.append_row([nome_arquivo, mes, ano, total_linhas, nao_mapeadas])


def salvar_erros(df_nao_mapeado: pd.DataFrame) -> None:
    """
    Salva as linhas não mapeadas na aba logs_erros.
    Substitui os dados a cada novo upload.
    """
    if df_nao_mapeado.empty:
        return
    sh  = conectar()
    aba = sh.worksheet(ABA_LOGS_ERROS)
    aba.clear()
    aba.update([df_nao_mapeado.columns.tolist()] + df_nao_mapeado.values.tolist())


# ── Leitura ───────────────────────────────────────────────────────────────────

def carregar_dados_processados() -> pd.DataFrame:
    """
    Lê os dados processados da aba dados_processados e retorna um DataFrame.
    """
    sh    = conectar()
    aba   = sh.worksheet(ABA_DADOS)
    dados = aba.get_all_records()

    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados)
    df["valor_empenhado"] = pd.to_numeric(df["valor_empenhado"].astype(str).str.replace(",", "."), errors="coerce").fillna(0)
    df["valor_liquidado"] = pd.to_numeric(df["valor_liquidado"].astype(str).str.replace(",", "."), errors="coerce").fillna(0)

    return df


def carregar_log_uploads() -> pd.DataFrame:
    """
    Lê o histórico de uploads realizados.
    """
    sh    = conectar()
    aba   = sh.worksheet(ABA_UPLOADS_LOG)
    dados = aba.get_all_records()

    if not dados:
        return pd.DataFrame()

    return pd.DataFrame(dados)