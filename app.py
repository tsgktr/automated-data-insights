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
        st.subheader("🔍 Estructura de las Columnas")
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
                "Únicos": unf_values, "Ejemplos": ejemplos
            })
        st.table(pd.DataFrame(info_data))

        # --- NUEVA SECCIÓN: DESCRIPTIVOS SELECCIONABLES ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado")
        st.markdown("Selecciona las variables numéricas que deseas analizar a fondo.")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            selected_vars = st.multiselect("Selecciona variables:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols)
            
            if selected_vars:
                # Calculamos descriptivos y transponemos para mejor lectura
                desc_df = df[selected_vars].describe().T
                # Añadimos métricas extra
                desc_df['Suma Total'] = df[selected_vars].sum()
                desc_df['Varianza'] = df[selected_vars].var()
                
                # Renombrar columnas para claridad
                desc_df.columns = ['Registros', 'Media', 'Desv. Estándar', 'Mín', '25%', '50% (Mediana)', '75%', 'Máx', 'Suma Total', 'Varianza']
                
                st.dataframe(desc_df.style.format("{:,.2f}").background_gradient(cmap='Blues'))
                
                
            else:
                st.info("Selecciona al menos una variable para ver sus descriptivos.")
        else:
            st.warning("No se encontraron variables numéricas para realizar cálculos estadísticos.")

        # --- SECCIÓN 4: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización e Interpretation")
        
        all_cols = df.columns.tolist()

        if numeric_cols:
            col_viz1, col_viz2 = st.columns([1, 2])
            
            with col_viz1:
                st.markdown("### ⚙️ Configuración")
                feat_x = st.selectbox("Eje X (Categorías/Tiempo)", all_cols)
                feat_y = st.selectbox("Eje Y (Valores Numéricos)", numeric_cols)
                
                chart_type = st.radio(
                    "Tipo de gráfico", 
                    ["Barras", "Dispersión", "Líneas", "Boxplot", "Violín", "Histograma", "Histograma + Densidad"]
                )

            with col_viz2:
                if chart_type == "Barras":
                    df_counts = df.groupby(feat_x)[feat_y].sum().reset_index()
                    total_sum = df_counts[feat_y].sum()
                    df_counts['label'] = df_counts[feat_y].apply(lambda x: f"{x:,.0f}<br>({(x/total_sum)*100:.1f}%)" if total_sum != 0 else "0")
                    fig = px.bar(df_counts, x=feat_x, y=feat_y, text='label', template="plotly_dark")
                    max_y = df_counts[feat_y].max()
                    fig.update_yaxes(range=[0, max_y * 1.2]) 
                    fig.update_traces(textposition='outside')
                    exp = "**Interpretación:** El porcentaje muestra el peso de cada categoría sobre el total sumado."

                elif chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Busca patrones lineales o nubes de puntos para entender la correlación."

                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Ideal para ver la evolución de una métrica."

                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** La caja muestra el rango intercuartílico; los puntos externos son valores atípicos."

                elif chart_type == "Violín":
                    fig = px.violin(df, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                    exp = "**Interpretación:** Combina boxplot con densidad para ver dónde se agrupan más los datos."

                elif chart_type == "Histograma":
                    fig = px.histogram(df, x=feat_y, template="plotly_dark", text_auto=True)
                    fig.update_layout(bargap=0.1)
                    fig.update_traces(textposition='outside')
                    exp = "**Interpretación:** Muestra la forma de la distribución de una sola variable."

                else: # Histograma + Densidad
                    fig = px.histogram(df, x=feat_y, marginal="rug", histnorm='probability density', template="plotly_dark")
                    exp = "**Interpretación:** La curva suavizada representa la probabilidad de encontrar un valor en ese rango."

                st.plotly_chart(fig, use_container_width=True)
                st.info(exp)

    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("👋 Sube un archivo CSV o Excel para comenzar.")
