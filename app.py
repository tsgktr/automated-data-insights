import streamlit as st
import pandas as pd
import plotly.express as px
import random
from scipy import stats

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights Pro")
st.markdown("Tu analista virtual: Convierte datos complejos en decisiones claras.")

uploaded_file = st.file_uploader("1. Sube tu archivo (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 1. CARGA DE DATOS
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # --- NUEVA SECCIÓN: VISTA PREVIA ---
        with st.expander("👀 Vista previa de los datos (Primeras 5 filas)"):
            st.dataframe(df.head())
        
        # --- GESTIÓN DE TIPOS DE DATOS ---
        with st.expander("🛠️ PASO 1: Configurar tipos de datos (Opcional)"):
            st.info("Asegúrate de que los números sean 'Numérico' y las fechas 'Fecha'.")
            type_col1, type_col2 = st.columns(2)
            for i, col in enumerate(df.columns):
                target_container = type_col1 if i % 2 == 0 else type_col2
                current_type = str(df[col].dtype)
                options = ["Mantener actual", "Numérico", "Texto / Categoría", "Fecha"]
                selection = target_container.selectbox(f"**{col}** ({current_type})", options, key=f"t_{col}")
                
                if selection == "Numérico":
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif selection == "Texto / Categoría":
                    df[col] = df[col].astype(str)
                elif selection == "Fecha":
                    df[col] = pd.to_datetime(df[col], errors='coerce')

        # 2. PROCESAMIENTO DE FECHAS AUTOMÁTICO
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols:
            main_date = date_cols[0]
            df['Año'] = df[main_date].dt.year
            df['Mes_Num'] = df[main_date].dt.month
            df['Mes'] = df[main_date].dt.strftime('%b')
            df['Día_Num'] = df[main_date].dt.dayofweek 
            df['Día Semana'] = df[main_date].dt.strftime('%a')

        # --- SECCIÓN 2: DESCRIPTIVOS E INSIGHTS ---
        st.divider()
        st.subheader("🔢 PASO 2: Análisis Descriptivo e Insights")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        time_segments = [c for c in ['Año', 'Mes', 'Día Semana'] if c in df.columns]
        potential_segments = ["Sin Segmentar"] + time_segments + [c for c in df.columns if df[c].nunique() < 25 and c not in numeric_cols]
        
        if numeric_cols:
            c_sel1, c_sel2 = st.columns([2, 1])
            with c_sel1:
                selected_vars = st.multiselect("Selecciona variables para analizar:", numeric_cols, default=numeric_cols[:1])
            with c_sel2:
                segment_by = st.selectbox("Segmentar por:", potential_segments)

            if selected_vars:
                if segment_by == "Sin Segmentar":
                    desc_df = df[selected_vars].describe().T
                    desc_df['Varianza'] = df[selected_vars].var()
                    desc_df['Suma Total'] = df[selected_vars].sum()
                    
                    desc_df = desc_df[['count', 'mean', 'std', 'Varianza', 'min', '25%', '50%', '75%', 'max', 'Suma Total']]
                    desc_df.columns = [
                        'Registros (N)', 'Media', 'Desv. Estándar', 'Varianza', 
                        'Mínimo', '25% (Bajos)', 'Mediana (Centro)', '75% (Altos)', 
                        'Máximo', 'Suma Total'
                    ]
                    st.dataframe(desc_df.style.format(precision=2, thousands=".", decimal=","))
                    
                    st.markdown("### 💡 Diagnóstico del Analista Virtual")
                    for var in selected_vars:
                        m, med, std, q3, mx = df[var].mean(), df[var].median(), df[var].std(), df[var].quantile(0.75), df[var].max()
                        
                        with st.container():
                            st.write(f"**Análisis de {var}:**")
                            if abs(m - med) / (med if med != 0 else 1) > 0.15:
                                st.write(f"⚠️ **Sesgo Detectado:** El promedio ({m:,.2f}) es muy distinto a la mediana ({med:,.2f}). Tienes valores extremos distorsionando el resultado.")
                            else:
                                st.write(f"✅ **Equilibrio:** El promedio es una representación fiel de tus datos.")
                            if std > abs(m):
                                st.write(f"🚩 **Inestabilidad:** La variación es altísima respecto al promedio. Tus datos son impredecibles.")
                            st.write(f"ℹ️ El 75% de tus casos están por debajo de {q3:,.2f}. Si el máximo es {mx:,.2f}, el tramo final concentra mucha diferencia.")

                else:
                    desc_grouped = df.groupby(segment_by)[selected_vars].agg(['mean', 'std', 'median', 'count', 'sum'])
                    desc_grouped.columns = ['_'.join(col).strip() for col in desc_grouped.columns.values]
                    st.dataframe(desc_grouped.reset_index().style.format(precision=2, thousands=".", decimal=","))

        # --- GUÍA EDUCATIVA ---
        with st.expander("🎓 CURSO RÁPIDO: ¿Cómo entender estos números? (Nivel 0)"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("""
                **1. ¿Dónde está el centro?**
                * **Media (Promedio):** Reparto igualitario. 
                * **Mediana (Centro Real):** El valor que separa al 50% de los datos. 
                """)
                st.write("")
            with col_b:
                st.markdown("""
                **2. ¿Qué tan estable es todo?**
                * **Desv. Estándar:** Es el margen de error. Si es pequeña, tus datos son constantes. 
                """)
                st.write("")

        # --- SECCIÓN 3: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 PASO 3: Visualización")
        if numeric_cols:
            c_v1, c_v2 = st.columns([1, 3])
            with c_v1:
                feat_x = st.selectbox("Segmentar gráfico por:", potential_segments[1:] if len(potential_segments)>1 else df.columns)
                feat_y = st.selectbox("Métrica a medir:", numeric_cols)
                chart_type = st.radio("Gráfico:", ["Barras", "Líneas", "Boxplot", "Violín", "Histograma"])
            
            with c_v2:
                if feat_x == 'Mes': df_plot = df.sort_values('Mes_Num')
                elif feat_x == 'Día Semana': df_plot = df.sort_values('Día_Num')
                else: df_plot = df
                
                if chart_type == "Barras":
                    fig = px.bar(df_plot.groupby(feat_x, sort=False)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", title=f"Suma de {feat_y}")
                elif chart_type == "Líneas":
                    fig = px.line(df_plot.groupby(feat_x, sort=False)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", markers=True, title=f"Promedio de {feat_y}")
                elif chart_type == "Boxplot":
                    fig = px.box(df_plot, x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Violín":
                    fig = px.violin(df_plot, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                else:
                    fig = px.histogram(df_plot, x=feat_y, template="plotly_dark", marginal="box", title=f"Distribución de {feat_y}")
                    st.write("")
                
                st.plotly_chart(fig, use_container_width=True)

        # --- SECCIÓN 4: TEST DE HIPÓTESIS ---
        st.divider()
        st.subheader("🧪 PASO 4: Validación Científica (T-Test)")
        binary_cols = [c for c in df.columns if df[c].nunique() == 2]
        if binary_cols and numeric_cols:
            ch1, ch2 = st.columns(2)
            with ch1: t_num = st.selectbox("Métrica a comparar:", numeric_cols, key="tn")
            with ch2: g_col = st.selectbox("Comparar grupos de:", binary_cols, key="tc")
            
            lbls = df[g_col].unique()
            g1 = df[df[g_col] == lbls[0]][t_num].dropna()
            g2 = df[df[g_col] == lbls[1]][t_num].dropna()
            
            if len(g1) > 1 and len(g2) > 1:
                t_stat, p_val = stats.ttest_ind(g1, g2)
                st.metric("P-valor (Probabilidad de error)", f"{p_val:.4f}")
                if p_val < 0.05:
                    st.success(f"✅ **Diferencia Real:** Los grupos '{lbls[0]}' y '{lbls[1]}' NO son iguales estadísticamente.")
                else:
                    st.warning(f"⚠️ **Sin pruebas:** La diferencia podría ser casualidad.")
                st.write("")

    except Exception as e:
        st.error(f"Hubo un problema: {e}")
else:
    st.info("👋 Sube un archivo para empezar.")
