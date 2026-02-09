import streamlit as st
import pandas as pd
import plotly.express as px
import random

# Configuración de la página
st.set_page_config(page_title="Automated Data Insights", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica descriptiva automática para tus ficheros de datos.")

uploaded_file = st.file_uploader("Elige un fichero", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("¡Archivo cargado con éxito!")

        # --- SECCIÓN 1: VISTA PREVIA (Solo 5 registros) ---
        st.subheader("👀 Vista previa de los datos (Top 5)")
        st.dataframe(df.head(5))

        # --- SECCIÓN 2: INFORMACIÓN DE COLUMNAS MEJORADA ---
        st.subheader("🔍 Información Detallada de Columnas")
        
        info_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulos = df[col].isnull().sum()
            unf_values = df[col].nunique()
            
            # Lógica de valores de ejemplo
            all_unique = df[col].dropna().unique().tolist()
            if unf_values <= 5:
                ejemplos = ", ".join(map(str, all_unique))
            else:
                ejemplos = ", ".join(map(str, random.sample(all_unique, 5))) + "..."

            info_data.append({
                "Columna": col,
                "Tipo": dtype,
                "Nulos": nulos,
                "Valores Únicos": unf_values,
                "Ejemplos / Valores": ejemplos
            })
        
        st.table(pd.DataFrame(info_data))

        # --- SECCIÓN 3: RESUMEN ESTADÍSTICO ---
        st.subheader("📋 Resumen Estadístico")
        st.write(df.describe())

        # --- SECCIÓN 4: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización de Datos")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            col_viz1, col_viz2 = st.columns([1, 2])
            with col_viz1:
                feat_x = st.selectbox("Eje X", all_cols)
                feat_y = st.selectbox("Eje Y (Numérico)", numeric_cols)
                chart_type = st.radio("Tipo de gráfico", ["Dispersión", "Líneas", "Barras", "Boxplot"])

            with col_viz2:
                if chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y)
                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y)
                elif chart_type == "Boxplot":
                    fig = px.box(df, y=feat_y, x=feat_x)
                else:
                    fig = px.bar(df, x=feat_x, y=feat_y)
                
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error: {e}")
