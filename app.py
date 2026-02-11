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
        
        # --- VISTA PREVIA ---
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

        # --- NUEVA SECCIÓN: EXPLORACIÓN DE VALORES ÚNICOS ---
        st.divider()
        st.subheader("🔍 PASO 1.5: Exploración Detallada de Columnas")
        
        col_explorer_data = []
        for col in df.columns:
            unique_values = df[col].dropna().unique()
            n_unique = len(unique_values)
            
            if n_unique <= 5:
                # Si hay 5 o menos, mostramos todos
                display_values = ", ".join(map(str, sorted(unique_values)))
                label_tipo = "Todos los valores"
            else:
                # Si hay más de 5, tomamos una muestra aleatoria
                sample_values = random.sample(list(unique_values), 5)
                display_values = ", ".join(map(str, sample_values)) + "..."
                label_tipo = "Muestra aleatoria"
            
            col_explorer_data.append({
                "Columna": col,
                "Valores Únicos": n_unique,
                label_tipo: display_values
            })
        
        st.table(pd.DataFrame(col_explorer_data))

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
        
        if not df.empty:
            c_v1, c_v2 = st.columns([1, 3])
            
            with c_v1:
                # Permitimos elegir cualquier columna para el eje X (Categorías o Fechas)
                feat_x = st.selectbox("Variable Principal (Eje X):", potential_segments if len(potential_segments)>0 else df.columns)
                
                # Opciones de gráfico
                chart_type = st.radio("Tipo de Gráfico:", ["Barras (Frecuencias)", "Líneas (Tendencia)", "Boxplot", "Violín", "Histograma"])
                
                # La métrica Y solo es necesaria para ciertos gráficos
                feat_y = None
                if chart_type in ["Líneas", "Boxplot", "Violín"]:
                    feat_y = st.selectbox("Métrica Numérica (Eje Y):", numeric_cols)
            
            with c_v2:
                # Lógica de ordenación para fechas
                if feat_x == 'Mes': df_plot = df.sort_values('Mes_Num')
                elif feat_x == 'Día Semana': df_plot = df.sort_values('Día_Num')
                else: df_plot = df

                if chart_type == "Barras (Frecuencias)":
                    # Cálculo de Absolutos y Relativos
                    counts = df_plot[feat_x].value_counts().reset_index()
                    counts.columns = [feat_x, 'Absoluto']
                    total = counts['Absoluto'].sum()
                    counts['Relativo (%)'] = (counts['Absoluto'] / total * 100).round(1)
                    
                    # Creación del gráfico con etiquetas
                    fig = px.bar(counts, x=feat_x, y='Absoluto', 
                                 text=counts.apply(lambda r: f"{r['Absoluto']}<br>({r['Relativo (%)']}%)", axis=1),
                                 template="plotly_dark", 
                                 title=f"Distribución de {feat_x}")
                    
                    fig.update_traces(textposition='outside')
                    # Espacio extra arriba (15% más del máximo) para que no se corten las etiquetas
                    fig.update_layout(yaxis_range=[0, counts['Absoluto'].max() * 1.15])

                elif chart_type == "Líneas":
                    summary = df_plot.groupby(feat_x, sort=False)[feat_y].mean().reset_index()
                    fig = px.line(summary, x=feat_x, y=feat_y, template="plotly_dark", markers=True, 
                                  title=f"Promedio de {feat_y} por {feat_x}")

                elif chart_type == "Boxplot":
                    fig = px.box(df_plot, x=feat_x, y=feat_y, template="plotly_dark", 
                                 title=f"Dispersión de {feat_y} por {feat_x}")

                elif chart_type == "Violín":
                    fig = px.violin(df_plot, x=feat_x, y=feat_y, box=True, points="all", 
                                    template="plotly_dark", title=f"Densidad de {feat_y} por {feat_x}")

                else: # Histograma
                    target_h = feat_y if feat_y else numeric_cols[0]
                    fig = px.histogram(df_plot, x=target_h, template="plotly_dark", marginal="box", 
                                       title=f"Distribución de {target_h}")
                
                st.plotly_chart(fig, use_container_width=True)

        # --- SECCIÓN 4: TEST DE HIPÓTESIS (VALIDACIÓN CIENTÍFICA) ---
        st.divider()
        st.subheader("🧪 PASO 4: Validación Científica (T-Test)")
        
        # Filtramos columnas con exactamente 2 valores únicos para comparar grupos
        binary_cols = [c for c in df.columns if df[c].nunique() == 2]
        
        if binary_cols and numeric_cols:
            ch1, ch2 = st.columns(2)
            with ch1: 
                t_num = st.selectbox("Métrica numérica a comparar:", numeric_cols, key="tn")
            with ch2: 
                g_col = st.selectbox("Dividir grupos por la columna:", binary_cols, key="tc")
            
            # Separación de datos
            lbls = df[g_col].unique()
            g1 = df[df[g_col] == lbls[0]][t_num].dropna()
            g2 = df[df[g_col] == lbls[1]][t_num].dropna()
            
            if len(g1) > 1 and len(g2) > 1:
                # --- TABLA DE ESTADÍSTICOS SEGMENTADOS ---
                st.markdown(f"**Comparativa de grupos: {lbls[0]} vs {lbls[1]}**")
                
                def get_stats(data):
                    return {
                        "Registros": len(data),
                        "Media": data.mean(),
                        "Desv. Estándar": data.std(),
                        "25% (P25)": data.quantile(0.25),
                        "50% (Mediana)": data.median(),
                        "85% (P85)": data.quantile(0.85)
                    }

                stats_df = pd.DataFrame({
                    lbls[0]: get_stats(g1),
                    lbls[1]: get_stats(g2)
                }).T
                
                st.dataframe(stats_df.style.format(precision=2, thousands=".", decimal=","))

                # --- CÁLCULO DE T-TEST ---
                t_stat, p_val = stats.ttest_ind(g1, g2)
                
                st.write("---")
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    st.metric("P-valor (Confianza)", f"{p_val:.4f}")
                
                with col_m2:
                    if p_val < 0.05:
                        st.success("✅ **Diferencia Significativa:** Es muy poco probable que la diferencia sea por azar.")
                    else:
                        st.warning("⚠️ **Sin Evidencia:** No hay base estadística suficiente para decir que son distintos.")
                
                # Insight adicional sobre la diferencia de medias
                diff = ((g1.mean() - g2.mean()) / g2.mean()) * 100
                st.info(f"💡 El grupo **{lbls[0]}** tiene una media {abs(diff):.1f}% {'mayor' if diff > 0 else 'menor'} que el grupo **{lbls[1]}**.")

            else:
                st.error("No hay suficientes datos en uno de los grupos para realizar el test.")
        else:
            st.warning("Necesitas al menos una columna con solo 2 categorías (ej. Género, Segmento A/B) y una columna numérica para esta validación.")
# --- SECCIÓN 5: COMPARACIÓN DE MÁS DE 2 GRUPOS (ANOVA) ---
        st.divider()
        st.subheader("🧪 PASO 5: Comparación Múltiple (ANOVA)")

        with st.expander("📖 ¿Qué es este test y qué buscamos?"):
            st.markdown("""
            ### ¿Qué es el test ANOVA?
            El **ANOVA (Análisis de Varianza)** es una prueba estadística que se utiliza para comparar las medias de **tres o más grupos** al mismo tiempo. 
            
            **¿Qué buscamos aquí?**
            * **Hipótesis Nula (H0):** Todas las medias de los grupos son iguales (las diferencias que ves son pura casualidad).
            * **Hipótesis Alternativa (H1):** Al menos uno de los grupos tiene una media significativamente distinta a los demás.
            
            Es ideal para variables como *Etnia, Departamento, Nivel Educativo o País*, donde queremos saber si esa categoría realmente influye en el resultado numérico.
            """)

        # Filtramos columnas que tengan más de 2 valores únicos pero menos de 15 (para que sea interpretable)
        multi_groups = [c for c in df.columns if 2 < df[c].nunique() < 15]

        if multi_groups and numeric_cols:
            c1, c2 = st.columns(2)
            with c1:
                target_var = st.selectbox("Métrica numérica a analizar:", numeric_cols, key="anova_num")
            with c2:
                group_var = st.selectbox("Dividir grupos por la columna:", multi_groups, key="anova_cat")

            # 1. Mostrar Estadísticos por Segmento
            st.markdown(f"**Análisis descriptivo por {group_var}:**")
            
            # Calculamos los estadísticos solicitados anteriormente
            anova_stats = df.groupby(group_var)[target_var].agg([
                'count', 'mean', 'std', 
                lambda x: x.quantile(0.25), 
                'median', 
                lambda x: x.quantile(0.85)
            ]).reset_index()
            
            anova_stats.columns = [group_var, 'Registros', 'Media', 'Desv. Estándar', '25% (P25)', '50% (Mediana)', '85% (P85)']
            
            st.dataframe(anova_stats.style.format(precision=2, thousands=".", decimal=","))

            # 2. Ejecutar ANOVA
            # Preparamos los datos: una lista de series (una por cada grupo)
            groups_data = [group[target_var].dropna() for name, group in df.groupby(group_var)]
            
            if len(groups_data) > 2:
                f_stat, p_val_anova = stats.f_oneway(*groups_data)
                
                st.write("---")
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.metric("P-valor (ANOVA)", f"{p_val_anova:.4f}")
                
                with col_res2:
                    if p_val_anova < 0.05:
                        st.success(f"✅ **Diferencias Significativas:** Al menos uno de los grupos en **{group_var}** se comporta de forma distinta a los demás.")
                        st.info("💡 **Siguiente paso recomendado:** Revisa la tabla de arriba. El grupo con la Media o el P85 más alejado del resto es probablemente el que marca la diferencia.")
                    else:
                        st.warning(f"⚠️ **Sin Diferencias Claras:** No hay evidencia estadística de que los grupos de **{group_var}** afecten a la métrica **{target_var}**.")
            else:
                st.info("Se necesitan al menos 3 grupos con datos para ejecutar ANOVA.")
        else:
            st.warning("No se encontraron columnas con el número adecuado de categorías (entre 3 y 15) para realizar este análisis.")
    except Exception as e:
        st.error(f"Hubo un problema: {e}")
else:
    st.info("👋 Sube un archivo para empezar.")




