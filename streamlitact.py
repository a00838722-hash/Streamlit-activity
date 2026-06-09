import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from streamlit_dynamic_filters import DynamicFilters
import plotly.express as px

#Mateo Cañamar Marrufo A00838722
#22/05/2026

df = pd.read_excel("sellers.xlsx")

df["FULL NAME"] = df["NAME"] + " " + df["LASTNAME"]

st.title("Sales Dashboard")

#Punto 1: En esta tabla de ventas, se muestra toda la información de los vendedores. Se puede filtrar por región para ver solo los datos correspondientes a esa región. 
st.subheader("Tabla de Ventas")

regions = df["REGION"].unique().tolist()
selected_region = st.selectbox("Filtrar por Región", options=["Todas"] + regions, key="region_select")

if selected_region == "Todas":
    df_filtered = df.copy()
else:
    df_filtered = df[df["REGION"] == selected_region]

st.dataframe(df_filtered, use_container_width=True)

#Punto 2: En esta sección se muestran tres gráficas de barras que resumen las ventas por cada región que hay. La primera gráfica muestra el total de unidades vendidas por región, la segunda gráfica muestra el total de ventas por región y la tercera gráfica muestra el promedio de ventas por unidad por región.
st.subheader("Gráficas de Ventas")

gcol1, gcol2, gcol3 = st.columns(3)

with gcol1:
    resumen_units = df.groupby("REGION")["SOLD UNITS"].sum().reset_index()
    fig1 = px.bar(resumen_units, x="REGION", y="SOLD UNITS", title="Units Sold",
                  color="REGION", text_auto=True)
    fig1.update_layout(showlegend=False, xaxis_tickangle=0)
    st.plotly_chart(fig1, use_container_width=True)

with gcol2:
    resumen_sales = df.groupby("REGION")["TOTAL SALES"].sum().reset_index()
    fig2 = px.bar(resumen_sales, x="REGION", y="TOTAL SALES", title="Total Sales",
                  color="REGION", text_auto=True)
    fig2.update_layout(showlegend=False, xaxis_tickangle=0)
    st.plotly_chart(fig2, use_container_width=True)

with gcol3:
    resumen_avg = df.groupby("REGION")["SALES AVERAGE"].mean().reset_index()
    fig3 = px.bar(resumen_avg, x="REGION", y="SALES AVERAGE", title="Sales Average",
                  color="REGION", text_auto=True)
    fig3.update_layout(showlegend=False, xaxis_tickangle=0, yaxis_range=[0, 1])
    st.plotly_chart(fig3, use_container_width=True)

    

# Punto 3: Es esta sección, se presentan dos espacios para escribir nombres de vendedores para comparar los numeros de uno contra los numerod el otro. Se comparan las unidades vendidas, el total de ventas, el promedio de ventas y las ventas promedio por unidad vendida. Además, se muestran gráficas de barras para cada una de estas métricas para comparar visualmente a los dos vendedores. Finalmente, se muestra la tabla con los datos de cada vendedor para revisar la información utilizada.
st.subheader("Datos por Vendedor")

icol1, icol2 = st.columns(2)

with icol1:
    nombre1 = st.text_input("Escribe el nombre del vendedor 1")

with icol2:
    nombre2 = st.text_input("Escribe el nombre del vendedor 2")

def get_vendor(nombre):
    if nombre:
        df_v = df[df["FULL NAME"].str.contains(nombre, case=False, na=False, regex=False)]
        return df_v if not df_v.empty else None
    return None

df_v1 = get_vendor(nombre1)
df_v2 = get_vendor(nombre2)

if nombre1 and df_v1 is None:
    st.warning(f"No se encontró: {nombre1}")
if nombre2 and df_v2 is None:
    st.warning(f"No se encontró: {nombre2}")

def mostrar_metricas(col, df_v, label):
    with col:
        st.markdown(f"**{label}**")
        vpu = df_v["TOTAL SALES"].sum() / df_v["SOLD UNITS"].sum()
        st.markdown(f"""
        | Métrica | Valor |
        |---|---|
        | Units Sold | {df_v['SOLD UNITS'].sum():,} |
        | Total Sales | ${df_v['TOTAL SALES'].sum():,.0f} |
        | Sales Average | {df_v['SALES AVERAGE'].mean():.4f} |
        | $ por Unidad | ${vpu:,.2f} |
        """)

if df_v1 is not None or df_v2 is not None:
    vcol1, vcol2 = st.columns(2)

    if df_v1 is not None:
        mostrar_metricas(vcol1, df_v1, df_v1["FULL NAME"].iloc[0])
    if df_v2 is not None:
        mostrar_metricas(vcol2, df_v2, df_v2["FULL NAME"].iloc[0])

    if df_v1 is not None and df_v2 is not None:
        nombre_v1 = df_v1["FULL NAME"].iloc[0]
        nombre_v2 = df_v2["FULL NAME"].iloc[0]

        df_comp = pd.DataFrame({
            "Vendedor": [nombre_v1, nombre_v2],
            "Units Sold": [df_v1["SOLD UNITS"].sum(), df_v2["SOLD UNITS"].sum()],
            "Total Sales": [df_v1["TOTAL SALES"].sum(), df_v2["TOTAL SALES"].sum()],
            "$ por Unidad": [
                df_v1["TOTAL SALES"].sum() / df_v1["SOLD UNITS"].sum(),
                df_v2["TOTAL SALES"].sum() / df_v2["SOLD UNITS"].sum()
            ],
            "Sales Average": [df_v1["SALES AVERAGE"].mean(), df_v2["SALES AVERAGE"].mean()]
        })

        bc1, bc2, bc3, bc4 = st.columns(4)

        def make_bar(df_comp, y, title):
            fig = px.bar(
                df_comp, x="Vendedor", y=y, title=title,
                color="Vendedor", text_auto=True,
                color_discrete_sequence=["#636EFA", "#EF553B"]
            )
            fig.update_layout(showlegend=False)
            return fig

        with bc1:
            st.plotly_chart(make_bar(df_comp, "Units Sold", "Units Sold"), use_container_width=True)
        with bc2:
            st.plotly_chart(make_bar(df_comp, "Total Sales", "Total Sales"), use_container_width=True)
        with bc3:
            st.plotly_chart(make_bar(df_comp, "$ por Unidad", "$ por Unidad"), use_container_width=True)
        with bc4:
            fig4 = make_bar(df_comp, "Sales Average", "Sales Average")
            fig4.update_layout(yaxis_range=[0, 1])
            st.plotly_chart(fig4, use_container_width=True)

    if df_v1 is not None:
        st.dataframe(df_v1, use_container_width=True)
    if df_v2 is not None:
        st.dataframe(df_v2, use_container_width=True)




















