import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica con Segmentación Temporal Inteligente.")

uploaded_file = st.file_uploader("Elige un fichero (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 1. CARGA DE DATOS
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # 2. DETECCIÓN Y CONVERSIÓN DE FECHAS
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    continue

        # 3. SEGMENTACIÓN TEMPORAL (Sidebar)
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if date_cols:
            st.sidebar.header("📅 Filtros y Segmentación")
            main_date_col = st.sidebar.selectbox("Columna de tiempo maestra:", date_cols)
            
            # Crear dimensiones temporales
            df['Año'] = df[main_date_col].dt.year
            df['Mes'] = df[main_date_col].dt.month_name()
            df['Día Semana'] = df[main_date_col].dt.day_name()
            df['Trimestre'] = df[main_date_col].dt.quarter.apply(lambda x: f"T{x}")
            
            # Filtros dinámicos en el Sidebar
            years = sorted(df['Año'].unique().tolist())
            selected_years = st.sidebar.multiselect("Año", years, default=years)
            
            months = df['Mes'].unique().tolist()
            selected_months = st.sidebar.multiselect("Mes", months, default=months)
            
            # Aplicar Filtro Global
            df = df[(df['Año'].isin(selected_years)) & (df['Mes'].isin(selected_months))]
            st.sidebar.success(f"Analizando {len(df)} registros")
        
        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Vista previa de datos filtrados"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: DESCRIPTIVOS SELECCIONABLES ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            selected_vars = st.multiselect("Variables a analizar:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols)
            
            if selected_vars:
                desc = df[selected_vars].describe().T
                desc['Suma Total'] = df[selected_vars].sum()
                desc['Varianza'] = df[selected_vars].var()
                
                columns_order = ['mean', 'std', 'Varianza', 'min', 'max', '25%', '50%', '75%', 'count', 'Suma Total']
                desc_df = desc[columns_order]
                desc_df.columns = ['Media', 'Desv. Estándar', 'Varianza', 'Mínimo', 'Máximo', '25% (Q1)', '50% (Mediana)', '75% (Q3)', 'Registros', 'Suma Total']
                
                st.dataframe(desc_df.style.format("{:,.2f}"))

                with st.expander("📘 Guía de Interpretación Desarrollada"):
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        st.markdown("""
                        **1. Centralidad:** La **Media** es el promedio, pero la **Mediana (50%)** es más robusta si hay valores extremos.
                        **2. Dispersión:** La **Desv. Estándar** indica estabilidad. Si es alta, tus datos son volátiles.
                        """)
                    with col_exp2:
                        st.markdown("""
                        **3. Posicionamiento:** El **25% (Q1)** y **75% (Q3)** marcan los umbrales de tus valores bajos y altos.
                        """)
                        

        # --- SECCIÓN 4: VISUALIZACIÓN CON SEGMENTACIÓN ---
        st.divider()
        st.subheader("📈 Visualización y Segmentación de Gráficos")
        
        if numeric_cols:
            col_viz1, col_viz2 = st.columns([1, 2])
            
            with col_viz1:
                st.markdown("### ⚙️ Configuración")
                feat_y = st.selectbox("Métrica (Eje Y)", numeric_cols)
                
                # Aquí añadimos el COMBO DE SEGMENTACIÓN que pediste
                segmentar_por = st.selectbox(
                    "Segmentar/Agrupar por:", 
                    ["Año", "Mes", "Día Semana", "Trimestre"] + [c for c in df.columns if df[c].nunique() < 15 and c not in numeric_cols]
                )
                
                chart_type = st.radio("Tipo de gráfico", ["Barras", "Líneas", "Boxplot", "Violín"])

            with col_viz2:
                # Preparar datos agrupados para Barras y Líneas
                df_grouped = df.groupby(segmentar_por)[feat_y].agg(['sum', 'mean']).reset_index()
                
                if chart_type == "Barras":
                    # Usamos el total sumado para las barras
                    total_sum = df_grouped['sum'].sum()
                    df_grouped['label'] = df_grouped['sum'].apply(lambda x: f"{x:,.0f}<br>({(x/total_sum)*100:.1f}%)" if total_sum != 0 else "0")
                    fig = px.bar(df_grouped, x=segmentar_por, y='sum', text='label', template="plotly_dark", title=f"Total de {feat_y} por {segmentar_por}")
                    fig.update_yaxes(range=[0, df_grouped['sum'].max() * 1.2])
                    fig.update_traces(textposition='outside')

                elif chart_type == "Líneas":
                    # Usamos el promedio para las líneas (mejor para ver tendencias)
                    fig = px.line(df_grouped, x=segmentar_por, y='mean', template="plotly_dark", markers=True, title=f"Promedio de {feat_y} por {segmentar_por}")
                    

[Image of a line graph showing trends]


                elif chart_type == "Boxplot":
                    fig = px.box(df, x=segmentar_por, y=feat_y, template="plotly_dark", title=f"Distribución de {feat_y} por {segmentar_por}")

                else: # Violín
                    fig = px.violin(df, x=segmentar_por, y=feat_y, box=True, points="all", template="plotly_dark", title=f"Densidad de {feat_y} por {segmentar_por}")
                    

                st.plotly_chart(fig, use_container_width=True)
                st.info(f"💡 Interpretación: Este gráfico muestra cómo se distribuye o evoluciona '{feat_y}' cuando lo dividimos por '{segmentar_por}'.")

    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")
else:
    st.info("👋 Sube un archivo para comenzar el análisis segmentado.")
