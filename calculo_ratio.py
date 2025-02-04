import streamlit as st
import math
from decimal import Decimal

def calcular_equivalentes_jornada_completa(horas_semanales):
    """
    Convierte las horas semanales en equivalentes a jornada completa.
    """
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def calcular_horas(plazas):
    """
    Calcula las HORAS SEMANALES necesarias para Fisioterapia y Terapia Ocupacional.

    - Para hasta 50 residentes: 4 horas diarias (de lunes a viernes) = 20 h/semana.
    - A partir de ahí, por cada 25 residentes adicionales (o fracción),
      se añaden 2 horas diarias (10 h/semana), permitiendo incrementos parciales
      si no se completa el siguiente bloque de 25.
    """
    dias_semana = 5
    base_horas_diarias = 4.0  # 4 horas/día para 1-50 residentes

    if plazas <= 50:
        horas_diarias = base_horas_diarias
    else:
        plazas_adicionales = plazas - 50
        incrementos_enteros = plazas_adicionales // 25
        resto = plazas_adicionales % 25
        horas_adicionales_enteras = incrementos_enteros * 2.0
        horas_adicionales_parciales = (resto / 25.0) * 2.0
        horas_diarias = base_horas_diarias + horas_adicionales_enteras + horas_adicionales_parciales

    horas_semanales = horas_diarias * dias_semana
    return horas_semanales

def formatear_ratio(valor):
    """
    Formatea un número a dos decimales y usando coma como separador decimal.
    Maneja también el caso en que 'valor' sea infinito, NaN o None.
    """
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

# ---------------------------------------------------------------------------------------------
# INTERFAZ DE STREAMLIT
# ---------------------------------------------------------------------------------------------

st.title("Ádrika - 📊 cálculo de RATIO de personal - CAM")
st.write("**Ingrese las horas semanales de cada categoría para calcular la ratio de personal.**")

# Sección: Ocupación de la Residencia
st.subheader("🏥 Ocupación de la Residencia")
ocupacion = st.number_input(
    "Ingrese el número de residentes",
    min_value=0,      # Por defecto 0, se obligará a introducir manualmente
    value=0,
    step=1,
    format="%d"
)

# Categorías de personal
directas = [
    "Médico",
    "ATS/DUE (Enfermería)",
    "Gerocultor",
    "Fisioterapeuta",
    "Terapeuta Ocupacional",
    "Trabajador Social",
    "Psicólogo/a",
    "Animador sociocultural / TASOC",
    "Director/a"
]
no_directas = ["Limpieza", "Cocina", "Mantenimiento"]

datos_directas = {}
datos_no_directas = {}

# Horas de Atención Directa
st.subheader("🔹 Horas semanales de Atención Directa")
for categoria in directas:
    datos_directas[categoria] = st.number_input(
        f"{categoria} (horas/semana)",
        min_value=0.0,
        format="%.2f",
        key=f"directas_{categoria}"
    )

# Horas de Atención No Directa
st.subheader("🔹 Horas semanales de Atención No Directa")
for categoria in no_directas:
    datos_no_directas[categoria] = st.number_input(
        f"{categoria} (horas/semana)",
        min_value=0.0,
        format="%.2f",
        key=f"nodirectas_{categoria}"
    )

# Botón para realizar el cálculo
if st.button("📌 Calcular Ratio"):

    # 1) Verificar si se ha introducido la ocupación
    if ocupacion == 0:
        st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
        st.stop()

    # 2) Calcular EJC totales de Atención Directa y No Directa
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_directas.values())
    total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_no_directas.values())

    # 3) Calcular los ratios por cada 100 residentes
    ratio_directa = (total_eq_directa / ocupacion) * 100
    ratio_no_directa = (total_eq_no_directa / ocupacion) * 100

    st.subheader("📊 Resultados del Cálculo de Ratios")
    ratio_directa_color = "green" if ratio_directa / 100 >= 0.47 else "red"
    ratio_no_directa_color = "green" if ratio_no_directa / 100 >= 0.15 else "red"

    st.markdown(f"""
    <p style='font-size:18px; color:{ratio_directa_color};'>
        🔹 <b>Atención Directa</b> → Total EQ: <b>{total_eq_directa:.2f}</b> | 
        Ratio: <b>{ratio_directa:.2f}</b> por cada 100 residentes
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style='font-size:18px; color:{ratio_no_directa_color};'>
        🔹 <b>Atención No Directa</b> → Total EQ: <b>{total_eq_no_directa:.2f}</b> | 
        Ratio: <b>{ratio_no_directa:.2f}</b> por cada 100 residentes
    </p>
    """, unsafe_allow_html=True)

    # 4) Verificación de cumplimiento global de ratios CAM
    cumple_directa = (ratio_directa / 100) >= 0.47
    cumple_no_directa = (ratio_no_directa / 100) >= 0.15

    eq_gerocultores = calcular_equivalentes_jornada_completa(datos_directas.get("Gerocultor", 0))
    ratio_gerocultores = eq_gerocultores / ocupacion
    cumple_gerocultores = ratio_gerocultores >= 0.33

    st.subheader("✅ Verificación de cumplimiento con la CAM")
    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if cumple_directa else "red"};'>
        - <b>Atención Directa</b>: {"✅ CUMPLE" if cumple_directa else "❌ NO CUMPLE"} 
        (Mínimo 0,47). Ratio: <b>{ratio_directa/100:.2f}</b>
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if cumple_no_directa else "red"};'>
        - <b>Atención No Directa</b>: {"✅ CUMPLE" if cumple_no_directa else "❌ NO CUMPLE"} 
        (Mínimo 0,15). Ratio: <b>{ratio_no_directa/100:.2f}</b>
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if cumple_gerocultores else "red"};'>
        - <b>Gerocultores</b>: {"✅ CUMPLE" if cumple_gerocultores else "❌ NO CUMPLE"} 
        (Mínimo 0,33). Ratio: <b>{ratio_gerocultores:.2f}</b>
    </p>
    """, unsafe_allow_html=True)

    # 5) Cálculo de horas Fisioterapia y Terapia Ocupacional
    horas_necesarias_terapia = calcular_horas(ocupacion)
    horas_fisio_usuario = datos_directas.get("Fisioterapeuta", 0)
    horas_to_usuario = datos_directas.get("Terapeuta Ocupacional", 0)

    cumple_fisio = (horas_fisio_usuario >= horas_necesarias_terapia)
    cumple_to = (horas_to_usuario >= horas_necesarias_terapia)

    st.subheader("🩺 Cálculo de horas Fisioterapia y Terapia Ocupacional")
    st.write(f"**Plazas ocupadas:** {ocupacion} residentes")

    texto_fisio = (
        f"<p style='font-size:16px; color:{'green' if cumple_fisio else 'red'};'>"
        f"🔹 <b>Fisioterapeuta</b>: Horas requeridas/semana: "
        f"<b>{formatear_ratio(horas_necesarias_terapia)}</b>. "
        f"Horas introducidas: <b>{formatear_ratio(horas_fisio_usuario)}</b> → "
        f"{'✅ CUMPLE' if cumple_fisio else '❌ NO CUMPLE'}"
        f"</p>"
    )
    st.markdown(texto_fisio, unsafe_allow_html=True)

    texto_to = (
        f"<p style='font-size:16px; color:{'green' if cumple_to else 'red'};'>"
        f"🔹 <b>Terapeuta Ocupacional</b>: Horas requeridas/semana: "
        f"<b>{formatear_ratio(horas_necesarias_terapia)}</b>. "
        f"Horas introducidas: <b>{formatear_ratio(horas_to_usuario)}</b> → "
        f"{'✅ CUMPLE' if cumple_to else '❌ NO CUMPLE'}"
        f"</p>"
    )
    st.markdown(texto_to, unsafe_allow_html=True)

    # 6) Otras comprobaciones específicas
    # - Trabajador Social: obligado a tener alguna hora (si 0 => NO CUMPLE).
    horas_ts = datos_directas.get("Trabajador Social", 0)
    cumple_ts = (horas_ts > 0)

    # - Médico: pedimos al menos 5h/sem para poder decir "presencia lunes a viernes (1h/día)".
    #   y aclaramos que "cumple siempre y cuando haya habido presencia de lunes a viernes".
    horas_medico = datos_directas.get("Médico", 0)
    cumple_medico = (horas_medico >= 5)

    # - Enfermería: mínimo 168h/semana para 24h/día x 7 días
    #   Aclaramos que "cumple siempre y cuando se haya cubierto 24h/día"
    horas_enfermeria = datos_directas.get("ATS/DUE (Enfermería)", 0)
    cumple_enfermeria = (horas_enfermeria >= 168)

    st.subheader("🔎 Verificación de requisitos específicos")
    # Trabajador Social
    st.markdown(f"""
    <p style='font-size:16px; color:{"green" if cumple_ts else "red"};'>
        🔹 <b>Trabajador Social</b>: Contratación obligatoria.
        Horas introducidas: <b>{formatear_ratio(horas_ts)}</b> → 
        {"✅ CUMPLE" if cumple_ts else "❌ NO CUMPLE (debe ser > 0)"}
    </p>
    """, unsafe_allow_html=True)

    # Médico
    # Mensaje aclarando "cumple siempre y cuando haya habido presencia lunes a viernes".
    st.markdown(f"""
    <p style='font-size:16px; color:{"green" if cumple_medico else "red"};'>
        🔹 <b>Médico</b>: Presencia de lunes a viernes (≥5h/sem).
        Horas introducidas: <b>{formatear_ratio(horas_medico)}</b> → 
        {"✅ CUMPLE (siempre y cuando haya habido presencia L-V)" if cumple_medico else "❌ NO CUMPLE (debe ser ≥ 5h)"}
    </p>
    """, unsafe_allow_html=True)

    # Enfermería
    # Mensaje aclarando "cumple siempre y cuando se haya cubierto 24h/día, 7d/sem."
    st.markdown(f"""
    <p style='font-size:16px; color:{"green" if cumple_enfermeria else "red"};'>
        🔹 <b>Enfermería (ATS/DUE)</b>: 
        Presencia 24h/día, 7 días/semana (≥168h/sem).
        Horas introducidas: <b>{formatear_ratio(horas_enfermeria)}</b> → 
        {"✅ CUMPLE (siempre y cuando se haya cubierto 24h/día, 7d/sem.)" if cumple_enfermeria else "❌ NO CUMPLE (debe ser ≥ 168h)"}
    </p>
    """, unsafe_allow_html=True)

    # 7) Información adicional final
    st.subheader("ℹ️ Información sobre las ratios")
    st.write("- **Atención Directa**: Mínimo de 0,47 (EJC) por residente.")
    st.write("- **Gerocultores**: Mínimo de 0,33 (EJC) por residente.")
    st.write("- **Fisioterapeuta y Terapeuta Ocupacional**: 4 horas/día (20h/sem) para 1-50 plazas. "
             "Por cada 25 plazas más (o fracción), +2h/día (10h/sem).")
    st.write("- **Trabajador Social**: Contratación obligatoria, sin horas mínimas específicas (pero > 0h).")
    st.write("- **Médico**: Presencia física de lunes a viernes. Se consideran ≥5h/sem para validarlo en este cálculo, "
             "pero realmente depende de turnos/horarios concretos.")
    st.write("- **Enfermería**: Presencia física 24h/día, 7 días/semana (≥168h/sem).")
    st.write("- **Psicólogo/a y Animador Sociocultural**: Servicios opcionales.")
    st.write("- **Atención No Directa**: Mínimo de 0,15 (EJC) por residente.")