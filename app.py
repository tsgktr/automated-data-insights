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
                
                # Reorganizamos y renombramos las columnas según tu petición
                # El orden original de describe().T es: count, mean, std, min, 25%, 50%, 75%, max
                columns_order = [
                    'count', 'mean', 'std', 'Varianza', 'min', 'max', '25%', '50%', '75%', 'Suma Total'
                ]
                desc_df = desc[columns_order]
                
                desc_df.columns = [
                    'Registros', 'Media', 'Desv. Estándar', 'Varianza', 'Mínimo', 'Máximo', 
                    '25% (Q1)', '50% (Mediana)', '75% (Q3)', 'Suma Total'
                ]
                
                # Mostrar tabla
                st.dataframe(desc_df.style.format("{:,.2f}"))

                # --- EXPLICACIONES DE LAS MÉTRICAS ---
                with st.expander("❓ ¿Qué significan estos números? (Guía rápida)"):
# --- GUÍA DE INTERPRETACIÓN DESARROLLADA ---
                st.markdown("### 📘 Guía de Interpretación y Casos Reales")
                
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    st.markdown("""
                    #### 1. Centralidad y Tendencia
                    * **Media:** Es el punto de equilibrio. Si la media de "Tiempo de Entrega" es 5 días, ese es tu estándar actual.
                    * **50% (Mediana):** El centro real. Si la media es 10 pero la mediana es 5, tienes unos pocos casos que tardan muchísimo y "ensucian" tu promedio.
                    
                    
                    #### 2. Dispersión (¿Qué tan fiable es el dato?)
                    * **Desv. Estándar:** Si vendes un producto a 100€ con desv. de 2€, tus precios son **consistentes**. Si la desv. es de 40€, tus precios son **caóticos**.
                    * **Varianza:** Nos dice cuánta "sorpresa" hay en los datos. A mayor varianza, más difícil es predecir el futuro.
                    
                    """)

                with col_exp2:
                    st.markdown("""
                    #### 3. Los Cuartiles en el Mundo Real
                    * **25% (Q1 - El umbral inferior):** * *Ejemplo:* "El 25% de mis clientes gasta menos de 15€". Son tus clientes de bajo ticket.
                    * **75% (Q3 - El umbral superior):** * *Ejemplo:* "El 75% de mis empleados gana menos de 2000€". El 25% restante son tus perfiles senior o directivos.
                    
                    
                    #### 4. Ejemplo de Diagnóstico Rápido
                    Si analizas **"Salarios"** y ves:
                    * **Mínimo:** 1.000€ / **Máximo:** 50.000€
                    * **Media:** 8.000€
                    * **Mediana (50%):** 2.500€
                    
                    **Insight:** La mayoría gana cerca de 2.500€, pero hay directivos ganando 50.000€ que hacen que la media parezca mucho más alta de lo que realmente es. ¡No te fíes de la media en este caso!
                    """)
            else:
                st.info("Selecciona al menos una variable en el buscador de arriba.")
        else:
            st.warning("No hay columnas numéricas en este archivo.")

        # --- SECCIÓN 4: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización e Interpretación")
        
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
                    exp = "**Interpretación:** Compara magnitudes entre categorías. El % indica el peso relativo de cada barra."

                elif chart_type == "Dispersión":
                    fig = px.scatter(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Analiza la relación entre dos variables numéricas."

                elif chart_type == "Líneas":
                    fig = px.line(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Ideal para observar tendencias y evolución temporal."

                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                    exp = "**Interpretación:** Muestra la distribución mediante cuartiles. Los puntos aislados son outliers."

                elif chart_type == "Violín":
                    fig = px.violin(df, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                    exp = "**Interpretación:** Muestra la densidad de los datos. Donde el violín es más ancho, hay más registros."

                elif chart_type == "Histograma":
                    fig = px.histogram(df, x=feat_y, template="plotly_dark", text_auto=True)
                    fig.update_layout(bargap=0.1)
                    fig.update_traces(textposition='outside')
                    exp = "**Interpretación:** Clasifica los datos en rangos para ver su frecuencia."

                else: # Histograma + Densidad
                    fig = px.histogram(df, x=feat_y, marginal="rug", histnorm='probability density', template="plotly_dark")
                    exp = "**Interpretación:** La curva suavizada permite ver la forma de la probabilidad de los datos."

                st.plotly_chart(fig, use_container_width=True)
                st.info(exp)

    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("👋 Sube un archivo CSV o Excel para comenzar.")

