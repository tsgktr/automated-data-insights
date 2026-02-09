import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica con Segmentación Dinámica y Orden Cronológico Abreviado.")

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

        # 3. EXTRACCIÓN Y ORDENAMIENTO DE DIMENSIONES TEMPORALES
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols:
            main_date = date_cols[0]
            df['Año'] = df[main_date].dt.year
            # Creamos el número del mes para ordenar
            df['Mes_Num'] = df[main_date].dt.month
            # Creamos el nombre abreviado (Jan, Feb, etc.)
            # %b devuelve el nombre abreviado en el idioma local del sistema
            df['Mes'] = df[main_date].dt.strftime('%b')
            
            df['Día Semana'] = df[main_date].dt.day_name()
            df['Trimestre'] = df[main_date].dt.quarter.apply(lambda x: f"T{x}")

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa de los datos"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: DESCRIPTIVOS CON SEGMENTACIÓN ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado y Segmentado")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Lista de segmentos: Priorizamos Año y Mes
        time_segments = []
        if 'Año' in df.columns: time_segments.append('Año')
        if 'Mes' in df.columns: time_segments.append('Mes')
        
        potential_segments = ["Sin Segmentar"] + time_segments + [c for c in df.columns if df[c].nunique() < 25 and c not in numeric_cols and c not in time_segments]
        
        if numeric_cols:
            col_sel1, col_sel2 = st.columns([2, 1])
            
            with col_sel1:
                selected_vars = st.multiselect("1. Selecciona variables numéricas:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols)
            
            with col_sel2:
                segment_by = st.selectbox("2. Segmentar tabla por:", potential_segments)

            if selected_vars:
                if segment_by == "Sin Segmentar":
                    desc = df[selected_vars].describe().T
                    desc['Suma Total'] = df[selected_vars].sum()
                    desc['Varianza'] = df[selected_vars].var()
                    
                    desc_df = desc[['mean', 'std', 'Varianza', 'min', 'max', '25%', '50%', '75%', 'count', 'Suma Total']]
                    desc_df.columns = ['Media', 'Desv. Estándar', 'Varianza', 'Mínimo', 'Máximo', '25% (Q1)', '50% (Mediana)', '75% (Q3)', 'Registros', 'Suma Total']
                
                else:
                    # Lógica de ordenamiento para la segmentación
                    if segment_by == 'Mes':
                        # Agrupamos por número y nombre abreviado para mantener el orden
                        desc_grouped = df.groupby(['Mes_Num', 'Mes'])[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum'])
                        desc_grouped = desc_grouped.sort_index(level='Mes_Num')
                    elif segment_by == 'Año':
                        desc_grouped = df.groupby('Año')[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum']).sort_index()
                    else:
                        desc_grouped = df.groupby(segment_by)[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum']).sort_index()
                    
                    # Aplanar y renombrar
                    desc_grouped.columns = ['_'.join(col).strip() for col in desc_grouped.columns.values]
                    desc_df = desc_grouped.reset_index()
                    
                    # Eliminamos el número auxiliar para que solo quede el nombre Jan, Feb...
                    if 'Mes_Num' in desc_df.columns:
                        desc_df = desc_df.drop(columns=['Mes_Num'])

                    # Renombrado de columnas
                    for var in selected_vars:
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
                
                st.dataframe(desc_df.style.format(precision=2, thousands=".", decimal=","))

                with st.expander("📘 Guía de Interpretación"):
                    st.markdown("""
                    * **Media vs Mediana:** Si difieren mucho, hay valores atípicos (outliers).
                    
                    * **Desv. Estándar:** Alta dispersión = datos volátiles.
                    
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
                # Asegurar orden cronológico en el gráfico
                if 'Mes_Num' in df.columns:
                    df_plot = df.sort_values('Mes_Num')
                else:
                    df_plot = df.sort_values(feat_x)

                if chart_type == "Barras":
                    fig = px.bar(df_plot.groupby(feat_x, sort=False)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", text_auto='.2s')
                elif chart_type == "Líneas":
                    fig = px.line(df_plot.groupby(feat_x, sort=False)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", markers=True)
                else:
                    fig = px.box(df_plot, x=feat_x, y=feat_y, template="plotly_dark")
                
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Sube un archivo para comenzar.")
