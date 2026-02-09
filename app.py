import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import random

# --- CONFIGURACIÓN DE GEMINI (Segura a través de Secrets) ---
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ No se encontró la GEMINI_KEY en los Secrets o hay un error de configuración.")

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights + IA", layout="wide")

st.title("📊 Automated Data Insights + ✨ IA")
st.markdown("Analítica descriptiva automática potenciada por Inteligencia Artificial.")

# --- CARGADOR DE ARCHIVOS ---
uploaded_file = st.file_uploader("Elige un fichero (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Lectura de datos
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("¡Archivo cargado con éxito!")

        # --- SECCIÓN 1: VISTA PREVIA (Solo 5 registros) ---
        st.subheader("👀 Vista previa de los datos (Top 5)")
        st.dataframe(df.head(5))

        # --- SECCIÓN 2: INFORMACIÓN DE COLUMNAS (Lógica de valores únicos) ---
        st.subheader("🔍 Información de Columnas")
        
        info_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulos = df[col].isnull().sum()
            unique_values = df[col].dropna().unique().tolist()
            num_unique = len(unique_values)
            
            # Lógica: si son < 5 mostramos todos, si no, 5 aleatorios
            if num_unique <= 5:
                ejemplos = ", ".join(map(str, unique_values))
            else:
                ejemplos = ", ".join(map(str, random.sample(unique_values, 5))) + "..."

            info_data.append({
                "Columna": col,
                "Tipo": dtype,
                "Nulos": nulos,
                "Valores Únicos": num_unique,
                "Ejemplos / Valores": ejemplos
            })
        
        st.table(pd.DataFrame(info_data))

        # --- SECCIÓN 3: VISUALIZACIÓN E INSIGHTS CON IA ---
        st.divider()
        st.subheader("📈 Análisis Visual e Inteligencia Artificial")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            # Diseño de dos columnas: Gráfico a la izquierda, IA a la derecha
            col_viz, col_ai = st.columns([2, 1])

            with col_viz:
                st.markdown("### Configuración")
                c1, c2 = st.columns(2)
                with c1:
                    feat_x = st.selectbox("Selecciona Eje X", all_cols)
                with c2:
                    feat_y = st.selectbox("Selecciona Eje Y (Numérico)", numeric_cols)
                
                chart_type = st.segmented_control(
                    "Tipo de gráfico", 
                    options=["Dispersión", "Líneas", "Barras", "Boxplot"],
                    default="Dispersión"
                )

                # Renderizado del gráfico
                if chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y, template="plotly_dark")
                else:
                    fig = px.bar(df, x=feat_x, y=feat_y, template="plotly_dark")
                
                st.plotly_chart(fig, use_container_width=True)

            with col_ai:
                st.markdown("### ✨ Insights de Gemini")
                if st.button("🪄 Analizar tendencia con IA"):
                    with st.spinner("Gemini está analizando los datos..."):
                        # Creamos un resumen estadístico rápido para enviárselo a la IA
                        stats_summary = df.groupby(feat_x)[feat_y].describe().head(10).to_string()
                        
                        prompt = f"""
                        Eres un experto científico de datos. Analiza la relación entre '{feat_x}' (Eje X) y '{feat_y}' (Eje Y).
                        Basado en este resumen estadístico:
                        {stats_summary}
                        
                        Dime 3 observaciones clave del gráfico y una recomendación estratégica. 
                        Sé breve, profesional y usa puntos de lista.
                        """
                        
                        try:
                            response = model.generate_content(prompt)
                            st.info(response.text)
                        except Exception as e:
                            st.error(f"Error al conectar con Gemini: {e}")
        else:
            st.warning("Se necesita al menos una columna numérica para realizar el análisis visual.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("👋 ¡Bienvenido! Por favor, sube un archivo CSV o Excel para comenzar el análisis.")

