import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CORES
# =========================
COLORS = {
    "blue_dark": "#0B3C5D",
    "blue_light": "#BFD7EA",
    "blue_medium": "#328CC1",
    "gray": "#A9A9A9",
    "green": "#5CB85C",
    "red": "#D9534F",
    "magenta": "#C2185B"
}

labels_macro = ["FAR", "Civil", "Property Tax", "Labor", "Tax"]

pagina = st.sidebar.radio("Navegação", [
    "Overview",
    "Claims por Ano",
    "New Claims",
    "Resolved"
])

# =========================
# FUNÇÃO DONUT 
# =========================
def donut(values, title, total):
    fig = go.Figure(data=[go.Pie(
        labels=labels_macro,
        values=values,
        hole=0.7,
        marker_colors=[
            COLORS["blue_dark"],
            COLORS["blue_medium"],
            COLORS["magenta"],
            COLORS["gray"],
            COLORS["blue_light"]
        ],
        textinfo='percent',
        texttemplate='%{percent:.2%}'
    )])
    fig.update_layout(
        title=dict(text=title, x=0.5),
        annotations=[dict(text=f"<b>{total}</b>", x=0.5, y=0.5, showarrow=False)],
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        plot_bgcolor="white"
    )
    return fig

# =========================
# FUNÇÃO LABEL INTELIGENTE
# =========================
def add_labels(fig, x_vals, y_vals, color):
    texts = []
    for i in range(len(y_vals)):
        if y_vals[i] >= 11:
            texts.append(str(y_vals[i]))
        else:
            texts.append("")
            if y_vals[i] > 0:
                fig.add_annotation(
                    x=x_vals[i],
                    y=y_vals[i],
                    text=str(y_vals[i]),
                    showarrow=False,
                    xshift=-25,
                    font=dict(color=color, size=11)
                )
    return texts

# =========================
# PAGE 1 — OVERVIEW
# =========================
if pagina == "Overview":

    st.title("Erbe Update")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(donut([220,310,140,90,70], "Total Claims", 830), use_container_width=True)

    with col2:
        st.plotly_chart(donut([120,210,90,50,35], "Expected Loss", 505), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    values = [553,-48,35,22,562,40,602]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Sep25","Resolved","Savings","Revised","Subtotal","New","Total"],
        y=values,
        marker_color=[
            COLORS["gray"], COLORS["red"], COLORS["green"],
            COLORS["blue_medium"], COLORS["gray"],
            COLORS["magenta"], COLORS["blue_dark"]
        ],
        text=values,
        textposition="outside"
    ))

    fig.update_layout(plot_bgcolor="white", height=350)
    st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns([2,1])

    with col3:
        vals = [500,611,111]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=["Total","Updated","Carrying"],
            y=vals,
            marker_color=[COLORS["gray"], COLORS["blue_medium"], COLORS["green"]],
            text=vals,
            textposition="outside"
        ))
        fig2.update_layout(plot_bgcolor="white", height=300)
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        st.table(pd.DataFrame({
            "Subject":["Civil","Tax","Labor","Construction"],
            "Rate":["TJ+1%","Selic","TST+1%","INCC"],
            "12M":["16.8%","14.5%","16.8%","5.8%"]
        }))

# (RESTO DO CÓDIGO — 100% INTACTO)
# =========================
# =========================
# PAGE 2 — CLAIMS
# =========================
elif pagina == "Claims por Ano":

    st.title("New Claims Filled per Year")

    anos = ["≤2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026"]

    ativos = [80,34,90,160,260,200,630,260,640,1700,520,330,300,450,49]
    encerrados = [7900,5900,7500,7900,7300,4800,2700,1800,1000,2400,600,480,230,70,0]

    st.table(pd.DataFrame({
        "Métrica":["Total Risk","Expected Loss"],
        "≤2012":[144,33],"2013":[47,7],"2014":[24,16],"2015":[87,31],
        "2016":[199,69],"2017":[194,65],"2018":[190,94],"2019":[87,40],
        "2020":[226,93],"2021":[191,59],"2022":[211,20],"2023":[136,50],
        "2024":[46,18],"2025":[55,28],"2026":[12,5]
    }))

    fig = go.Figure()

    text_resolved = add_labels(fig, anos, encerrados, COLORS["blue_light"])
    text_active = add_labels(fig, anos, ativos, COLORS["blue_dark"])

    fig.add_trace(go.Bar(
        x=anos, y=encerrados,
        name="Resolved",
        marker_color=COLORS["blue_light"],
        text=text_resolved,
        textposition="inside"
    ))

    fig.add_trace(go.Bar(
        x=anos, y=ativos,
        name="Active",
        marker_color=COLORS["blue_dark"],
        text=text_active,
        textposition="inside"
    ))

    totals = [a+b for a,b in zip(ativos,encerrados)]

    for i in range(len(anos)):
        fig.add_annotation(x=anos[i], y=totals[i]*1.05, text=str(totals[i]), showarrow=False)

    fig.update_layout(barmode="stack", plot_bgcolor="white", height=450)

    st.plotly_chart(fig, use_container_width=True)

# =========================
# PAGE 3 — NEW CLAIMS
# =========================
elif pagina == "New Claims":

    st.title("New Claims")

    values = [72.6,9.2,10.3]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Budget","Forecast","Actual"],
        y=values,
        marker_color=[COLORS["magenta"], COLORS["blue_medium"], COLORS["blue_light"]],
        text=values,
        textposition="outside"
    ))

    perc = (values[2]/values[1] - 1)*100

    fig.add_annotation(
    x=1,
    y=max(values)*0.8,
    text=f"{perc:.2f}%",
    showarrow=True
    )

    st.plotly_chart(fig, use_container_width=True)

    tipos = ["Civil","Property Tax","Labor","Delay","FAR","Construction","Tax","Total"]

    st.table(pd.DataFrame({
        "Tipo": tipos,
        "Total Risk":[82,137,3,6,4,5,4,241],
        "Expected Loss":[30,50,1,2,1,2,1,87]
    }))

    valores = [40,60,5,8,6,4,3,126]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=tipos,
        y=valores,
        marker_color=COLORS["blue_dark"],
        text=valores,
        textposition="outside"
    ))

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# PAGE 4 — RESOLVED
# =========================
elif pagina == "Resolved":

    st.title("Finally Resolved Claims")

    tipos = ["Civil","Property Tax","Labor","Delay","FAR","Construction","Tax"]

    df = pd.DataFrame({
        "Métrica": ["Total Risk","Expected Loss","Disbursement"],
        "Civil":[68,30,19],
        "Property Tax":[0.5,0.2,0],
        "Labor":[2.7,1.1,0.1],
        "Delay":[37.8,14.7,12],
        "FAR":[3.4,1.1,0.2],
        "Construction":[9.2,0.9,1],
        "Tax":[0,0,0]
    })

    st.table(df)

    settlement = [37,0,3,39,4,11,0]
    lost = [40,0,8,26,20,3,2]
    won = [27,16,8,6,25,4,0]

    fig = go.Figure()

    fig.add_trace(go.Bar(x=tipos, y=settlement, marker_color=COLORS["red"]))
    fig.add_trace(go.Bar(x=tipos, y=lost, marker_color=COLORS["blue_dark"]))
    fig.add_trace(go.Bar(x=tipos, y=won, marker_color=COLORS["blue_light"]))

    totals = [s+l+w for s,l,w in zip(settlement,lost,won)]

    for i in range(len(tipos)):
        fig.add_annotation(x=tipos[i], y=totals[i]*1.08, text=str(totals[i]), showarrow=False)

    fig.update_layout(barmode="stack", plot_bgcolor="white", height=450)

    st.plotly_chart(fig, use_container_width=True)