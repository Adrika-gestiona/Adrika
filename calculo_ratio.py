import streamlit as st
import math
from decimal import Decimal

# ---------------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------------------------

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

    - Para hasta 50 residentes: 4 horas diarias (lunes a viernes) = 20 h/semana.
    - A partir de ahí, por cada 25 residentes adicionales (o fracción),
      se añaden 2 horas diarias (10 h/semana). Permite incrementos parciales.
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
    Maneja también infinito, NaN o None.
    """
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

# ---------------------------------------------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------------------------------------------

st.title("Ádrika - 📊 Cálculo de RATIO de personal - CAM")

# NUEVO: Seleccionamos el modo de cálculo
modo_calculo = st.selectbox(
    "Seleccione el tipo de cálculo que desea realizar:",
    [
        "Cálculo RATIO CAM AM atención residencial", 
        "Cálculo RATIO CAM Orden 2680-2024 Acreditación de centros"
    ]
)

# Sección: Ocupación de la Residencia
st.subheader("🏥 Ocupación de la Residencia")
ocupacion = st.number_input(
    "Ingrese el número de residentes (plazas ocupadas o autorizadas)",
    min_value=0,  # Por defecto 0
    value=0,
    step=1,
    format="%d"
)

# ---------------------------------------------------------------------------------------------
# MODO 1: CÁLCULO RATIO CAM AM ATENCIÓN RESIDENCIAL (lógica original)
# ---------------------------------------------------------------------------------------------
if modo_calculo == "Cálculo RATIO CAM AM atención residencial":
    st.write("**Se encuentra en el modo de cálculo según normativa CAM AM (Atención Residencial).**")

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
    if st.button("📌 Calcular Ratio (CAM AM)"):

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
        # - Trabajador Social: obligado a tener alguna hora (>0).
        horas_ts = datos_directas.get("Trabajador Social", 0)
        cumple_ts = (horas_ts > 0)

        # - Médico: al menos 5h/sem (presencia L-V).
        horas_medico = datos_directas.get("Médico", 0)
        cumple_medico = (horas_medico >= 5)

        # - Enfermería: mínimo 168h/sem para cubrir 24h/día x 7 días.
        horas_enfermeria = datos_directas.get("ATS/DUE (Enfermería)", 0)
        cumple_enfermeria = (horas_enfermeria >= 168)

        st.subheader("🔎 Verificación de requisitos específicos")
        # Trabajador Social
        st.markdown(f"""
        <p style='font-size:16px; color:{"green" if cumple_ts else "red"};'>
            🔹 <b>Trabajador Social</b>: Contratación obligatoria.
            Horas: <b>{formatear_ratio(horas_ts)}</b> → 
            {"✅ CUMPLE" if cumple_ts else "❌ NO CUMPLE (debe ser > 0)"}
        </p>
        """, unsafe_allow_html=True)

        # Médico
        st.markdown(f"""
        <p style='font-size:16px; color:{"green" if cumple_medico else "red"};'>
            🔹 <b>Médico</b>: Presencia de lunes a viernes (≥5h/sem).
            Horas: <b>{formatear_ratio(horas_medico)}</b> → 
            {"✅ CUMPLE (si hubo presencia L-V)" if cumple_medico else "❌ NO CUMPLE (debe ser ≥ 5h)"}
        </p>
        """, unsafe_allow_html=True)

        # Enfermería
        st.markdown(f"""
        <p style='font-size:16px; color:{"green" if cumple_enfermeria else "red"};'>
            🔹 <b>Enfermería (ATS/DUE)</b>: 
            Presencia 24h/día, 7 días/semana (≥168h/sem).
            Horas: <b>{formatear_ratio(horas_enfermeria)}</b> → 
            {"✅ CUMPLE (24h/día cubiertas)" if cumple_enfermeria else "❌ NO CUMPLE (debe ser ≥ 168h)"}
        </p>
        """, unsafe_allow_html=True)

        # 7) Información adicional final
        st.subheader("ℹ️ Información sobre las ratios")
        st.write("- **Atención Directa**: Mínimo de 0,47 (EJC) por residente.")
        st.write("- **Gerocultores**: Mínimo de 0,33 (EJC) por residente.")
        st.write("- **Fisioterapeuta / Terapeuta Ocupacional**: 4 horas/día (20h/sem) para 1-50 plazas, "
                 "y +2h/día (10h/sem) por cada 25 plazas o fracción.")
        st.write("- **Trabajador Social**: Contratación obligatoria (sin horas mínimas, pero > 0h).")
        st.write("- **Médico**: Presencia física L-V (indicativo ≥5h/sem).")
        st.write("- **Enfermería**: Presencia 24h/día, 7 días/semana (≥168h/sem).")
        st.write("- **Psicólogo/a y Animador Sociocultural**: Servicios opcionales.")
        st.write("- **Atención No Directa**: Mínimo de 0,15 (EJC) por residente.")


# ---------------------------------------------------------------------------------------------
# MODO 2: CÁLCULO RATIO CAM Orden 2680-2024 Acreditación de centros (solo atención directa)
# ---------------------------------------------------------------------------------------------
else:
    st.write("**Se encuentra en el modo de cálculo según la Orden 2680-2024 (Acreditación de centros).**")
    st.write("Para residencias de personas mayores, la ratio mínima de personal de atención directa es:")
    st.markdown("- **0,45** si la residencia tiene más de 50 plazas autorizadas.\n"
                "- **0,37** si la residencia tiene 50 o menos plazas autorizadas.")

    # Solo pedimos horas de Atención Directa
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

    datos_directas = {}

    st.subheader("🔹 Horas semanales de Atención Directa (Orden 2680-2024)")
    for categoria in directas:
        datos_directas[categoria] = st.number_input(
            f"{categoria} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_2_{categoria}"
        )

    if st.button("📌 Calcular Ratio (Orden 2680-2024)"):

        if ocupacion == 0:
            st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
            st.stop()

        # Calculamos la suma total de EJC en atención directa
        total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in datos_directas.values())
        ratio_directa = total_eq_directa / ocupacion  # EJC por residente

        # Determinamos la ratio mínima a aplicar (≥0,45 si >50, sino ≥0,37)
        if ocupacion > 50:
            ratio_minima = 0.45
        else:
            ratio_minima = 0.37

        st.subheader("📊 Resultado del Cálculo de Ratio (Atención Directa)")
        st.write(f"**Total de EJC de Atención Directa**: {total_eq_directa:.2f}")
        st.write(f"**Ratio de Atención Directa** (EJC por residente): {ratio_directa:.2f}")

        cumple_ratio = ratio_directa >= ratio_minima
        color_ratio = "green" if cumple_ratio else "red"

        st.markdown(f"""
        <p style='font-size:18px; color:{color_ratio};'>
            - Ratio mínima exigida: <b>{ratio_minima:.2f}</b><br>
            - El centro {"<b>CUMPLE ✅</b>" if cumple_ratio else "<b>NO CUMPLE ❌</b>"}
        </p>
        """, unsafe_allow_html=True)

        st.info(
            "Esta verificación se basa únicamente en la ratio global de personal de atención directa. "
            "Pueden existir otros requisitos cualitativos (distribución de categorías, turnos, etc.) "
            "contemplados en la Orden 2680-2024."
        )
