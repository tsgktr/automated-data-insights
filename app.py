import streamlit as st
import pandas as pd
import plotly.express as px
import random
from scipy import stats # Nueva librería para estadística inferencial

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights + Inferencial")
st.markdown("Analítica descriptiva y validación de hipótesis estadísticas.")

uploaded_file = st.file_uploader("Elige un fichero (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("¡Archivo cargado con éxito!")

        # --- MOTOR DE FECHAS ---
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    continue

        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if date_cols:
            main_date = date_cols[0]
            df['Año'] = df[main_date].dt.year
            df['Mes_Num'] = df[main_date].dt.month
            df['Mes'] = df[main_date].dt.strftime('%b')

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: DESCRIPTIVOS ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        potential_segments = ["Sin Segmentar"] + [c for c in df.columns if df[c].nunique() < 25 and c not in numeric_cols]
        
        if numeric_cols:
            c1, c2 = st.columns([2, 1])
            with c1:
                selected_vars = st.multiselect("Variables:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols)>1 else numeric_cols)
            with c2:
                segment_by = st.selectbox("Segmentar por:", potential_segments)

            if selected_vars:
                if segment_by == "Sin Segmentar":
                    desc_df = df[selected_vars].describe().T
                    desc_df['Suma Total'] = df[selected_vars].sum()
                    desc_df['Varianza'] = df[selected_vars].var()
                    desc_df = desc_df[['mean', 'std', 'Varianza', 'min', 'max', '25%', '50%', '75%', 'count', 'Suma Total']]
                    desc_df.columns = ['Media', 'Desv. Est.', 'Varianza', 'Mín', 'Máx', '25%', 'Mediana', '75%', 'N', 'Suma']
                else:
                    desc_grouped = df.groupby(segment_by)[selected_vars].agg(['mean', 'std', 'median', 'count'])
                    desc_grouped.columns = ['_'.join(col).strip() for col in desc_grouped.columns.values]
                    desc_df = desc_grouped.reset_index()
                
                st.dataframe(desc_df.style.format(precision=2))

        # --- NUEVA SECCIÓN: TEST DE HIPÓTESIS (T-TEST) ---
        st.divider()
        st.subheader("🧪 Validación de Hipótesis (T-Test)")
        st.markdown("Compara si la diferencia entre dos grupos es estadísticamente significativa.")

        # Necesitamos una variable categórica de exactamente 2 niveles (ej: Si/No, A/B, M/F)
        binary_cols = [c for c in df.columns if df[c].nunique() == 2]

        if binary_cols and numeric_cols:
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                target_num = st.selectbox("Métrica a comparar:", numeric_cols)
            with col_h2:
                group_col = st.selectbox("Dividir grupos por:", binary_cols)

            # Ejecución del Test
            group_labels = df[group_col].unique()
            group1 = df[df[group_col] == group_labels[0]][target_num].dropna()
            group2 = df[df[group_col] == group_labels[1]][target_num].dropna()

            t_stat, p_value = stats.ttest_ind(group1, group2)

            # Resultado visual
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.metric(f"Media {group_labels[0]}", f"{group1.mean():.2f}")
                st.metric(f"Media {group_labels[1]}", f"{group2.mean():.2f}")
            
            with c_res2:
                st.write(f"**P-valor:** `{p_value:.4f}`")
                if p_value < 0.05:
                    st.success("✅ **Diferencia Significativa:** Es muy poco probable que esta diferencia sea por azar.")
                else:
                    st.warning("⚠️ **Diferencia NO Significativa:** La diferencia podría ser fruto del azar.")
            
            with st.expander("❓ ¿Cómo interpretar el P-valor?"):
                st.markdown("""
                La prueba T compara las medias de dos grupos:
                * **P-valor < 0.05:** Los grupos son realmente diferentes. Hay un efecto real.
                * **P-valor > 0.05:** No hay pruebas suficientes para decir que son diferentes.
                """)
                
        else:
            st.info("Para esta prueba necesitas una columna con solo 2 categorías (ej. Género, Pagado: Si/No).")

        # --- SECCIÓN VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización")
        if numeric_cols:
            feat_x = st.selectbox("Eje X", potential_segments[1:] if len(potential_segments)>1 else df.columns)
            feat_y = st.selectbox("Eje Y", numeric_cols)
            chart_type = st.radio("Gráfico", ["Barras", "Líneas", "Boxplot"], horizontal=True)
            
            df_plot = df.sort_values('Mes_Num') if 'Mes_Num' in df.columns else df
            
            if chart_type == "Barras":
                fig = px.bar(df_plot.groupby(feat_x, sort=False)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, template="plotly_dark")
            elif chart_type == "Líneas":
                fig = px.line(df_plot.groupby(feat_x, sort=False)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark", markers=True)
            else:
                fig = px.box(df_plot, x=feat_x, y=feat_y, template="plotly_dark")
            
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
