import json
import os
import pandas as pd
import streamlit as st
import plotly.express as px

##############################################################################
# CONFIGURACIÓN DE LA PÁGINA Y ESTILO
##############################################################################
st.set_page_config(layout="wide", page_title="Dashboard de Contratos, Gastos y Consumos")

# Ajustamos el tamaño de fuente global a 12px
st.markdown(
    """
    <style>
    * { font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True
)

##############################################################################
# FUNCIONES DE FORMATO Y ESTILO
##############################################################################
def custom_spanish_format(x):
    """
    Convierte el número a entero (sin decimales) y usa punto como separador de miles.
    Ejemplo: 1234567 -> "1.234.567"
    """
    if pd.isnull(x):
        return ""
    try:
        x_int = int(round(x))
        s = f"{x_int:,}"
        return s.replace(",", ".")
    except Exception:
        return str(x)

def style_totals(df):
    """
    Aplica estilo a la fila "Total Mensual" y a la columna "Total Anual" (negrita y color negro).
    """
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    if "contrato" in df.columns:
        for i, row in df.iterrows():
            if str(row["contrato"]) == "Total Mensual":
                styles.loc[i, :] = "font-weight: bold; color: black;"
    if "Total Anual" in df.columns:
        for i in df.index:
            styles.loc[i, "Total Anual"] = "font-weight: bold; color: black;"
    return styles

def highlight_max_red(df, months_selected):
    """
    Resalta en rojo y negrita el importe máximo en cada fila (solo en las columnas de meses,
    ignorando "Total Anual" y la fila "Total Mensual").
    """
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    if "contrato" not in df.columns:
        return styles
    for i, row in df.iterrows():
        if str(row["contrato"]) == "Total Mensual":
            continue
        row_values = row[months_selected]
        if not row_values.empty:
            max_val = row_values.max()
            for col in months_selected:
                # Si hay empate, se resaltan todas las que alcanzan el valor máximo
                if row[col] == max_val:
                    styles.loc[i, col] = "color: red; font-weight: bold;"
    return styles

##############################################################################
# CARGA Y PROCESAMIENTO DE DATOS DESDE JSON
##############################################################################
@st.cache_data(show_spinner=False)
def load_data(json_file="data.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    contract_rows = []
    invoice_rows = []

    for c in data:
        # Renombramos "tipo" a "contrato" para mayor claridad
        contrato_nombre = c.get("tipo", "Desconocido")
        centro = c.get("centro", "Desconocido")
        fecha_firma = c.get("fecha_firma", "N/D")
        fecha_vencimiento = c.get("fecha_vencimiento", "N/D")

        monthly_totals = {}
        for factura in c.get("facturas", []):
            fecha_str = factura.get("fecha")
            total_str = factura.get("total")
            consumo_total = factura.get("consumo total", 0)
            if fecha_str and total_str:
                try:
                    total = float(total_str)
                except Exception:
                    total = 0.0
                try:
                    fecha = pd.to_datetime(fecha_str, format="%d/%m/%Y")
                    month_str = fecha.strftime("%Y-%m")
                except Exception:
                    month_str = None

                if month_str:
                    monthly_totals[month_str] = monthly_totals.get(month_str, 0) + total

                invoice_rows.append({
                    "contrato": contrato_nombre,
                    "centro": centro,
                    "fecha": fecha_str,
                    "total": total,
                    "consumo total": float(consumo_total),
                    "mes": month_str,
                    "concepto": factura.get("concepto", ""),
                    "suministro": factura.get("suministro", "").strip()
                })

        registro = {
            "contrato": contrato_nombre,
            "centro": centro,
            "fecha_firma": fecha_firma,
            "fecha_vencimiento": fecha_vencimiento
        }
        registro.update(monthly_totals)
        registro["Total Anual"] = sum(monthly_totals.values())
        contract_rows.append(registro)

    contracts_df = pd.DataFrame(contract_rows)
    invoices_df = pd.DataFrame(invoice_rows)

    if not invoices_df.empty:
        invoices_df["year"] = invoices_df["mes"].apply(lambda x: x.split("-")[0] if isinstance(x, str) and "-" in x else None)

    return contracts_df, invoices_df

contracts_df, invoices_df = load_data("data.json")

# Asumimos que solo existe un centro y lo extraemos
unique_center = contracts_df["centro"].unique()[0]

##############################################################################
# MENÚ LATERAL: SELECCIÓN DE MODO
##############################################################################
view_mode = st.sidebar.radio(
    "Selecciona la sección:",
    options=["Gastos", "Consumos", "Contratos"],
    index=0
)

##############################################################################
# MODO 1: GASTOS
##############################################################################
if view_mode == "Gastos":
    st.markdown("<h1 style='font-size:30px;'>Dashboard de Gastos por Contrato</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:24px;'>Filtra por contrato y año.</h2>", unsafe_allow_html=True)

    all_contratos = sorted(contracts_df["contrato"].unique().tolist())
    month_cols = [col for col in contracts_df.columns
                  if col not in ["contrato", "centro", "fecha_firma", "fecha_vencimiento", "Total Anual"]
                  and "-" in col]
    all_years = sorted({col.split("-")[0] for col in month_cols})

    # Selección de contratos
    if st.sidebar.checkbox("Seleccionar TODOS los contratos", value=False):
        selected_contratos = all_contratos
    else:
        selected_contratos = st.sidebar.multiselect("Selecciona Contrato(s):", options=all_contratos)

    # Filtramos utilizando el único centro disponible
    filtered_contracts = contracts_df[
        (contracts_df["contrato"].isin(selected_contratos)) &
        (contracts_df["centro"] == unique_center)
    ]

    def aggregate_by_year(df, years):
        month_cols_year = sorted([
            col for col in df.columns
            if col not in ["contrato", "centro", "fecha_firma", "fecha_vencimiento", "Total Anual"]
            and any(col.startswith(year + "-") for year in years)
        ])
        if not month_cols_year:
            return pd.DataFrame(), []
        grouped = df.groupby("contrato", as_index=False)[month_cols_year].sum()
        grouped["Total Anual"] = grouped[month_cols_year].sum(axis=1)
        # Solo se conservan filas con al menos un importe mayor a 0
        grouped = grouped[(grouped[month_cols_year] > 0).any(axis=1)]
        return grouped, month_cols_year

    if len(all_years) == 0:
        aggregated_df, months_selected = aggregate_by_year(filtered_contracts, all_years)
    else:
        # Se pueden seleccionar años en la barra lateral, pero si no se selecciona ninguno, se usan todos
        selected_years = st.sidebar.multiselect("Selecciona Año(s):", options=all_years)
        if not selected_years:
            selected_years = all_years
        aggregated_df, months_selected = aggregate_by_year(filtered_contracts, selected_years)

    st.markdown("<h2 style='font-size:24px;'>Resumen Agregado de Gastos</h2>", unsafe_allow_html=True)
    if not aggregated_df.empty:
        # Añadimos la fila "Total Mensual"
        total_row = {"contrato": "Total Mensual"}
        for col in months_selected:
            total_row[col] = aggregated_df[col].sum()
        total_row["Total Anual"] = aggregated_df["Total Anual"].sum()
        aggregated_df_total = pd.concat([aggregated_df, pd.DataFrame([total_row])], ignore_index=True)

        numeric_cols = months_selected + ["Total Anual"]
        styled_table = aggregated_df_total.style.format(custom_spanish_format, subset=numeric_cols)
        styled_table = styled_table.apply(style_totals, axis=None)
        styled_table = styled_table.apply(lambda df: highlight_max_red(df, months_selected), axis=None)
        styled_table = styled_table.set_properties(**{"text-align": "center"})
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)
    else:
        st.info("No hay datos para la combinación de filtros seleccionada.")

##############################################################################
# MODO 2: CONSUMOS (LUZ, GAS, AGUA)
##############################################################################
elif view_mode == "Consumos":
    st.markdown("<h1 style='font-size:30px;'>Análisis de Consumo y Gasto</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:24px;'>Selecciona el suministro (Luz, Gas o Agua) y el/los año(s) a analizar.</h2>", unsafe_allow_html=True)
    
    consumo_options = ["Luz", "Gas", "Agua"]
    selected_consumo = st.sidebar.radio("Selecciona el suministro a analizar:", options=consumo_options, index=0)
    
    available_years_supply = sorted(
        invoices_df[invoices_df["suministro"].str.lower() == selected_consumo.lower()]["year"].dropna().unique().tolist()
    )
    selected_years_consumo = st.sidebar.multiselect("Selecciona Año(s):", options=available_years_supply, default=[])
    
    if not selected_years_consumo:
        st.info("Seleccione al menos un año para analizar el consumo y gasto.")
    else:
        df_supply = invoices_df[
            (invoices_df["suministro"].str.lower() == selected_consumo.lower()) &
            (invoices_df["year"].isin(selected_years_consumo))
        ]
        
        # DataFrames de consumo (consumo total > 0) y gasto (total > 0)
        df_consumo = df_supply[df_supply["consumo total"] > 0]
        df_gasto = df_supply[df_supply["total"] > 0]
        
        # Agregar consumo total por centro y mes (aunque solo haya un centro)
        consumption_agg = df_consumo.groupby(["centro", "mes"])["consumo total"].sum().reset_index()
        pivot_consumo = consumption_agg.pivot(index="centro", columns="mes", values="consumo total").fillna(0)
        pivot_consumo = pivot_consumo.reindex(sorted(pivot_consumo.columns), axis=1)
        pivot_consumo["Total Anual"] = pivot_consumo.sum(axis=1)
        
        # Agregar gasto total por centro y mes
        expense_agg = df_gasto.groupby(["centro", "mes"])["total"].sum().reset_index()
        pivot_gasto = expense_agg.pivot(index="centro", columns="mes", values="total").fillna(0)
        pivot_gasto = pivot_gasto.reindex(sorted(pivot_gasto.columns), axis=1)
        pivot_gasto["Total Anual"] = pivot_gasto.sum(axis=1)
        
        # Gestión de residentes: se busca un archivo "residents.json"; si no existe, se asigna 1 por defecto.
        residents_file = "residents.json"
        if os.path.exists(residents_file):
            with open(residents_file, "r", encoding="utf-8") as f:
                residents_dict = json.load(f)
        else:
            residents_dict = {center: 1 for center in sorted(pivot_consumo.index)}
        
        st.sidebar.markdown("### Número de Residentes por Centro")
        updated_residents = {}
        for center in sorted(pivot_consumo.index):
            default_val = residents_dict.get(center, 1)
            new_val = st.sidebar.number_input(
                f"{center}", min_value=0, value=default_val, step=1
            )
            updated_residents[center] = new_val
        if st.sidebar.button("Guardar número de residentes"):
            with open(residents_file, "w", encoding="utf-8") as f:
                json.dump(updated_residents, f, indent=2, ensure_ascii=False)
            st.sidebar.success("Guardado correctamente.")
            residents_dict = updated_residents
        
        # Calcular consumo y gasto por residente
        pivot_consumo_pr = pivot_consumo.copy()
        pivot_gasto_pr = pivot_gasto.copy()
        for centro in pivot_consumo_pr.index:
            resid = residents_dict.get(centro, 1)
            if resid == 0:
                resid = 1
            pivot_consumo_pr.loc[centro] = pivot_consumo_pr.loc[centro] / resid
            pivot_gasto_pr.loc[centro] = pivot_gasto_pr.loc[centro] / resid
        
        # Mostrar tablas sin decimales (convertidos a enteros)
        st.markdown("## Consumo Total por Centro")
        st.dataframe(pivot_consumo.applymap(lambda x: int(round(x))), use_container_width=True)

        st.markdown("## Consumo por Residente por Centro")
        st.dataframe(pivot_consumo_pr.applymap(lambda x: int(round(x))), use_container_width=True)
        
        st.markdown("## Gasto Total por Centro")
        df_gasto_fmt = pivot_gasto.copy()
        for col in df_gasto_fmt.columns:
            df_gasto_fmt[col] = df_gasto_fmt[col].apply(custom_spanish_format)
        st.dataframe(df_gasto_fmt, use_container_width=True)
        
        st.markdown("## Gasto por Residente por Centro")
        df_gasto_pr_fmt = pivot_gasto_pr.copy()
        for col in df_gasto_pr_fmt.columns:
            df_gasto_pr_fmt[col] = df_gasto_pr_fmt[col].apply(custom_spanish_format)
        st.dataframe(df_gasto_pr_fmt, use_container_width=True)
        
        # Gráfico: Consumo por residente (excluyendo la columna "Total Anual")
        month_cols_consumo = [col for col in pivot_consumo_pr.columns if col != "Total Anual"]
        if month_cols_consumo:
            melt_df = pivot_consumo_pr.reset_index().melt(
                id_vars="centro", value_vars=month_cols_consumo,
                var_name="Mes", value_name="Consumo por residente"
            )
            melt_df["Consumo por residente"] = melt_df["Consumo por residente"].apply(lambda x: int(round(x)))
            fig = px.bar(
                melt_df, x="Mes", y="Consumo por residente", color="centro", barmode="group",
                title=f"Consumo por Residente - {selected_consumo} ({', '.join(selected_years_consumo)})"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos mensuales para graficar.")

##############################################################################
# MODO 3: CONTRATOS
##############################################################################
elif view_mode == "Contratos":
    st.markdown("<h1 style='font-size:30px;'>Información de Contratos</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:24px;'>Se muestra la información del único centro: </h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:20px;'>{unique_center}</h3>", unsafe_allow_html=True)

    df_center = contracts_df[contracts_df["centro"] == unique_center]
    if df_center.empty:
        st.info("No hay contratos para este centro.")
    else:
        contract_options = [f"{row['contrato']} ({row['centro']})" for _, row in df_center.iterrows()]
        selected_contract = st.sidebar.selectbox("Selecciona un Contrato:", options=["-- Selecciona un contrato --"] + contract_options)
        if selected_contract != "-- Selecciona un contrato --":
            idx = contract_options.index(selected_contract)
            contract_record = df_center.iloc[idx]
            # Extraer columnas de importes (meses)
            importes = contract_record.filter(regex=r'^\d{4}-\d{2}$').dropna()
            importes = importes[importes != 0]
            importes = importes.sort_index()
            total_anual = contract_record.get("Total Anual", 0)
            
            st.markdown("<h2 style='font-size:24px;'>Importes Mensuales y Total Anual</h2>", unsafe_allow_html=True)
            if not importes.empty:
                df_importes = pd.DataFrame({"Mes": importes.index, "Importe": importes.values}).reset_index(drop=True)
                total_row_df = pd.DataFrame({"Mes": ["Total Anual"], "Importe": [total_anual]})
                df_importes = pd.concat([df_importes, total_row_df], ignore_index=True)
                df_importes["Importe"] = df_importes["Importe"].apply(custom_spanish_format)
                st.dataframe(df_importes, use_container_width=True)
            else:
                st.info("No hay importes mensuales para este contrato.")

            st.markdown("<h2 style='font-size:24px;'>Datos Generales del Contrato</h2>", unsafe_allow_html=True)
            # Excluir columnas de importes y "Total Anual"
            cols_generales = [col for col in contract_record.index if not pd.Series(col).str.match(r'^\d{4}-\d{2}$').any() and col != "Total Anual"]
            general_info = contract_record[cols_generales].to_dict()
            general_df = pd.DataFrame(list(general_info.items()), columns=["Campo", "Valor"])
            st.table(general_df)
    else:
        st.info("No hay contratos disponibles para el centro seleccionado.")