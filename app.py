import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import random
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights + IA", layout="wide")

# --- INICIALIZACIÓN DEL CLIENTE GEMINI ---
# Intentamos conectar con la versión v1 (estable para planes gratuitos)
try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_KEY"],
        http_options={'api_version': 'v1'}
    )
    # Lista de modelos por orden de preferencia para el plan gratuito
    # Si el primero falla por cuota, podrías cambiar manualmente al segundo
    MODEL_ID = "gemini-1.5-flash" 
except Exception as e:
    st.error(f"⚠️ Error al configurar la API Key. Verifica los Secrets en Streamlit Cloud.")

st.title("📊 Automated Data Insights + ✨ IA")
st.markdown("Analítica descriptiva automática con soporte de Inteligencia Artificial (Plan Gratuito).")

# --- CARGADOR DE ARCHIVOS ---
uploaded_file = st.file_uploader("Sube tu archivo CSV o Excel", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carga inteligente
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ Datos cargados correctamente")

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa de los datos"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: INFORMACIÓN DE COLUMNAS ---
        st.subheader("🔍 Estructura de los Datos")
        info_data = []
        for col in df.columns:
            unique_vals = df[col].dropna().unique().tolist()
            num_unique = len(unique_vals)
            
            # Lógica solicitada: <5 mostrar todos, si no 5 aleatorios
            if num_unique <= 5:
                ejemplos = ", ".join(map(str, unique_vals))
            else:
                ejemplos = ", ".join(map(str, random.sample(unique_vals, 5))) + "..."

            info_data.append({
                "Columna": col,
                "Tipo": str(df[col].dtype),
                "Nulos": df[col].isnull().sum(),
                "Únicos": num_unique,
                "Valores de ejemplo": ejemplos
            })
        st.table(pd.DataFrame(info_data))

        # --- SECCIÓN 3: VISUALIZACIÓN E IA ---
        st.divider()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            col_main, col_sidebar = st.columns([2, 1])

            with col_sidebar:
                st.markdown("### ⚙️ Configuración")
                feat_x = st.selectbox("Eje X (Categorías/Tiempo)", all_cols)
                feat_y = st.selectbox("Eje Y (Valores numéricos)", numeric_cols)
                chart_type = st.radio("Tipo de gráfico", ["Barras", "Líneas", "Dispersión", "Boxplot"])
                
                st.markdown("---")
                ai_button = st.button("🪄 Obtener Insights con IA")

            with col_main:
                st.subheader("📈 Visualización Interactiva")
                if chart_type == "Barras":
                    fig = px.bar(df, x=feat_x, y=feat_y, template="plotly_dark", color_discrete_sequence=['#636EFA'])
                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, template="plotly_dark")
                else:
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                
                st.plotly_chart(fig, use_container_width=True)

            # --- LÓGICA DE INTELIGENCIA ARTIFICIAL ---
            if ai_button:
                with st.spinner("Consultando a Gemini..."):
                    # RESUMEN ULTRA-COMPRIMIDO para no exceder cuotas gratuitas
                    # Agrupamos por X para ver cómo se comporta Y
                    stats = df.groupby(feat_x)[feat_y].describe().head(5).to_string()
                    
                    prompt = f"""
                    Analiza como experto: Gráfico {chart_type} de {feat_y} por {feat_x}.
                    Datos estadísticos:
                    {stats}
                    
                    Dime en 3 frases muy cortas qué destaca y una recomendación.
                    """
                    
                    try:
                        # Llamada a la API
                        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                        st.info(f"### ✨ Análisis de la IA\n\n{response.text}")
                    except Exception as e:
                        if "429" in str(e):
                            st.warning("⚠️ El plan gratuito está saturado. Espera 15 segundos y pulsa el botón otra vez.")
                        else:
                            st.error(f"Hubo un problema con el modelo {MODEL_ID}: {e}")
        else:
            st.warning("⚠️ No se detectaron columnas numéricas para graficar.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("👋 Por favor, carga un archivo para empezar el análisis.")
