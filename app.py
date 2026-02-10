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
                # Cálculo de descriptivos
                if segment_by == "Sin Segmentar":
                    desc_df = df[selected_vars].describe().T
                    desc_df['Suma Total'] = df[selected_vars].sum()
                    desc_df['Varianza'] = df[selected_vars].var()
                    desc_df = desc_df[['mean', 'std', 'min', 'max', '25%', '50%', '75%', 'count', 'Suma Total']]
                    desc_df.columns = ['Media', 'Desv. Est.', 'Varianza', 'Mín', 'Máx', '25%', 'Mediana', '75%', 'N', 'Suma']
                    st.dataframe(desc_df.style.format(precision=2))
                    
                    # --- INSIGHTS AUTOMÁTICOS ---
                    st.markdown("### 💡 Diagnóstico del Analista Virtual")
                    for var in selected_vars:
                        m = df[var].mean()
                        med = df[var].median()
                        std = df[var].std()
                        q3 = df[var].quantile(0.75)
                        mx = df[var].max()
                        
                        with st.container():
                            st.write(f"**Análisis de {var}:**")
                            # Lógica de sesgo
                            if abs(m - med) / med > 0.1:
                                st.write(f"⚠️ El promedio ({m:.2f}) es muy distinto a la mediana ({med:.2f}). Tienes valores extremos (muy altos o muy bajos) que están distorsionando la realidad.")
                            else:
                                st.write(f"✅ Los datos son bastante equilibrados; el promedio es una buena representación del grupo.")
                            
                            # Lógica de dispersión
                            if std > m:
                                st.write(f"🚩 **Alerta de Inestabilidad:** La variación es mayor que el promedio. Esto indica un comportamiento muy caótico o impredecible.")
                            
                            # Lógica de Pareto/Concentración
                            st.write(f"ℹ️ El 75% de tus datos son menores a {q3:.2f}, pero el valor máximo llega hasta {mx:.2f}. Esto sugiere que hay un grupo pequeño con valores excepcionalmente altos.")

                else:
                    # Tabla segmentada
                    desc_grouped = df.groupby(segment_by)[selected_vars].agg(['mean', 'std', 'median', 'count', 'sum'])
                    desc_grouped.columns = ['_'.join(col).strip() for col in desc_grouped.columns.values]
                    st.dataframe(desc_grouped.reset_index().style.format(precision=2))

        # --- GUÍA EDUCATIVA ---
        with st.expander("🎓 CURSO RÁPIDO: ¿Cómo entender estos números? (Nivel 0)"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("""
                **1. ¿Dónde está el centro?**
                * **Media (Promedio):** Es el reparto igualitario. 
                * **Mediana (50%):** Es el valor "de en medio". Si la media es mucho más alta que la mediana, ¡Cuidado! Tienes unos pocos valores gigantes inflando el resultado.
                """)
                
            with col_b:
                st.markdown("""
                **2. ¿Qué tan estable es todo?**
                * **Desv. Estándar:** Es el margen de error. Si es pequeña, los datos son parecidos. Si es gigante, hay mucha desigualdad.
                * **Máximo y Mínimo:** Los límites de tu universo de datos.
                """)
                

        # --- SECCIÓN 3: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 PASO 3: Visualización")
        if numeric_cols:
            c_v1, c_v2 = st.columns([1, 3])
            with c_v1:
                feat_x = st.selectbox("Eje X (Categoría)", potential_segments[1:] if len(potential_segments)>1 else df.columns)
                feat_y = st.selectbox("Eje Y (Métrica)", numeric_cols)
                chart_type = st.radio("Gráfico:", ["Barras", "Líneas", "Boxplot", "Violín", "Histograma"])
            
            with c_v2:
                df_plot = df.sort_values('Mes_Num') if 'Mes_Num' in df.columns else df
                if chart_type == "Barras":
                    fig = px.bar(df_plot.groupby(feat_x, sort=False)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", title=f"Total de {feat_y} por {feat_x}")
                elif chart_type == "Líneas":
                    fig = px.line(df_plot.groupby(feat_x, sort=False)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", markers=True, title=f"Evolución promedio de {feat_y}")
                elif chart_type == "Boxplot":
                    fig = px.box(df_plot, x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Violín":
                    fig = px.violin(df_plot, x=feat_x, y=feat_y, box=True, points="all", template="plotly_dark")
                else:
                    fig = px.histogram(df_plot, x=feat_y, template="plotly_dark", marginal="box")
                
                st.plotly_chart(fig, use_container_width=True)
                

        # --- SECCIÓN 4: TEST DE HIPÓTESIS ---
        st.divider()
        st.subheader("🧪 PASO 4: Validación Científica (T-Test)")
        binary_cols = [c for c in df.columns if df[c].nunique() == 2]
        if binary_cols and numeric_cols:
            ch1, ch2 = st.columns(2)
            with ch1: t_num = st.selectbox("Métrica:", numeric_cols, key="t_n")
            with ch2: g_col = st.selectbox("Comparar grupos de:", binary_cols, key="t_c")
            
            labels = df[g_col].unique()
            g1 = df[df[g_col] == labels[0]][t_num].dropna()
            g2 = df[df[g_col] == labels[1]][t_num].dropna()
            
            if len(g1) > 1 and len(g2) > 1:
                t_stat, p_val = stats.ttest_ind(g1, g2)
                st.metric("P-valor (Probabilidad de error)", f"{p_val:.4f}")
                if p_val < 0.05:
                    st.success(f"✅ Confirmado: Hay una diferencia REAL entre {labels[0]} y {labels[1]}.")
                else:
                    st.warning(f"⚠️ Sin pruebas: La diferencia entre {labels[0]} y {labels[1]} puede ser casualidad.")
                

    except Exception as e:
        st.error(f"Hubo un problema: {e}")
else:
    st.info("👋 Sube un archivo para empezar tu consultoría de datos.")
