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

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa (Top 5)"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: INFORMACIÓN DE COLUMNAS ---
        st.subheader("🔍 Información Detallada de Columnas")
        info_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulos = df[col].isnull().sum()
            unf_values = df[col].nunique()
            all_unique = df[col].dropna().unique().tolist()
            if unf_values <= 5:
                ejemplos = ", ".join(map(str, all_unique))
            else:
                ejemplos = ", ".join(map(str, random.sample(all_unique, 5))) + "..."
            info_data.append({
                "Columna": col, "Tipo": dtype, "Nulos": nulos, 
                "Valores Únicos": unf_values, "Ejemplos": ejemplos
            })
        st.table(pd.DataFrame(info_data))

        # --- SECCIÓN 3: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización y Guía de Interpretación")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            col_viz1, col_viz2 = st.columns([1, 2])
            with col_viz1:
                st.markdown("### ⚙️ Configuración")
                feat_x = st.selectbox("Eje X (Categorías/Tiempo)", all_cols)
                feat_y = st.selectbox("Eje Y (Numérico)", numeric_cols)
                
                chart_type = st.radio(
                    "Tipo de gráfico", 
                    ["Dispersión", "Líneas", "Barras", "Boxplot", "Violín", "Histograma", "Histograma + Densidad"]
                )

            with col_viz2:
                # Lógica de Gráficos
                if chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, color_discrete_sequence=['#636EFA'])
                    exp = """
                    **¿Cómo interpretar la Dispersión?**
                    * **Relación:** Busca si los puntos forman una línea (correlación). Si suben juntos, es positiva.
                    * **Outliers:** Fíjate en los puntos muy alejados; pueden ser errores o casos excepcionales.
                    * **Clusters:** ¿Se forman grupos de puntos? Podrían indicar segmentos de datos distintos.
                    """
                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y)
                    exp = """
                    **¿Cómo interpretar las Líneas?**
                    * **Tendencia:** ¿Los valores suben o bajan con el tiempo o la secuencia?
                    * **Estacionalidad:** Busca patrones que se repiten (picos y valles regulares).
                    * **Volatilidad:** Cambios bruscos de dirección indican inestabilidad en los datos.
                    """
                elif chart_type == "Barras":
                    fig = px.bar(df, x=feat_x, y=feat_y)
                    exp = """
                    **¿Cómo interpretar las Barras?**
                    * **Comparación:** Es ideal para ver quién tiene el valor más alto o bajo por categoría.
                    * **Brechas:** Fíjate en la diferencia de altura entre barras adyacentes.
                    """
                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y)
                    exp = """
                    **¿Cómo interpretar el Boxplot (Caja y Bigotes)?**
                    * **La Caja:** Representa el 50% de los datos. La línea central es la **Mediana**.
                    * **Bigotes:** Indican el rango de los datos. Lo que está fuera son **Outliers** (puntos atípicos).
                    * **Simetría:** Si la mediana no está en el centro de la caja, los datos están sesgados.
                    """
                elif chart_type == "Violín":
                    fig = px.violin(df, x=feat_x, y=feat_y, box=True, points="all")
                    exp = """
                    **¿Cómo interpretar el Gráfico de Violín?**
                    * **Ancho del Violín:** Indica dónde hay más concentración de datos (densidad).
                    * **Forma:** Un violín "gordo" abajo indica que la mayoría de valores son bajos.
                    * **Combinación:** Incluye un boxplot interno para ver la mediana y cuartiles al mismo tiempo.
                    """
                elif chart_type == "Histograma":
                    fig = px.histogram(df, x=feat_y)
                    exp = """
                    **¿Cómo interpretar el Histograma?**
                    * **Distribución:** Mira si tiene forma de campana (Normal) o si está inclinado a un lado.
                    * **Moda:** El pico más alto indica el rango de valores más frecuente.
                    * **Huecos:** Espacios vacíos indican rangos donde no existen datos.
                    """
                else: # Histograma + Densidad
                    fig = px.histogram(df, x=feat_y, marginal="rug", histnorm='probability density')
                    exp = """
                    **¿Cómo interpretar el Histograma con Densidad?**
                    * **Probabilidad:** El eje Y muestra la probabilidad, lo que permite comparar distribuciones de diferentes tamaños.
                    * **La curva (Rug):** Las líneas pequeñas en la base indican cada registro individual, ayudando a ver la densidad exacta.
                    * **Suavizado:** Ayuda a ignorar el "ruido" de las barras para ver la forma real de los datos.
                    """
                
                # Mostrar gráfico y su explicación
                st.plotly_chart(fig, use_container_width=True)
                st.info(exp)
    
    except Exception as e:
        st.error(f"Error: {e}")
