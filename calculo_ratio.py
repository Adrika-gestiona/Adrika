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

st.title("Ádrika - 📊 Cálculo de Ratio de Personal - CAM")
st.write("**Ingrese las horas semanales de cada categoría para calcular la ratio de personal.**")

# Ingreso de ocupación al principio
st.subheader("🏥 Ocupación de la Residencia")
ocupacion = st.number_input("Ingrese el número de residentes", min_value=1, format="%.0f")

# Crear los campos de entrada de horas semanales
datos_directas = {}
datos_no_directas = {}

st.subheader("🔹 Horas semanales de Atención Directa")
for categoria in directas:
    datos_directas[categoria] = st.number_input(f"{categoria} (horas/semana)", min_value=0.0, format="%.2f")

st.subheader("🔹 Horas semanales de Atención No Directa")
for categoria in no_directas:
    datos_no_directas[categoria] = st.number_input(f"{categoria} (horas/semana)", min_value=0.0, format="%.2f")

if st.button("📌 Calcular Ratio"):
    # Calcular equivalentes a jornada completa
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_directas.values())
    total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_no_directas.values())
    
    # Calcular ratios
    ratio_directa = (total_eq_directa / ocupacion) * 100
    ratio_no_directa = (total_eq_no_directa / ocupacion) * 100
    
    # Mostrar resultados
    st.subheader("📊 Resultados del Cálculo de Ratios")
    st.markdown(f"<p style='font-size:18px;'>🔹 <b>Atención Directa</b> → Total EQ: <b>{total_eq_directa:.2f}</b> | Ratio: <b>{ratio_directa:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px;'>🔹 <b>Atención No Directa</b> → Total EQ: <b>{total_eq_no_directa:.2f}</b> | Ratio: <b>{ratio_no_directa:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)
    
    # Verificación de cumplimiento
    cumple_directa = ratio_directa / 100 >= 0.47
    cumple_no_directa = ratio_no_directa / 100 >= 0.15
    cumple_gerocultores = (calcular_equivalentes_jornada_completa(datos_directas.get("Gerocultor", 0)) / ocupacion) >= 0.33
    
    st.subheader("✅ Verificación de cumplimiento con la CAM")
    st.markdown(f"<p style='font-size:18px;'>- <b>Atención Directa</b>: {'✅ CUMPLE' if cumple_directa else '❌ NO CUMPLE'} (Mínimo 0,47). Ratio: <b>{ratio_directa / 100:.2f}</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px;'>- <b>Atención No Directa</b>: {'✅ CUMPLE' if cumple_no_directa else '❌ NO CUMPLE'} (Mínimo 0,15). Ratio: <b>{ratio_no_directa / 100:.2f}</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px;'>- <b>Gerocultores</b>: {'✅ CUMPLE' if cumple_gerocultores else '❌ NO CUMPLE'} (Mínimo 0,33). Ratio: <b>{(calcular_equivalentes_jornada_completa(datos_directas.get('Gerocultor', 0)) / ocupacion):.2f}</b></p>", unsafe_allow_html=True)
    
    # Resumen de ratios por categoría
    st.subheader("📋 Resumen de Ratios por Categoría")
    for categoria, horas in datos_directas.items():
        ratio_categoria = (calcular_equivalentes_jornada_completa(horas) / ocupacion) * 100
        st.markdown(f"<p style='font-size:18px;'>🔹 <b>{categoria}</b> → Ratio: <b>{ratio_categoria:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)
    for categoria, horas in datos_no_directas.items():
        ratio_categoria = (calcular_equivalentes_jornada_completa(horas) / ocupacion) * 100
        st.markdown(f"<p style='font-size:18px;'>🔹 <b>{categoria}</b> → Ratio: <b>{ratio_categoria:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)