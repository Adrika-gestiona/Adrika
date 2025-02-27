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