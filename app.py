import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica descriptiva automática con interpretación guiada para toma de decisiones.")

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

        # --- SECCIÓN 3: DESCRIPTIVOS SELECCIONABLES ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            selected_vars = st.multiselect("Selecciona variables para analizar:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols)
            
            if selected_vars:
                # Calculamos estadísticas
                desc = df[selected_vars].describe().T
                desc['Suma Total'] = df[selected_vars].sum()
                desc['Varianza'] = df[selected_vars].var()
                
                # Reorganizamos las columnas: Media -> Desv -> Varianza -> Mín -> Máx -> Cuartiles
                columns_order = [
                    'mean', 'std', 'Varianza', 'min', 'max', '25%', '50%', '75%', 'count', 'Suma Total'
                ]
                desc_df = desc[columns_order]
                
                desc_df.columns = [
                    'Media', 'Desv. Estándar', 'Varianza', 'Mínimo', 'Máximo', 
                    '25% (Q1)', '50% (Mediana)', '75% (Q3)', 'Registros', 'Suma Total'
                ]
                
                # Mostrar tabla formateada
                st.dataframe(desc_df.style.format("{:,.2f}"))

                # --- GUÍA DE INTERPRETACIÓN DESARROLLADA CON EJEMPLOS ---
                st.markdown("### 📘 Guía de Interpretación y Casos Reales")
                
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    st.markdown("""
                    #### 1. Centralidad: ¿Dónde está el "foco"?
                    * **Media:** Es el promedio. Si la media de "Días de Cobro" es 30, ese es tu desempeño estándar.
                    * **50% (Mediana):** El centro real. Si tienes 10 facturas de 1€ y una de 1.000.000€, la *Media* será altísima, pero la *Mediana* te dirá que la mayoría de tus facturas son pequeñas.
                    
                    
                    #### 2. Dispersión: ¿Qué tan fiable es el dato?
                    * **Desv. Estándar:** Mide la estabilidad. 
                        * *Ejemplo:* Si fabricas piezas de 10cm con desv. de 0.01cm, tu proceso es **preciso**. Si la desv. es de 2cm, tu proceso es **caótico** y defectuoso.
                    * **Varianza:** Indica la cantidad de "sorpresas" o incertidumbre. A mayor varianza, más difícil es predecir resultados futuros.
                    
                    """)

                with col_exp2:
                    st.markdown("""
                    #### 3. Rango y Posicionamiento (Cuartiles)
                    * **Mínimo y Máximo:** Indican los límites. Sirven para detectar errores (ej. una edad de 200 años) o récords históricos.
                    * **25% (Q1 - Umbral Inferior):** *Ejemplo:* "El 25% de mis ventas son menores a 50€". Identifica tu segmento de bajo ticket.
                    * **75% (Q3 - Umbral Superior):** *Ejemplo:* "El 75% de mis envíos tardan menos de 3 días". El 25% restante son los que necesitan atención urgente por lentos.
                    
                    
                    #### 4. Ejemplo de Diagnóstico Rápido
                    Si analizas el **"Tiempo de Respuesta a Clientes"**:
                    - **Media:** 12 horas.
                    - **Mediana (50%):** 2 horas.
                    - **Máximo:** 120 horas.
                    
                    **Insight:** Tu equipo suele responder rápido (2h), pero hay algunos casos olvidados (120h) que están arruinando tu promedio y tu reputación. ¡Ataca los valores máximos!
                    """)
            else:
                st.info("Selecciona al menos una variable en el buscador de arriba.")
        else:
            st.warning("No hay columnas numéricas en este archivo.")

        # --- SECCIÓN 4: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización e Interpretación de Gráficos")
        
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
                    exp = "**Interpretación de Barras:** Compara el peso de cada categoría. El porcentaje (%) indica la relevancia sobre el total acumulado."

                elif chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación de Dispersión:** Busca nubes de puntos. Si hay una línea clara, una variable influye directamente en la otra."

                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación de Líneas:** Ideal para ver evolución. Los picos y valles muestran momentos de éxito o crisis."

                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación de Boxplot:** Visualiza la tabla de descriptivos. La caja es el 50% de tus datos. Los puntos fuera son tus excepciones."
                    

                elif chart_type == "Violín":
                    fig = px.violin(df, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                    exp = "**Interpretación de Violín:** Donde el violín es más ancho, hay más concentración de casos. Es la 'huella dactilar' de tus datos."

                elif chart_type == "Histograma":
                    fig = px.histogram(df, x=feat_y, template="plotly_dark", text_auto=True)
                    fig.update_layout(bargap=0.1)
                    fig.update_traces(textposition='outside')
                    exp = "**Interpretación de Histograma:** Muestra cuántos registros caen en cada rango. ¿Tienes una distribución equilibrada o concentrada en los extremos?"

                else: # Histograma + Densidad
                    fig = px.histogram(df, x=feat_y, marginal="rug", histnorm='probability density', template="plotly_dark")
                    exp = "**Interpretación de Densidad:** La curva suavizada elimina el ruido visual para mostrar la probabilidad real de que ocurra un valor."

                st.plotly_chart(fig, use_container_width=True)
                st.info(exp)

    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("👋 Sube un archivo CSV o Excel para comenzar el análisis profesional.")
