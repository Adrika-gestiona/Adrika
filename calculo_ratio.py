import streamlit as st

def calcular_ratio():
    st.title("Mayores.ai - Ádrika")
    st.write("Ingrese los datos para calcular la ratio de personal en su residencia.")

    # Selección del tipo de ratio a calcular
    tipo_ratio = st.radio("Seleccione el tipo de ratio a calcular:", ("Atención Directa", "Atención No Directa"))
    
    if tipo_ratio == "Atención Directa":
        st.write("Ha seleccionado calcular la ratio de Personal de Atención Directa.")

        # Entrada de datos
        st.write("Introduzca las horas semanales trabajadas por categoría de atención directa y la ocupación media de la semana.")
        usuarios = st.number_input("Número de usuarios (ocupación media)", min_value=1, step=1)
        categorias = {
            "DUE": st.number_input("Horas semanales para DUE (Enfermeros)", min_value=0.0, step=0.5),
            "Gerocultores": st.number_input("Horas semanales para Gerocultores", min_value=0.0, step=0.5),
            "Médico": st.number_input("Horas semanales para Médico", min_value=0.0, step=0.5),
            "Fisioterapeuta": st.number_input("Horas semanales para Fisioterapeuta", min_value=0.0, step=0.5),
            "Terapeuta Ocupacional": st.number_input("Horas semanales para Terapeuta Ocupacional", min_value=0.0, step=0.5),
            "Trabajador Social": st.number_input("Horas semanales para Trabajador Social", min_value=0.0, step=0.5),
            "TASOC": st.number_input("Horas semanales para TASOC (Animador Sociocultural)", min_value=0.0, step=0.5),
            "Psicólogo": st.number_input("Horas semanales para Psicólogo", min_value=0.0, step=0.5),
            "Director": st.number_input("Horas semanales para Director", min_value=0.0, step=0.5)
        }

        if st.button("Calcular Ratio de Atención Directa"):
            # Ajustar horas de fisioterapeuta y terapeuta ocupacional
            if usuarios <= 50:
                categorias["Fisioterapeuta"] = 4 * 5  # 4 horas diarias de L-V
                categorias["Terapeuta Ocupacional"] = 4 * 5
            else:
                incremento = ((usuarios - 50) // 25 + 1) * 2 * 5
                categorias["Fisioterapeuta"] += incremento
                categorias["Terapeuta Ocupacional"] += incremento

            # Cálculo de horas anuales y plantilla equivalente
            horas_anuales_totales = sum(horas * 52.14 for horas in categorias.values())
            plantilla_equivalente = horas_anuales_totales / 1772
            ratio = plantilla_equivalente / usuarios

            # Ratios específicas
            ratio_gerocultores = (categorias["Gerocultores"] * 52.14 / 1772) / usuarios

            # Mostrar resultados
            st.success(f"Total de horas anuales: {horas_anuales_totales:.2f} horas")
            st.success(f"Plantilla equivalente anual: {plantilla_equivalente:.2f} trabajadores")
            st.success(f"Ratio obtenida: {ratio:.3f} ({ratio * 100:.1f} trabajadores por cada 100 residentes)")
            st.success(f"Ratio de Gerocultores: {ratio_gerocultores:.3f} ({ratio_gerocultores * 100:.1f} trabajadores por cada 100 residentes)")

            # Verificar cumplimiento de ratios
            if ratio < 0.47:
                st.error("La ratio de atención directa no cumple con el mínimo requerido de 0,47.")
            if ratio_gerocultores < 0.33:
                st.error("La ratio de gerocultores no cumple con el mínimo requerido de 0,33.")

    else:
        st.write("Ha seleccionado calcular la ratio de Personal de Atención No Directa.")
        
        # Opciones para introducir datos para atención no directa
        empleados_no_directa = st.number_input("Número total de empleados para atención no directa", min_value=0, step=1)
        horas_no_directa = st.number_input("Horas totales trabajadas por semana para atención no directa", min_value=0, step=1)
        residentes = st.number_input("Número de plazas ocupadas en la residencia", min_value=1, step=1)
        
        if st.button("Calcular Ratio de Atención No Directa"):
            horas_anuales_no_directa = horas_no_directa * 52.14
            trabajadores_equivalentes_no_directa = horas_anuales_no_directa / 1772
            ratio_no_directa = trabajadores_equivalentes_no_directa / residentes
            
            st.success(f"Total de horas presenciales para atención no directa: {horas_anuales_no_directa:.0f} horas")
            st.success(f"Trabajadores equivalentes a jornada completa: {trabajadores_equivalentes_no_directa:.2f}")
            st.success(f"Ratio obtenida: {ratio_no_directa:.3f} ({ratio_no_directa * 100:.1f} trabajadores por cada 100 residentes)")

if __name__ == "__main__":
    calcular_ratio()
