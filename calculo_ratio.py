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
    """
    Calcula las horas necesarias de fisioterapia y terapia ocupacional según las plazas ocupadas.
    """
    base_horas_diarias = 4  # 4 horas diarias para los primeros 50 residentes
    dias_semana = 5  # De lunes a viernes
    horas_totales = base_horas_diarias * dias_semana  # Horas para los primeros 50 residentes

    if plazas > 50:
        plazas_adicionales = plazas - 50
        # Incremento de 2 horas diarias por cada 25 plazas adicionales o fracción
        incrementos = (plazas_adicionales + 24) // 25  # Redondeo hacia arriba
        horas_adicionales_diarias = incrementos * 2
        horas_totales += horas_adicionales_diarias * dias_semana

    return horas_totales

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
    st.write("- **Atención médica**: Presencia física de lunes a viernes y localizable los fines de semana, preferiblemente por un médico geriatra.")
    st.write("- **Cuidados de enfermería**: Obligatorio con presencia física de lunes a domingo, garantizando el servicio continuo y permanente.")
    st.write("- **Gerocultores**: Plantilla integrada por profesionales con la formación requerida, con la frecuencia y calidad exigida, todos los días del año, garantizándose el carácter continuo y permanente del servicio de lunes a domingo.")
