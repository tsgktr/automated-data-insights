import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Automated Data Insights", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Carga tu archivo (CSV o Excel) para obtener analíticas automáticas.")

# 1. Cargador de archivos
uploaded_file = st.file_uploader("Elige un fichero", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Leer el archivo según la extensión
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("¡Archivo cargado con éxito!")

        # --- SECCIÓN 1: VISTA PREVIA ---
        st.subheader("👀 Vista previa de los datos")
        st.dataframe(df.head(10))

        # --- SECCIÓN 2: ANALÍTICA BÁSICA ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Resumen Estadístico")
            st.write(df.describe())

        with col2:
            st.subheader("🔍 Información de Columnas")
            info_df = pd.DataFrame({
                "Tipo": df.dtypes.astype(str),
                "Nulos": df.isnull().sum()
            })
            st.table(info_df)

        # --- SECCIÓN 3: VISUALIZACIÓN INTERACTIVA ---
        st.divider()
        st.subheader("📈 Visualización de Datos")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            col_viz1, col_viz2 = st.columns(2)

            with col_viz1:
                feat_x = st.selectbox("Selecciona eje X", all_cols)
                feat_y = st.selectbox("Selecciona eje Y (Numérico)", numeric_cols)
                chart_type = st.radio("Tipo de gráfico", ["Dispersión", "Líneas", "Barras"])

            with col_viz2:
                if chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, color_discrete_sequence=['#00CC96'])
                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y)
                else:
                    fig = px.bar(df, x=feat_x, y=feat_y)
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No se encontraron columnas numéricas para graficar.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Esperando a que subas un archivo...")