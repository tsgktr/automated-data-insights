import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica con Segmentación Dinámica en Estadísticas Descriptivas.")

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

        # 3. EXTRACCIÓN DE DIMENSIONES TEMPORALES
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols:
            main_date = date_cols[0]
            df['Año'] = df[main_date].dt.year
            df['Mes'] = df[main_date].dt.month_name()
            df['Día Semana'] = df[main_date].dt.day_name()
            df['Trimestre'] = df[main_date].dt.quarter.apply(lambda x: f"T{x}")

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa de los datos"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: DESCRIPTIVOS CON SEGMENTACIÓN ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado y Segmentado")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        # Identificamos columnas para segmentar (Fechas + Categorías con pocos valores)
        potential_segments = ["Sin Segmentar"] + [c for c in df.columns if df[c].nunique() < 25 and c not in numeric_cols]
        
        if numeric_cols:
            col_sel1, col_sel2 = st.columns([2, 1])
            
            with col_sel1:
                selected_vars = st.multiselect("1. Selecciona variables numéricas:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols)
            
            with col_sel2:
                segment_by = st.selectbox("2. Segmentar tabla por:", potential_segments)

            if selected_vars:
                if segment_by == "Sin Segmentar":
                    # --- MODO NORMAL ---
                    desc = df[selected_vars].describe().T
                    desc['Suma Total'] = df[selected_vars].sum()
                    desc['Varianza'] = df[selected_vars].var()
                    
                    # Reordenar y renombrar
                    desc_df = desc[['mean', 'std', 'Varianza', 'min', 'max', '25%', '50%', '75%', 'count', 'Suma Total']]
                    desc_df.columns = ['Media', 'Desv. Estándar', 'Varianza', 'Mínimo', 'Máximo', '25% (Q1)', '50% (Mediana)', '75% (Q3)', 'Registros', 'Suma Total']
                
                else:
                    # --- MODO SEGMENTADO (AGRUPADO) ---
                    # Agrupamos y calculamos todas las métricas de una vez
                    desc_grouped = df.groupby(segment_by)[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum'])
                    
                    # Aplanamos el índice de columnas (que queda como multi-nivel)
                    desc_grouped.columns = ['_'.join(col).strip() for col in desc_grouped.columns.values]
                    desc_df = desc_grouped.reset_index()
                    
                    # Como hay múltiples variables, para no saturar la tabla, mostramos una variable a la vez si hay segmentación
                    # o permitimos ver el bloque completo. Para esta versión, mostramos el bloque completo renombrado.
                    final_cols = [segment_by]
                    for var in selected_vars:
                        # Renombramos para que el usuario entienda qué es qué
                        desc_df = desc_df.rename(columns={
                            f'{var}_mean': f'{var} | Media',
                            f'{var}_std': f'{var} | Desv. Estándar',
                            f'{var}_var': f'{var} | Varianza',
                            f'{var}_min': f'{var} | Mínimo',
                            f'{var}_max': f'{var} | Máximo',
                            f'{var}_median': f'{var} | Mediana',
                            f'{var}_count': f'{var} | Registros',
                            f'{var}_sum': f'{var} | Suma Total'
                        })
                
                # Mostrar tabla final
                st.dataframe(desc_df.style.format(precision=2, thousands=".", decimal=","))

                # --- DESPLEGABLE DE INTERPRETACIÓN ---
                with st.expander("📘 Guía de Interpretación de Métricas"):
                    st.markdown("""
                    ### 📘 Glosario Desarrollado
                    * **Media:** Es el promedio aritmético. Indica el "centro" de tus datos.
                    * **Desv. Estándar:** Indica cuánto se alejan los datos de la media. Si es alta, los datos están muy dispersos.
                    * **Varianza:** El cuadrado de la desviación. Útil para medir la incertidumbre.
                    * **50% (Mediana):** El valor central. Si la Media es muy distinta a la Mediana, hay valores extremos influyendo.
                    * **Cuartiles (25%, 75%):** Indican dónde se corta el 25% más bajo y el 25% más alto de la muestra.
                    """)
                    

        # --- SECCIÓN 3: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización")
        if numeric_cols:
            col_v1, col_v2 = st.columns([1, 2])
            with col_v1:
                feat_x = st.selectbox("Eje X", potential_segments[1:] if len(potential_segments)>1 else df.columns)
                feat_y = st.selectbox("Eje Y", numeric_cols)
                chart_type = st.radio("Gráfico", ["Barras", "Líneas", "Boxplot"])
            
            with col_v2:
                if chart_type == "Barras":
                    fig = px.bar(df.groupby(feat_x)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", text_auto='.2s')
                elif chart_type == "Líneas":
                    fig = px.line(df.groupby(feat_x)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", markers=True)
                else:
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Se produjo un error al procesar la tabla: {e}")
else:
    st.info("👋 Sube un archivo para comenzar el análisis segmentado.")
