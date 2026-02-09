import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Automated Data Insights Pro", layout="wide")

st.title("📊 Automated Data Insights")
st.markdown("Analítica descriptiva con detección inteligente de fechas y filtros temporales.")

uploaded_file = st.file_uploader("Elige un fichero (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 1. CARGA DE DATOS
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # 2. DETECCIÓN Y CONVERSIÓN DE FECHAS
        # Intentamos convertir columnas que contengan 'fecha', 'date', 'time' o que parezcan fechas
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Probamos si es convertible a fecha
                    df[col] = pd.to_datetime(df[col])
                except:
                    continue

        # 3. EXTRACCIÓN DE VARIABLES TEMPORALES (Si hay fechas)
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if date_cols:
            st.sidebar.header("📅 Filtros Temporales")
            # Usamos la primera columna de fecha detectada para los filtros maestros
            main_date_col = st.sidebar.selectbox("Columna de fecha para filtrar:", date_cols)
            
            # Extraemos componentes para filtrar
            df['Año'] = df[main_date_col].dt.year
            df['Mes_Num'] = df[main_date_col].dt.month
            df['Mes'] = df[main_date_col].dt.month_name()
            df['Semana_Año'] = df[main_date_col].dt.isocalendar().week
            df['Dia_Semana'] = df[main_date_col].dt.day_name()

            # Widgets de filtro en el sidebar
            years = sorted(df['Año'].unique().tolist())
            selected_years = st.sidebar.multiselect("Filtrar por Año:", years, default=years)
            
            months = df['Mes'].unique().tolist()
            selected_months = st.sidebar.multiselect("Filtrar por Mes:", months, default=months)

            # Aplicar filtros al DataFrame
            df = df[(df['Año'].isin(selected_years)) & (df['Mes'].isin(selected_months))]
            
            st.success(f"✅ Fechas detectadas en: {', '.join(date_cols)}. Filtros aplicados.")

        # --- SECCIÓN 1: VISTA PREVIA ---
        with st.expander("👀 Ver vista previa de los datos filtrados"):
            st.dataframe(df.head(5))

        # --- SECCIÓN 2: ESTRUCTURA ---
        st.subheader("🔍 Estructura de las Columnas")
        info_data = []
        for col in df.columns:
            info_data.append({
                "Columna": col, "Tipo": str(df[col].dtype), 
                "Nulos": df[col].isnull().sum(), "Únicos": df[col].nunique()
            })
        st.table(pd.DataFrame(info_data))

        # --- SECCIÓN 3: DESCRIPTIVOS SELECCIONABLES ---
        st.divider()
        st.subheader("🔢 Análisis Descriptivo Personalizado")
        
        # Incluimos las nuevas variables temporales si el usuario quiere analizarlas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            selected_vars = st.multiselect("Selecciona variables para analizar:", numeric_cols, default=numeric_cols[:2] if len(numeric_cols) > 1 else numeric_cols)
            
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
                        #### 1. Centralidad y Dispersión
                        * **Media vs Mediana (50%):** Si la media es muy distinta a la mediana, tus datos tienen sesgo (hay valores extremos).
                        * **Desv. Estándar:** Si es muy alta respecto a la media, tus datos son poco uniformes.
                        """)
                    with col_exp2:
                        st.markdown("""
                        #### 2. Posicionamiento
                        * **25% y 75%:** Marcan dónde empieza el grupo de valores "bajos" y dónde el de valores "altos" (Top 25%).
                        """)
                        

        # --- SECCIÓN 4: VISUALIZACIÓN ---
        st.divider()
        st.subheader("📈 Visualización e Interpretación")
        
        all_cols = df.columns.tolist()
        if numeric_cols:
            col_viz1, col_viz2 = st.columns([1, 2])
            with col_viz1:
                feat_x = st.selectbox("Eje X (Prueba a usar 'Mes' o 'Dia_Semana')", all_cols)
                feat_y = st.selectbox("Eje Y", numeric_cols)
                chart_type = st.radio("Tipo de gráfico", ["Barras", "Líneas", "Boxplot", "Violín", "Histograma"])

            with col_viz2:
                if chart_type == "Barras":
                    # Ordenar meses cronológicamente si X es Mes
                    df_plot = df.copy()
                    fig = px.bar(df_plot.groupby(feat_x)[feat_y].sum().reset_index(), x=feat_x, y=feat_y, text_auto='.2s', template="plotly_dark")
                elif chart_type == "Líneas":
                    fig = px.line(df.groupby(feat_x)[feat_y].mean().reset_index(), x=feat_x, y=feat_y, template="plotly_dark")
                elif chart_type == "Boxplot":
                    fig = px.box(df, x=feat_x, y=feat_y, template="plotly_dark")
                
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Sube un archivo para activar los filtros inteligentes de fecha.")
