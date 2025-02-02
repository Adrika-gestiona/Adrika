import streamlit as st

def calcular_equivalentes_jornada_completa(horas_semanales):
    """
    Convierte las horas semanales en equivalentes a jornada completa.
    """
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

# Definir las categorías de personal
directas = [
    "Médico", "ATS/DUE (Enfermería)", "Gerocultor", "Fisioterapeuta", "Terapeuta Ocupacional",
    "Trabajador Social", "Psicólogo/a", "Animador sociocultural / TASOC", "Director/a"
]

no_directas = ["Limpieza", "Cocina", "Mantenimiento"]

st.title("📊 Cálculo de Ratio de Personal - Comunidad de Madrid")
st.write("Ingrese las horas semanales de cada categoría para calcular la ratio de personal.")

# Crear los campos de entrada de horas semanales
datos_directas = {}
datos_no_directas = {}

st.subheader("🔹 Horas semanales de Atención Directa")
for categoria in directas:
    datos_directas[categoria] = st.number_input(f"{categoria} (horas/semana)", min_value=0.0, format="%.2f")

st.subheader("🔹 Horas semanales de Atención No Directa")
for categoria in no_directas:
    datos_no_directas[categoria] = st.number_input(f"{categoria} (horas/semana)", min_value=0.0, format="%.2f")

# Ingreso de ocupación
st.subheader("🏥 Ocupación de la Residencia")
ocupacion = st.number_input("Ingrese el número de residentes", min_value=1, format="%.0f")

if st.button("📌 Calcular Ratio"):
    # Calcular equivalentes a jornada completa
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_directas.values())
    total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_no_directas.values())
    
    # Calcular ratios
    ratio_directa = (total_eq_directa / ocupacion) * 100
    ratio_no_directa = (total_eq_no_directa / ocupacion) * 100
    
    # Mostrar resultados
    st.subheader("📊 Resultados del Cálculo de Ratios")
    st.write(f"🔹 **Atención Directa** → Total EQ: `{total_eq_directa:.2f}` | Ratio: `{ratio_directa:.2f}` por cada 100 residentes")
    st.write(f"🔹 **Atención No Directa** → Total EQ: `{total_eq_no_directa:.2f}` | Ratio: `{ratio_no_directa:.2f}` por cada 100 residentes")
    
    # Verificación de cumplimiento
    cumple_directa = ratio_directa / 100 >= 0.47
    cumple_no_directa = ratio_no_directa / 100 >= 0.15
    
    st.subheader("✅ Verificación de cumplimiento con la CAM")
    st.write(f"- **Atención Directa**: {'✅ CUMPLE' if cumple_directa else '❌ NO CUMPLE'} (Mínimo 0.47). Ratio: `{ratio_directa / 100:.2f}`")
    st.write(f"- **Atención No Directa**: {'✅ CUMPLE' if cumple_no_directa else '❌ NO CUMPLE'} (Mínimo 0.15). Ratio: `{ratio_no_directa / 100:.2f}`")