import streamlit as st
from decimal import Decimal

def calcular_equivalentes_jornada_completa(horas_semanales):
    """
    Convierte las horas semanales en equivalentes a jornada completa.
    """
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

# Función para calcular las horas necesarias de fisioterapia y terapia ocupacional
def calcular_horas(plazas):
    base_horas = 20  # Para 1 a 50 plazas (4 horas/día x 5 días)
    if plazas > 50:
        incremento = ((plazas - 50) // 25 + 1) * 10  # 2 horas/día x 5 días por cada 25 plazas adicionales
        base_horas += incremento
    return base_horas

# Función para verificar formato de ratios
def formatear_ratio(valor):
    return f"{Decimal(valor).quantize(Decimal('0.00')).replace('.', ',')}"

# Verificación de cumplimiento de ratios
def verificar_ratios(plazas_ocupadas, horas_fisioterapia, horas_terapia, trabajador_social):
    resultados = {}

    # Calcular horas requeridas
    horas_necesarias = calcular_horas(plazas_ocupadas)

    # Verificar fisioterapia
    resultados['fisioterapia'] = horas_fisioterapia >= horas_necesarias

    # Verificar terapia ocupacional
    resultados['terapia_ocupacional'] = horas_terapia >= horas_necesarias

    # Verificar trabajador social
    resultados['trabajador_social'] = trabajador_social  # Solo se verifica que esté contratado

    return resultados

# Resumen de ratios (ajustando el formato para mostrar)
def generar_resumen_ratios(ratios):
    resumen = "\nResumen de Ratios:\n"
    for categoria, ratio in ratios.items():
        resumen += f"{categoria}: {formatear_ratio(ratio)}\n"
    return resumen

# Interfaz con Streamlit
st.title("Ádrika - 📊 cálculo de RATIO de personal - CAM")
st.write("**Ingrese las horas semanales de cada categoría para calcular la ratio de personal.**")

# Ingreso de ocupación al principio
st.subheader("🏥 Ocupación de la Residencia")
ocupacion = st.number_input("Ingrese el número de residentes", min_value=1, format="%.0f")

# Definir las categorías de personal
directas = [
    "Médico", "ATS/DUE (Enfermería)", "Gerocultor", "Fisioterapeuta", "Terapeuta Ocupacional",
    "Trabajador Social", "Psicólogo/a", "Animador sociocultural / TASOC", "Director/a"
]

no_directas = ["Limpieza", "Cocina", "Mantenimiento"]

datos_directas = {}
datos_no_directas = {}

st.subheader("🔹 Horas semanales de Atención Directa")
for categoria in directas:
    datos_directas[categoria] = st.number_input(f"{categoria} (horas/semana)", min_value=0.0, format="%.2f")

st.subheader("🔹 Horas semanales de Atención No Directa")
for categoria in no_directas:
    datos_no_directas[categoria] = st.number_input(f"{categoria} (horas/semana)", min_value=0.0, format="%.2f")

if st.button("📌 Calcular Ratio"):
    st.subheader("ℹ️ Información sobre las ratios")
    st.write("- **Atención Directa**: Se requiere un mínimo de 0,47.")
    st.write("- **Gerocultores**: Mínimo de 0,33 por cada residente.")
    st.write("- **Atención No Directa**: Mínimo de 0,15.")
    st.write("- **Fisioterapeuta y Terapeuta Ocupacional**: Presencia mínima de 4 horas diarias de lunes a viernes para 1-50 plazas. Por cada 25 plazas adicionales o fracción, se incrementan 2 horas diarias.")
    st.write("- **Psicólogo y Animador Sociocultural**: Servicios opcionales.")
    st.write("- **Trabajador Social**: Contratación obligatoria, sin horas mínimas específicas.")
    # Calcular equivalentes a jornada completa
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_directas.values())
    total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_no_directas.values())

    # Calcular ratios
    ratio_directa = (total_eq_directa / ocupacion) * 100
    ratio_no_directa = (total_eq_no_directa / ocupacion) * 100

    # Mostrar resultados
    st.subheader("📊 Resultados del Cálculo de Ratios")
    ratio_directa_color = "red" if ratio_directa / 100 < 0.47 else "green"
    ratio_no_directa_color = "red" if ratio_no_directa / 100 < 0.15 else "green"

    st.markdown(f"<p style='font-size:18px; color:{ratio_directa_color};'>🔹 <b>Atención Directa</b> → Total EQ: <b>{total_eq_directa:.2f}</b> | Ratio: <b>{ratio_directa:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px; color:{ratio_no_directa_color};'>🔹 <b>Atención No Directa</b> → Total EQ: <b>{total_eq_no_directa:.2f}</b> | Ratio: <b>{ratio_no_directa:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)

    # Verificación de cumplimiento
    cumple_directa = ratio_directa / 100 >= 0.47
    cumple_no_directa = ratio_no_directa / 100 >= 0.15
    cumple_gerocultores = (calcular_equivalentes_jornada_completa(datos_directas.get("Gerocultor", 0)) / ocupacion) >= 0.33
    gerocultores_color = "red" if not cumple_gerocultores else "green"

    st.subheader("✅ Verificación de cumplimiento con la CAM")
    st.markdown(f"<p style='font-size:18px; color:{'red' if not cumple_directa else 'green'};'>- <b>Atención Directa</b>: {'✅ CUMPLE' if cumple_directa else '❌ NO CUMPLE'} (Mínimo 0,47). Ratio: <b>{ratio_directa / 100:.2f}</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px; color:{'red' if not cumple_no_directa else 'green'};'>- <b>Atención No Directa</b>: {'✅ CUMPLE' if cumple_no_directa else '❌ NO CUMPLE'} (Mínimo 0,15). Ratio: <b>{ratio_no_directa / 100:.2f}</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:18px; color:{gerocultores_color};'>- <b>Gerocultores</b>: {'✅ CUMPLE' if cumple_gerocultores else '❌ NO CUMPLE'} (Mínimo 0,33). Ratio: <b>{(calcular_equivalentes_jornada_completa(datos_directas.get('Gerocultor', 0)) / ocupacion):.2f}</b></p>", unsafe_allow_html=True)

    # Resumen de ratios por categoría
    st.subheader("📋 Resumen de Ratios por Categoría")
    for categoria, horas in datos_directas.items():
        ratio_categoria = (calcular_equivalentes_jornada_completa(horas) / ocupacion) * 100
        categoria_color = "red" if ratio_categoria / 100 < 0.33 and categoria == "Gerocultor" else "green"
        st.markdown(f"<p style='font-size:18px; color:{categoria_color};'>🔹 <b>{categoria}</b> → Ratio: <b>{ratio_categoria:.2f}</b> por cada 100 residentes</p>", unsafe_allow_html=True)