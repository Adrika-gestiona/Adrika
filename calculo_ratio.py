import streamlit as st

def calcular_ratio():
    st.title("Cálculo ratio CAM - Mayores.ai - Ádrika")
    st.write("**Ingrese los datos para calcular la ratio de personal en su residencia.**")

    # Selección del tipo de ratio a calcular
    tipo_ratio = st.radio("Seleccione el tipo de ratio a calcular:", ("**Atención Directa**", "**Atención No Directa**"))
    
    if tipo_ratio == "**Atención Directa**":
        st.write("Ha seleccionado calcular la ratio de Personal de **Atención Directa**.")

        # Entrada de datos
        st.write("**Introduzca las horas semanales trabajadas por categoría de atención directa y la ocupación media de la semana.**")
        usuarios = st.number_input("**Número de usuarios (ocupación media)**", min_value=1, step=1, format="%d")
        categorias = {
            "DUE": st.number_input("**Horas semanales para DUE (Enfermeros)**", min_value=0.0, step=0.5, format="%.1f"),
            "Gerocultores": st.number_input("**Horas semanales para Gerocultores**", min_value=0.0, step=0.5, format="%.1f"),
            "Médico": st.number_input("**Horas semanales para Médico**", min_value=0.0, step=0.5, format="%.1f"),
            "Fisioterapeuta": st.number_input("**Horas semanales para Fisioterapeuta**", min_value=0.0, step=0.5, format="%.1f"),
            "Terapeuta Ocupacional": st.number_input("**Horas semanales para Terapeuta Ocupacional**", min_value=0.0, step=0.5, format="%.1f"),
            "Trabajador Social": st.number_input("**Horas semanales para Trabajador Social**", min_value=0.0, step=0.5, format="%.1f"),
            "TASOC": st.number_input("**Horas semanales para TASOC (Animador Sociocultural)**", min_value=0.0, step=0.5, format="%.1f"),
            "Psicólogo": st.number_input("**Horas semanales para Psicólogo**", min_value=0.0, step=0.5, format="%.1f"),
            "Director": st.number_input("**Horas semanales para Director**", min_value=0.0, step=0.5, format="%.1f")
        }

        if st.button("**Calcular Ratio de Atención Directa**"):
            # Ajustar horas de fisioterapeuta y terapeuta ocupacional
            if usuarios <= 50:
                categorias["Fisioterapeuta"] = 4 * 5  # 4 horas diarias de L-V
                categorias["Terapeuta Ocupacional"] = 4 * 5
            else:
                incremento = ((usuarios - 50) // 25 + 1) * 2 * 5
                categorias["Fisioterapeuta"] += incremento
                categorias["Terapeuta Ocupacional"] += incremento

            # Filtrar categorías con horas > 0
            categorias_filtradas = {k: v for k, v in categorias.items() if v > 0}

            # Cálculo de horas anuales y plantilla equivalente
            horas_anuales_totales = sum(horas * 52.14 for horas in categorias_filtradas.values())
            plantilla_equivalente = horas_anuales_totales / 1772
            ratio = plantilla_equivalente / usuarios

            # Ratios específicas
            horas_gerocultores_anuales = categorias.get("Gerocultores", 0) * 52.14
            plantilla_gerocultores = horas_gerocultores_anuales / 1772 if horas_gerocultores_anuales > 0 else 0
            ratio_gerocultores = plantilla_gerocultores / usuarios if plantilla_gerocultores > 0 else 0

            # Si solo hay gerocultores, igualar ratios
            if len(categorias_filtradas) == 1 and "Gerocultores" in categorias_filtradas:
                ratio = ratio_gerocultores

            # Mostrar resultados
            st.success(f"Total de horas anuales: {horas_anuales_totales:.2f} horas")
            st.success(f"Plantilla equivalente anual: {plantilla_equivalente:.2f} trabajadores")
            st.success(f"Ratio obtenida: {ratio:.3f} ({ratio * 100:.1f} trabajadores por cada 100 residentes)")
            st.success(f"Ratio de Gerocultores: {ratio_gerocultores:.3f} ({ratio_gerocultores * 100:.1f} trabajadores por cada 100 residentes)")

            # Verificar cumplimiento de ratios
            cumple_directa = ratio >= 0.47
            cumple_gerocultores = ratio_gerocultores >= 0.33

            if not cumple_directa:
                st.error("La ratio de atención directa no cumple con el mínimo requerido de 0,47.")
            if not cumple_gerocultores:
                st.error("La ratio de gerocultores no cumple con el mínimo requerido de 0,33.")

            # Resumen visual
            st.subheader("Resumen del Cálculo")
            resumen = {
                "Total de horas anuales": f"{horas_anuales_totales:.2f} horas",
                "Plantilla equivalente anual": f"{plantilla_equivalente:.2f} trabajadores",
                "Ratio obtenida": f"{ratio:.3f} ({ratio * 100:.1f} por cada 100 residentes)",
                "Cumple ratio atención directa": "Sí" if cumple_directa else "No",
                "Cumple ratio gerocultores": "Sí" if cumple_gerocultores else "No",
            }
            st.table(resumen)

    else:
        st.write("Ha seleccionado calcular la ratio de Personal de **Atención No Directa**.")
        
        # Opciones para introducir datos para atención no directa
        st.write("**Introduzca las horas semanales trabajadas por categoría de atención no directa.**")
        residentes = st.number_input("**Número de plazas ocupadas en la residencia**", min_value=1, step=1, format="%d")
        categorias_no_directa = {
            "Limpieza": st.number_input("**Horas semanales para Limpieza**", min_value=0.0, step=0.5, format="%.1f"),
            "Cocina": st.number_input("**Horas semanales para Cocina**", min_value=0.0, step=0.5, format="%.1f"),
            "Mantenimiento": st.number_input("**Horas semanales para Mantenimiento**", min_value=0.0, step=0.5, format="%.1f")
        }

        if st.button("**Calcular Ratio de Atención No Directa**"):
            # Filtrar categorías con horas > 0
            categorias_no_directa_filtradas = {k: v for k, v in categorias_no_directa.items() if v > 0}

            # Cálculo de horas anuales y plantilla equivalente
            horas_anuales_totales_no_directa = sum(horas * 52.14 for horas in categorias_no_directa_filtradas.values())
            plantilla_equivalente_no_directa = horas_anuales_totales_no_directa / 1772
            ratio_no_directa = plantilla_equivalente_no_directa / residentes

            # Mostrar resultados
            st.success(f"Total de horas anuales para atención no directa: {horas_anuales_totales_no_directa:.2f} horas")
            st.success(f"Plantilla equivalente anual para atención no directa: {plantilla_equivalente_no_directa:.2f} trabajadores")
            st.success(f"Ratio obtenida: {ratio_no_directa:.3f} ({ratio_no_directa * 100:.1f} trabajadores por cada 100 residentes)")

            # Verificar cumplimiento de ratio mínima
            cumple_no_directa = ratio_no_directa >= 0.15

            if not cumple_no_directa:
                st.error("La ratio de atención no directa no cumple con el mínimo requerido de 0,15.")

            # Resumen visual
            st.subheader("Resumen del Cálculo")
            resumen_no_directa = {
                "Total de horas anuales": f"{horas_anuales_totales_no_directa:.2f} horas",
                "Plantilla equivalente anual": f"{plantilla_equivalente_no_directa:.2f} trabajadores",
                "Ratio obtenida": f"{ratio_no_directa:.3f} ({ratio_no_directa * 100:.1f} por cada 100 residentes)",
                "Cumple ratio atención no directa": "Sí" if cumple_no_directa else "No",
            }
            st.table(resumen_no_directa)

if __name__ == "__main__":
    calcular_ratio()