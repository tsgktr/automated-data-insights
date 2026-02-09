import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica descriptiva automática con visualización optimizada.")

uploaded_file = st.file_uploader("Elige un fichero (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Carga de datos
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("¡Archivo cargado con éxito!")

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa de los datos (Top 5)"):
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
                "Columna": col,
                "Tipo": dtype,
                "Nulos": nulos,
                "Valores Únicos": unf_values,
                "Ejemplos / Valores": ejemplos
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
                feat_y = st.selectbox("Eje Y (Valores Numéricos)", numeric_cols)
                
                chart_type = st.radio(
                    "Selecciona el tipo de gráfico", 
                    ["Barras", "Dispersión", "Líneas", "Boxplot", "Violín", "Histograma", "Histograma + Densidad"]
                )

            with col_viz2:
                # --- LÓGICA DE GRÁFICOS ---
                
                if chart_type == "Barras":
                    # Agrupamos para calcular totales y porcentajes
                    df_counts = df.groupby(feat_x)[feat_y].sum().reset_index()
                    total_sum = df_counts[feat_y].sum()
                    
                    # Etiqueta: Valor formateado + (Porcentaje%)
                    df_counts['label'] = df_counts[feat_y].apply(
                        lambda x: f"{x:,.0f}<br>({(x/total_sum)*100:.1f}%)" if total_sum != 0 else "0"
                    )

                    fig = px.bar(df_counts, x=feat_x, y=feat_y, text='label', template="plotly_dark")
                    
                    # AJUSTE DEL EJE Y: Aumentamos un 20% el rango superior para que las etiquetas no se corten
                    max_y = df_counts[feat_y].max()
                    fig.update_yaxes(range=[0, max_y * 1.2]) 
                    fig.update_traces(textposition='outside')
                    
                    exp = """
                    **¿Cómo interpretar las Barras?**
                    * **Total y Porcentaje:** El número arriba indica el valor exacto, mientras que el % muestra el peso de cada barra sobre el total.
                    * **Comparación:** Es la mejor herramienta para ver diferencias de magnitud entre categorías.
                    """

                elif chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Busca patrones de correlación. Si los puntos forman una línea ascendente, las variables crecen juntas."

                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Ideal para series temporales. Observa si hay una tendencia clara al alza o a la baja."

                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** La línea central es la mediana. Los puntos fuera de los bigotes son valores atípicos (outliers)."

                elif chart_type == "Violín":
                    fig = px.violin(df, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                    exp = "**Interpretación:** El ancho indica dónde hay más datos. Es un híbrido entre un Boxplot y un Histograma."

                elif chart_type == "Histograma":
                    fig = px.histogram(df, x=feat_y, template="plotly_dark", text_auto=True)
                    # Ajuste de eje Y para histogramas con etiquetas automáticas
                    fig.update_layout(bargap=0.1)
                    fig.update_traces(textposition='outside')
                    exp = "**Interpretación:** Muestra la frecuencia de los datos. Ayuda a identificar si la mayoría de los valores son bajos, medios o altos."

                else: # Histograma + Densidad
                    fig = px.histogram(df, x=feat_y, marginal="rug", histnorm='probability density', template="plotly_dark")
                    exp = "**Interpretación:** La curva suavizada muestra la 'silueta' de tus datos, facilitando ver la probabilidad de ocurrencia."

                # Renderizado del gráfico
                st.plotly_chart(fig, use_container_width=True)
                st.info(exp)

    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("👋 Sube un archivo CSV o Excel para comenzar el análisis automático.")
