# ──────────────── IMPORTAÇÕES ────────────────
# Carregamento das bibliotecas essenciais:
# - os: interação com sistema operacional (variáveis de ambiente)
# - pandas: manipulação de dados em DataFrames
# - streamlit: framework para criação de aplicativos web
# - plotly: biblioteca para criação de gráficos interativos
# - sqlalchemy: ORM para conexão com banco de dados
# - dotenv: carregamento de variáveis de ambiente a partir de arquivo .env
import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ─────────────── CONEXÃO COM O BANCO ─────────
# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Cria engine de conexão com PostgreSQL usando URI de conexão
# A URI é obtida da variável de ambiente PGURI (boas práticas de segurança)
engine = create_engine(os.getenv("PGURI"))

# ─────────── FUNÇÕES AUXILIARES ───────────
def formatar_data_ptbr(dt: pd.Timestamp) -> str:
    """
    Formata um objeto Timestamp para o formato 'Dia, Mês, Ano' em português.
    Exemplo: 2025-07-16 → "16, Julho, 2025"
    
    Parâmetros:
        dt (pd.Timestamp): Data a ser formatada
    
    Retorna:
        str: Data formatada em português
    """
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    return f"{dt.day}, {meses[dt.month-1]}, {dt.year}"

# ─────────── FUNÇÕES CACHEADAS (OTIMIZADAS) ───────────
# Cache de 24 horas para evitar consultas repetidas ao banco
@st.cache_data(ttl=86_400)
def lista_tickers() -> list[str]:
    """
    Retorna lista de tickers principais (sem sufixos) formatados como:
    [PETR4, VALE3, ITUB4, ...]
    
    Técnica:
    - Usa regex para extrair o padrão básico de ticker (4 letras + 1 dígito)
    - Remove duplicatas e valores nulos
    - Ordena alfabeticamente
    """
    sql = """
        SELECT DISTINCT 
            -- Extrai apenas a parte principal do ticker (ex: PETR4 de PETR4F)
            (REGEXP_MATCH(codneg, '^([A-Z]{4}\d{1})'))[1] AS ticker_clean
        FROM cotahist_hist 
        -- Filtra apenas tickers que começam com 4 letras e 1 dígito
        WHERE codneg ~ '^[A-Z]{4}\d'  
        ORDER BY ticker_clean
    """
    # Executa consulta SQL e retorna como DataFrame
    df = pd.read_sql(sql, engine)
    
    # Remove valores nulos e retorna lista única de tickers
    return df['ticker_clean'].dropna().unique().tolist()

@st.cache_data(ttl=86_400)
def get_date_bounds() -> tuple:
    """
    Retorna as datas mínima e máxima disponíveis no banco
    (Cache de 24h para evitar consultas repetidas)
    """
    result = pd.read_sql(
        "SELECT MIN(data_operacao) AS min, MAX(data_operacao) AS max FROM cotahist_hist",
        engine
    ).iloc[0]  # Pega primeira linha do resultado
    return result["min"], result["max"]

@st.cache_data(ttl=3_600, show_spinner=False)
def load_data(t: str, ini, fim, freq: str = 'D') -> pd.DataFrame:
    """
    Carrega dados agregados do banco com otimização de performance
    
    Parâmetros:
        t (str): Ticker do ativo
        ini: Data inicial (datetime.date)
        fim: Data final (datetime.date)
        freq (str): Frequência de agregação ('D', 'W', 'M')
    
    Técnicas:
    - Agregação direta no banco usando DATE_TRUNC
    - Uso de prepared statements para segurança
    - Cache de 1 hora para consultas repetidas
    """
    # Query SQL com agregação temporal
    sql = text(f"""
        SELECT 
            DATE_TRUNC('{freq}', data_operacao) AS data_agregada,
            AVG(preco_fechamento) AS preco,
            SUM(volume) AS volume
        FROM cotahist_hist
        WHERE codneg = :t
          AND data_operacao BETWEEN :ini AND :fim
        GROUP BY data_agregada
        ORDER BY data_agregada
    """)
    
    # Executa consulta com parâmetros seguros
    df = pd.read_sql(
        sql, 
        engine,
        params={"t": t, "ini": ini, "fim": fim},
        parse_dates=["data_agregada"]  # Converte para datetime
    )
    # Padroniza nome da coluna de data
    return df.rename(columns={"data_agregada": "data_operacao"})

# ─────────── INTERFACE PRINCIPAL ─────────────
# Configuração da barra lateral (sidebar)
st.sidebar.title("Filtros")

# Obtém limites de datas do banco (com cache)
min_date, max_date = get_date_bounds()

# Seletor de ticker - Lista formatada sem sufixos
tickers = lista_tickers()
ticker = st.sidebar.selectbox(
    "Ativo", 
    options=tickers,
    # Define PETR4 como padrão se existir na lista
    index=tickers.index("PETR4") if "PETR4" in tickers else 0,
    placeholder="Digite ou selecione..."
)

# Seletor de frequência com opções traduzidas
freq = st.sidebar.radio(
    "Frequência", 
    options=["Diária", "Semanal", "Mensal"],
    index=1,  # Default = Semanal
    horizontal=True  # Layout otimizado para mobile
)
# Mapeamento das frequências para valores do PostgreSQL
freq_map = {"Diária": "D", "Semanal": "W", "Mensal": "M"}

# Seletor de intervalo de datas
data_ini, data_fim = st.sidebar.date_input(
    "Período",
    # Período padrão: últimos 6 meses até a data mais recente
    value=(max_date - pd.DateOffset(months=6), max_date),
    min_value=min_date,  # Limite inferior
    max_value=max_date   # Limite superior
)

# ─────────── CARREGAMENTO DE DADOS ───────────
# Placeholder para gráfico (permite atualização assíncrona)
chart_placeholder = st.empty()

# Indicador de carregamento
with st.spinner(f"Carregando dados para {ticker}..."):
    # Carrega dados com agregação otimizada
    df = load_data(ticker, data_ini, data_fim, freq_map[freq])
    
    # Feedback visual de conclusão
    st.toast(f"✅ {len(df)} registros carregados", icon="⚡")

# ─────────── CONSTRUÇÃO DO GRÁFICO ───────────
with chart_placeholder.container():
    # Formata datas para o título usando função auxiliar
    titulo_formatado = (
        f"{ticker} | {freq} | "
        f"{formatar_data_ptbr(pd.Timestamp(data_ini))} - "
        f"{formatar_data_ptbr(pd.Timestamp(data_fim))}"
    )
    
    # Cria figura com eixo secundário para volume
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Gráfico de linha para preços (usando WebGL para performance)
    fig.add_trace(
        go.Scattergl(
            x=df["data_operacao"],
            y=df["preco"],
            name="Preço (R$)",
            line=dict(color="#1f77b4")  # Cor consistente
        ),
        secondary_y=False,  # Eixo primário
    )
    
    # Barras para volume (inicialmente ocultas)
    fig.add_trace(
        go.Bar(
            x=df["data_operacao"],
            y=df["volume"],
            name="Volume",
            marker_color="lightgray",  # Cor neutra
            opacity=0.4,  # Transparência
            visible="legendonly",  # Oculta inicialmente
        ),
        secondary_y=True,  # Eixo secundário
    )
    
    # Configuração do layout
    fig.update_layout(
        title=titulo_formatado,  # Título com datas formatadas
        xaxis_title="Data",
        yaxis_title="Preço (R$)",  # Eixo primário
        yaxis2_title="Volume",     # Eixo secundário
        legend=dict(
            orientation="h",  # Horizontal
            yanchor="bottom", 
            y=1.02  # Posição acima do gráfico
        ),
        template="plotly_white",  # Tema claro
        height=600  # Altura fixa para melhor responsividade
    )
    
    # Garante que o eixo de volume comece em zero
    fig.update_yaxes(rangemode="tozero", secondary_y=True)
    
    # Exibe gráfico usando toda largura disponível
    st.plotly_chart(fig, use_container_width=True)

# Rodapé com data de atualização formatada
atualizacao_formatada = formatar_data_ptbr(pd.Timestamp.now())
st.caption(f"Fonte: Banco de dados | Atualizado em {atualizacao_formatada}")



