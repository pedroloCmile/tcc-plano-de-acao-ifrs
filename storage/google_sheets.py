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
    Funciona tanto localmente (arquivo .json) quanto no Streamlit Cloud (Secrets).
    """
    import os

    # Streamlit Cloud — lê das Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]),
                scopes=SCOPES,
            )
            client = gspread.authorize(creds)
            return client.open_by_key(SPREADSHEET_ID)
    except Exception:
        pass

    # Local — lê do arquivo .json
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado. "
            "Configure os Secrets no Streamlit Cloud ou adicione o arquivo localmente."
        )

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

    # Prepara novo df para salvar
    df_export = df.copy()
    df_export["valor_empenhado"] = df_export["valor_empenhado"].apply(lambda x: str(round(float(x), 2)))
    df_export["valor_liquidado"] = df_export["valor_liquidado"].apply(lambda x: str(round(float(x), 2)))
    df_export["valor_pago"]      = df_export["valor_pago"].apply(lambda x: str(round(float(x), 2)))

    if dados_existentes:
        df_existente = pd.DataFrame(dados_existentes)

        # Remove registros do mesmo mês e ano para evitar duplicata
        df_existente = df_existente[
            ~((df_existente["mes"] == mes) & (df_existente["ano"].astype(str) == str(ano)))
        ]

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
    dados = aba.get_all_records(value_render_option="UNFORMATTED_VALUE")

    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados)
    df["valor_empenhado"] = pd.to_numeric(df["valor_empenhado"], errors="coerce").fillna(0)
    df["valor_liquidado"] = pd.to_numeric(df["valor_liquidado"], errors="coerce").fillna(0)

    # valor_pago pode não existir em registros antigos
    if "valor_pago" in df.columns:
        df["valor_pago"] = pd.to_numeric(df["valor_pago"], errors="coerce").fillna(0)
    else:
        df["valor_pago"] = 0

    return df


def carregar_log_uploads() -> pd.DataFrame:
    """
    Lê o histórico de uploads realizados.
    Garante o cabeçalho mesmo que tenha sido apagado acidentalmente.
    """
    CABECALHO = ["nome_arquivo", "mes", "ano", "total_linhas", "nao_mapeadas"]

    try:
        sh    = conectar()
        aba   = sh.worksheet(ABA_UPLOADS_LOG)
        dados = aba.get_all_values()

        # Aba completamente vazia
        if not dados:
            aba.append_row(CABECALHO)
            return pd.DataFrame(columns=CABECALHO)

        primeira_linha = [str(v).strip().lower() for v in dados[0]]

        # Cabeçalho presente
        if "nome_arquivo" in primeira_linha:
            registros = [r for r in dados[1:] if any(str(v).strip() for v in r)]
            if not registros:
                return pd.DataFrame(columns=CABECALHO)
            df = pd.DataFrame(registros)
            # Garante que tem exatamente 5 colunas
            if len(df.columns) >= 5:
                df = df.iloc[:, :5]
                df.columns = CABECALHO
            return df

        # Cabeçalho foi apagado — reinsere
        aba.insert_row(CABECALHO, index=1)
        registros = [r for r in dados if any(str(v).strip() for v in r)]
        if not registros:
            return pd.DataFrame(columns=CABECALHO)
        df = pd.DataFrame(registros)
        if len(df.columns) >= 5:
            df = df.iloc[:, :5]
            df.columns = CABECALHO
        return df

    except Exception as e:
        return pd.DataFrame(columns=CABECALHO)
    
def excluir_dados_mes(mes: str, ano: int) -> None:
    """
    Remove todos os registros de um mês/ano específico
    da aba dados_processados.
    """
    sh  = conectar()
    aba = sh.worksheet(ABA_DADOS)

    dados = aba.get_all_records()
    if not dados:
        return

    df = pd.DataFrame(dados)
    df = df[~((df["mes"] == mes) & (df["ano"].astype(str) == str(ano)))]

    aba.clear()
    if not df.empty:
        aba.update([df.columns.tolist()] + df.values.tolist())


def excluir_log_upload(mes: str, ano: int) -> None:
    """
    Remove o registro de um mês/ano específico
    da aba uploads_log.
    """
    CABECALHO = ["nome_arquivo", "mes", "ano", "total_linhas", "nao_mapeadas"]

    sh  = conectar()
    aba = sh.worksheet(ABA_UPLOADS_LOG)

    dados = aba.get_all_values()
    if not dados:
        return

    # Mantém cabeçalho e filtra as linhas do mês/ano
    cabecalho = dados[0]
    registros = [
        r for r in dados[1:]
        if not (len(r) >= 3 and str(r[1]).strip() == mes and str(r[2]).strip() == str(ano))
    ]

    aba.clear()
    aba.append_row(cabecalho)
    for r in registros:
        aba.append_row(r)