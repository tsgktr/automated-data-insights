import streamlit as st
import pandas as pd
import plotly.express as px
import random
from scipy import stats  # Requiere 'scipy' en requirements.txt

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
            df['Mes_Num'] = df[main_date].dt.month
            df['Mes'] = df[main_date].dt.strftime('%b')
            
            # ORDENACIÓN DE DÍAS DE LA SEMANA
            # %a da el nombre abreviado (Mon, Tue...) y %w el número (0=Sunday, 1=Monday...)
            df['Día_Num'] = df[main_date].dt.dayofweek # Monday=0, Sunday=6
            df['Día Semana'] = df[main_date].dt.strftime('%a')
            
            df['Trimestre'] = df[main_date].dt.quarter.apply(lambda x: f"T{x}")

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa de los datos"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: DESCRIPTIVOS CON SEGMENTACIÓN ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado y Segmentado")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        time_segments = []
        if 'Año' in df.columns: time_segments.append('Año')
        if 'Mes' in df.columns: time_segments.append('Mes')
        if 'Día Semana' in df.columns: time_segments.append('Día Semana')
        
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
                        desc_grouped = df.groupby(['Mes_Num', 'Mes'])[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum']).sort_index(level='Mes_Num')
                    elif segment_by == 'Día Semana':
                        desc_grouped = df.groupby(['Día_Num', 'Día Semana'])[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum']).sort_index(level='Día_Num')
                    else:
                        desc_grouped = df.groupby(segment_by)[selected_vars].agg(['mean', 'std', 'var', 'min', 'max', 'median', 'count', 'sum']).sort_index()
                    
                    desc_grouped.columns = ['_'.join(col).strip() for col in desc_grouped.columns.values]
                    desc_df = desc_grouped.reset_index()
                    if 'Mes_Num' in desc_df.columns: desc_df = desc_df.drop(columns=['Mes_Num'])
                    if 'Día_Num' in desc_df.columns: desc_df = desc_df.drop(columns=['Día_Num'])

                    for var in selected_vars:
                        desc_df = desc_df.rename(columns={
                            f'{var}_mean': f'{var} | Media', f'{var}_std': f'{var} | Desv. Estándar',
                            f'{var}_var': f'{var} | Varianza', f'{var}_min': f'{var} | Mínimo',
                            f'{var}_max': f'{var} | Máximo', f'{var}_median': f'{var} | Mediana',
                            f'{var}_count': f'{var} | Registros', f'{var}_sum': f'{var} | Suma Total'
                        })
                st.dataframe(desc_df.style.format(precision=2, thousands=".", decimal=","))

        # --- SECCIÓN 3: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización")
        if numeric_cols:
            col_v1, col_v2 = st.columns([1, 2])
            with col_v1:
                feat_x = st.selectbox("Eje X", potential_segments[1:] if len(potential_segments)>1 else df.columns)
                feat_y = st.selectbox("Eje Y", numeric_cols)
                chart_type = st.radio("Gráfico", ["Barras", "Líneas", "Boxplot", "Violín", "Histograma"])
            
            with col_v2:
                # Ordenar dataframe para el gráfico
                if feat_x == 'Mes':
                    df_plot = df.sort_values('Mes_Num')
                elif feat_x == 'Día Semana':
                    df_plot = df.sort_values('Día_Num')
                else:
                    df_plot = df.sort_values(feat_x)

                if chart_type == "Barras":
                    fig = px.bar(df_plot.groupby(feat_x, sort=False)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", text_auto='.2s')
                elif chart_type == "Líneas":
                    fig = px.line(df_plot.groupby(feat_x, sort=False)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", markers=True)
                elif chart_type == "Boxplot":
                    fig = px.box(df_plot, x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Violín":
                    fig = px.violin(df_plot, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                elif chart_type == "Histograma":
                    fig = px.histogram(df_plot, x=feat_y, color=feat_x if feat_x != feat_y else None, template="plotly_dark", marginal="rug", nbins=30)
                
                st.plotly_chart(fig, use_container_width=True)

        # --- SECCIÓN 4: TEST DE HIPÓTESIS ---
        st.divider()
        st.subheader("🧪 Validación de Hipótesis (T-Test)")
        binary_cols = [c for c in df.columns if df[c].nunique() == 2]

        if binary_cols and numeric_cols:
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                target_num = st.selectbox("Métrica a comparar:", numeric_cols, key="ttest_num")
            with col_h2:
                group_col = st.selectbox("Dividir grupos por:", binary_cols, key="ttest_cat")

            group_labels = df[group_col].unique()
            g1_data = df[df[group_col] == group_labels[0]][target_num].dropna()
            g2_data = df[df[group_col] == group_labels[1]][target_num].dropna()

            if len(g1_data) > 1 and len(g2_data) > 1:
                t_stat, p_value = stats.ttest_ind(g1_data, g2_data)
                c_res1, c_res2 = st.columns(2)
                with c_res1:
                    st.metric(f"Media {group_labels[0]}", f"{g1_data.mean():,.2f}")
                    st.metric(f"Media {group_labels[1]}", f"{g2_data.mean():,.2f}")
                with c_res2:
                    st.write(f"**P-valor:** `{p_value:.4f}`")
                    if p_value < 0.05:
                        st.success("✅ Diferencia Significativa")
                    else:
                        st.warning("⚠️ Diferencia NO Significativa")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Sube un archivo para comenzar.")
