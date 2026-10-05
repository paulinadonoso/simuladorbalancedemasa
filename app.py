import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Simulador Balance de Masa - Bredenmaster",
    page_icon="🍞",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""

""", unsafe_allow_html=True)

st.title("🍞 Simulador de Balance de Masa y Gestión de Recortes")
st.caption("Planta Bredenmaster | Ingeniería de Procesos y Control de Mermas")

# ---------------------------------------------------------
# BARRA LATERAL: INPUTS DEL SIMULADOR
# ---------------------------------------------------------
st.sidebar.header("⚙️ Parámetros del Lote")

producto = st.sidebar.selectbox(
    "Producto / Receta",
    ["Marraqueta Grande (Cod. 90302267)", "Hallulla Especial 100g", "Empanada Pino Horno", "Dona Glaseada Bollería"]
)

col1_sb, col2_sb = st.sidebar.columns(2)
cant_batches = col1_sb.number_input("Cantidad Batches", min_value=1, max_value=1000, value=150)
peso_batch_kg = col2_sb.number_input("Peso Batch (kg)", min_value=1.0, value=214.105, step=1.0)

st.sidebar.subheader("🔄 Gestión de Recorte")
recorte_solicitado = st.sidebar.number_input("Recorte Solicitado (kg)", min_value=0.0, value=350.0, step=10.0)

st.sidebar.subheader("⚠️ Mermas Reales Registradas")
merma_horno_real = st.sidebar.number_input("Merma Horno (kg)", min_value=0.0, value=430.0)
merma_envasado_real = st.sidebar.number_input("Merma Envasado (kg)", min_value=0.0, value=1230.0)

st.sidebar.subheader("📐 Parámetros de Diseño (Teórico)")
pct_humedad_diseno = st.sidebar.slider("% Pérdida Humedad", 1.0, 15.0, 6.0) / 100.0
pct_recorte_diseno = st.sidebar.slider("% Generación Recorte", 0.0, 10.0, 2.0) / 100.0
pct_merma_diseno = st.sidebar.slider("% Merma Permitida", 0.1, 5.0, 1.5) / 100.0

# ---------------------------------------------------------
# MOTOR DE CÁLCULO
# ---------------------------------------------------------
total_batch_real = cant_batches * peso_batch_kg
total_entradas_real = total_batch_real + recorte_solicitado

perdida_humedad_real = total_entradas_real * pct_humedad_diseno
merma_total_real = merma_horno_real + merma_envasado_real
total_envasado_real = total_entradas_real - (perdida_humedad_real + merma_total_real)
rendimiento_real = (total_envasado_real / total_entradas_real) * 100 if total_entradas_real > 0 else 0

# Balance Diseño
total_entradas_diseno = total_batch_real
perdida_humedad_diseno = total_entradas_diseno * pct_humedad_diseno
recorte_generado_diseno = total_entradas_diseno * pct_recorte_diseno
merma_diseno = total_entradas_diseno * pct_merma_diseno
total_envasado_diseno = total_entradas_diseno - (perdida_humedad_diseno + recorte_generado_diseno + merma_diseno)
rendimiento_diseno = (total_envasado_diseno / total_entradas_diseno) * 100 if total_entradas_diseno > 0 else 0

exceso_mermas = merma_total_real - merma_diseno

# ---------------------------------------------------------
# DESPLIEGUE DE MÉTRICAS PRINCIPALES
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Entradas Reales", f"{total_entradas_real:,.2f} kg", f"Batch: {total_batch_real:,.2f} kg")
m2.metric("Envasado Proyectado", f"{total_envasado_real:,.2f} kg", f"Diseño: {total_envasado_diseno:,.2f} kg")
m3.metric("Mermas Reales", f"{merma_total_real:,.2f} kg", f"{exceso_mermas:+,.2f} kg Exceso", delta_color="inverse")
m4.metric("Rendimiento Real", f"{rendimiento_real:.2f}%", f"Diseño: {rendimiento_diseno:.2f}%")

st.divider()

# ---------------------------------------------------------
# GRÁFICOS Y ANÁLISIS VISUAL
# ---------------------------------------------------------
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📊 Comparativo Balance: Real vs. Diseño")
    df_chart = pd.DataFrame({
        "Componente": ["Envasado", "Pérdida Humedad", "Mermas", "Recorte Gen."],
        "Proceso Real (kg)": [total_envasado_real, perdida_humedad_real, merma_total_real, 0],
        "Por Diseño (kg)": [total_envasado_diseno, perdida_humedad_diseno, merma_diseno, recorte_generado_diseno]
    })
    fig_bar = px.bar(df_chart, x="Componente", y=["Proceso Real (kg)", "Por Diseño (kg)"], barmode="group",
                     color_discrete_sequence=["#D32F2F", "#1E293B"])
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.subheader("🍕 Distribución Salidas Reales")
    fig_pie = px.pie(
        names=["Envasado Proyectado", "Pérdida Humedad", "Merma Horno", "Merma Envasado"],
        values=[total_envasado_real, perdida_humedad_real, merma_horno_real, merma_envasado_real],
        color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------------------------------------
# TABLA DE INVENTARIO Y REPORTE
# ---------------------------------------------------------
st.subheader("📦 Estado de Inventario de Recortes (Lote FEFO)")
df_inv = pd.DataFrame([
    {"Lote": "26061", "Código": 90302267, "Masa": "Marraqueta", "Vencimiento": "2026-03-05", "Inicial (kg)": 350, "Consumido (kg)": min(350, recorte_solicitado), "Saldo (kg)": max(0, 350 - recorte_solicitado)},
    {"Lote": "26062", "Código": 90302267, "Masa": "Marraqueta", "Vencimiento": "2026-03-06", "Inicial (kg)": 500, "Consumido (kg)": max(0, min(500, recorte_solicitado - 350)), "Saldo (kg)": max(0, 500 - max(0, recorte_solicitado - 350))}
])
st.dataframe(df_inv, use_container_width=True)
