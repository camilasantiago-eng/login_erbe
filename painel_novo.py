import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime
import os

st.set_page_config(page_title="Report Mensal Erbe - Jurídico", layout="wide")

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def verificar_arquivo(nome):
    if not os.path.exists(nome):
        st.error(f"Arquivo não encontrado: {nome}")
        st.stop()

def tratar_data(col):
    if pd.api.types.is_numeric_dtype(col):
        return pd.to_datetime(col, unit="D", origin="1899-12-30", errors="coerce")
    return pd.to_datetime(col, errors="coerce", dayfirst=True)

def tratar_moeda(col):
    if pd.api.types.is_numeric_dtype(col):
        return pd.to_numeric(col, errors="coerce")

    return pd.to_numeric(
        col.astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip(),
        errors="coerce"
    )

def padronizar_colunas(df):
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df

def filtrar(df):
    if "data cálculo" not in df.columns:
        return df.copy()

    return df[
        (df["data cálculo"] >= pd.to_datetime(data_inicio)) &
        (df["data cálculo"] <= pd.to_datetime(data_fim))
    ].copy()

# ==========================================================
# HEADER
# ==========================================================

col_logo, col_titulo = st.columns([2,5])

with col_logo:
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        st.image(logo, width=450)

with col_titulo:
    st.title("Report Mensal Erbe - Jurídico")

st.divider()

# ==========================================================
# FILTRO
# ==========================================================

col1,col2 = st.columns(2)

with col1:
    data_inicio = st.date_input("Data início", value=datetime.date(2024,1,1))

with col2:
    data_fim = st.date_input("Data fim", value=datetime.date.today())

# ==========================================================
# CARREGAR BASES
# ==========================================================

@st.cache_data
def carregar_bases():

    verificar_arquivo("ENTRADAS.xlsx")
    verificar_arquivo("SETTLED.xlsx")
    verificar_arquivo("SETTLED_2.xlsx")
    verificar_arquivo("POS_BP.xlsx")
    verificar_arquivo("relatorio_tratado.xlsx")

    entradas = pd.read_excel("ENTRADAS.xlsx")
    settled = pd.read_excel("SETTLED.xlsx")
    settled_2 = pd.read_excel("SETTLED_2.xlsx")
    pos_bp = pd.read_excel("POS_BP.xlsx")
    relatorio = pd.read_excel("relatorio_tratado.xlsx")

    entradas = padronizar_colunas(entradas)
    settled = padronizar_colunas(settled)
    settled_2 = padronizar_colunas(settled_2)
    pos_bp = padronizar_colunas(pos_bp)
    relatorio = padronizar_colunas(relatorio)

    return entradas, settled, settled_2, pos_bp, relatorio

entradas, settled, settled_2, pos_bp, relatorio = carregar_bases()

# ==========================================================
# TRATAMENTO
# ==========================================================

for df in [entradas, settled, settled_2, pos_bp]:
    if "data cálculo" in df.columns:
        df["data cálculo"] = tratar_data(df["data cálculo"])

for df in [entradas, settled, settled_2, pos_bp]:
    if "pasta" in df.columns and "data cálculo" in df.columns:
        df.sort_values("data cálculo", inplace=True)
        df.drop_duplicates("pasta", keep="last", inplace=True)

if "pasta" in relatorio.columns:
    relatorio = relatorio.drop_duplicates("pasta")

# ==========================================================
# FILTROS
# ==========================================================

entradas_filtrado = filtrar(entradas)
settled_filtrado = filtrar(settled)
settled2_filtrado = filtrar(settled_2)

# ==========================================================
# MÉTRICAS
# ==========================================================

entradas_total = entradas_filtrado["pasta"].count()

baixa_prov = settled2_filtrado[
    settled2_filtrado["status"]
    .astype(str)
    .str.upper()
    .str.contains("BAIXA PROVIS", na=False)
]["pasta"].count()

encerrados = settled2_filtrado[
    settled2_filtrado["status"]
    .astype(str)
    .str.upper()
    .str.contains("ENCERR", na=False)
]["pasta"].count()

mes_atual = relatorio["pasta"].nunique()

col1,col2,col3,col4 = st.columns(4)

col1.metric("Entradas", entradas_total)
col2.metric("Baixa Provisória", baixa_prov)
col3.metric("Encerrados", encerrados)
col4.metric("Processos Atuais", mes_atual)

st.divider()

# ==========================================================
# GRÁFICO ENTRADAS
# ==========================================================

col_g1,col_g2 = st.columns(2)

with col_g1:
    st.subheader("Entradas do mês")

    if "macro assunto" in entradas_filtrado.columns:
        graf = entradas_filtrado.groupby("macro assunto")["pasta"].count().reset_index()

        if not graf.empty:
            fig = px.bar(graf, x="macro assunto", y="pasta", text="pasta")
            st.plotly_chart(fig,use_container_width=True)

# ==========================================================
# SAÍDAS
# ==========================================================

with col_g2:
    st.subheader("Saídas e Baixas")

    if {"status","macro encerramento"}.issubset(settled_filtrado.columns):

        saidas = settled_filtrado.groupby(
            ["status","macro encerramento"]
        )["pasta"].count().reset_index()

        fig = px.bar(
            saidas,
            x="status",
            y="pasta",
            color="macro encerramento",
            barmode="stack",
            text="pasta"
        )

        st.plotly_chart(fig,use_container_width=True)

st.divider()

# ==========================================================
# GRÁFICO MENSAL
# ==========================================================

st.subheader("Entradas x Saídas")

entradas_filtrado["mes"] = entradas_filtrado["data cálculo"].dt.month
settled_filtrado["mes"] = settled_filtrado["data cálculo"].dt.month

entradas_mes = entradas_filtrado.groupby("mes")["pasta"].count()
saidas_mes = settled_filtrado.groupby("mes")["pasta"].count()

meses = range(1,13)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=list(meses),
    y=[entradas_mes.get(m,0) for m in meses],
    mode="lines+markers",
    name="Entradas"
))

fig.add_trace(go.Scatter(
    x=list(meses),
    y=[saidas_mes.get(m,0) for m in meses],
    mode="lines+markers",
    name="Saídas"
))

st.plotly_chart(fig,use_container_width=True)

st.divider()

# ==========================================================
# TABELA FINANCEIRA
# ==========================================================

st.subheader("Baixa provisória e encerrados")

dados = []

settled_filtrado["macro encerramento"] = (
    settled_filtrado["macro encerramento"]
    .astype(str)
    .str.strip()
    .str.lower()
)

for status in ["won","settled","lost"]:

    df = settled_filtrado[
        settled_filtrado["macro encerramento"].str.contains(status, na=False)
    ]

    qtd = df["pasta"].count()
    bp = tratar_moeda(df["valor pedido objeto corrigido"]).sum()
    fcx = tratar_moeda(df["valor integral do acordo/condenação"]).sum()

    saving = (bp - fcx) / bp if bp > 0 else 0

    dados.append({
        "Status": status.title(),
        "Quantidade": qtd,
        "BP Atualizado": bp,
        "FCX Real": fcx,
        "Saving": saving
    })

df_tabela = pd.DataFrame(dados)

bp_total = df_tabela["BP Atualizado"].sum()
fcx_total = df_tabela["FCX Real"].sum()

total = {
    "Status": "Total",
    "Quantidade": df_tabela["Quantidade"].sum(),
    "BP Atualizado": bp_total,
    "FCX Real": fcx_total,
    "Saving": (bp_total - fcx_total) / bp_total if bp_total > 0 else 0
}

df_tabela = pd.concat([df_tabela, pd.DataFrame([total])])

df_tabela = df_tabela.reset_index(drop=True)

def format_moeda(v):
    return f"R$ {v/1000000:.2f}M"

df_tabela["BP Atualizado"] = df_tabela["BP Atualizado"].apply(format_moeda)
df_tabela["FCX Real"] = df_tabela["FCX Real"].apply(format_moeda)

df_tabela["Saving_raw"] = df_tabela["Saving"]
df_tabela["Saving"] = df_tabela["Saving"].apply(lambda v: f"{v*100:.1f}%")

def cor_saving(val):
    if val > 0:
        return "background-color: #d4edda"
    elif val < 0:
        return "background-color: #f8d7da"
    return ""

styled = df_tabela.style.applymap(cor_saving, subset=["Saving_raw"])

st.dataframe(styled, use_container_width=True)

# ==========================================================
# ASSUMPTIONS
# ==========================================================

st.divider()
st.subheader("Assumptions")

if os.path.exists("assumptions_26.xlsx"):

    assumptions = pd.read_excel("assumptions_26.xlsx")
    assumptions.columns = assumptions.columns.astype(str).str.strip().str.lower()

    for col in ["calculo","fixo","soma"]:
        if col in assumptions.columns:
            assumptions[col] = pd.to_numeric(assumptions[col], errors="coerce")
            assumptions[col] = assumptions[col].apply(
                lambda v: f"R$ {v/1000000:.2f}M" if pd.notnull(v) else ""
            )

    st.dataframe(assumptions,use_container_width=True)

else:
    st.info("Arquivo assumptions_26.xlsx não encontrado.")