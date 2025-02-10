import streamlit as st
import math
from decimal import Decimal
from datetime import date

# ---------------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------------------------
def calcular_equivalentes_jornada_completa(horas_semanales):
    """Convierte horas semanales en EJC (Equivalentes de Jornada Completa),
    asumiendo 1772 horas/año y ~52.14 semanas/año."""
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def formatear_ratio(valor):
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    # Usa "," como separador decimal
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

def si_cumple_texto(cumple: bool) -> str:
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

# --- REQUISITOS CAM ---
def calcular_horas_gerocultores_cam(usuarios_cam):
    """
    Calcula las horas mínimas requeridas para Gerocultores según normativa CAM:
      225 horas semanales por cada 35 usuarios o fracción.
    """
    bloques_completos = usuarios_cam // 35
    resto = usuarios_cam % 35
    horas_totales = bloques_completos * 225 + (resto / 35) * 225
    return horas_totales

def calcular_ratio_cam(usuarios_cam, horas_dict, sumar_ruta=False):
    """
    Devuelve:
      - ratio_directa (EJC/usuario)
      - si_cumple_ratio (bool) => >= 0,23
      - horas_gero (float) = total horas de Gerocultor (con o sin auxiliar de ruta)
      - horas_min_gero (float) = horas mínimas exigidas
      - si_cumple_gero (bool)

    :param sumar_ruta: Si True, se suman las horas de "Gerocultor (aux. ruta)" a las de "Gerocultor".
    """
    # 1) Ratio global 0,23 EJC/usuario
    #    (Enfermero, Gerocultor, Fisio, TO, Trabajador Social, Psicólogo)
    total_ejc_directa = 0.0
    for cat in ["Enfermera/o", "Gerocultor", "Fisioterapeuta", "Terapeuta Ocupacional",
                "Trabajador Social", "Psicólogo/a"]:
        h_sem = horas_dict.get(cat, 0.0)
        total_ejc_directa += calcular_equivalentes_jornada_completa(h_sem)

    ratio_directa = total_ejc_directa / usuarios_cam if usuarios_cam > 0 else 0
    cumple_ratio = ratio_directa >= 0.23

    # 2) Horas mínimas gerocultores CAM
    horas_min_gero = calcular_horas_gerocultores_cam(usuarios_cam)

    # Por si necesitamos sumar "Gerocultor (aux. ruta)"
    if sumar_ruta:
        horas_gero = horas_dict.get("Gerocultor", 0.0) + horas_dict.get("Gerocultor (aux. ruta)", 0.0)
    else:
        horas_gero = horas_dict.get("Gerocultor", 0.0)

    cumple_gero = horas_gero >= horas_min_gero

    return ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero

# --- REQUISITOS AYUNTAMIENTO ---
def calcular_minimos_ayuntamiento(usuarios_ayto):
    """
    Calcula las horas mínimas requeridas POR CATEGORÍA, de forma proporcional
    a los bloques de 30 usuarios o fracción.
    Por ejemplo, si se requieren 20 h/sem por cada 30 usuarios,
    para 75 usuarios => 2 bloques completos (60 usuarios) + 15 restantes.
    Horas totales = 2*20 + (15/30)*20 = 40 + 10 = 50.
    """
    # Horas requeridas POR CADA 30 usuarios:
    base_requisitos = {
        "Coordinador/a": 15,
        "Enfermera/o": 10,
        "Trabajador Social": 10,
        "Fisioterapeuta": 20,
        "Terapeuta Ocupacional": 20,
        "Psicólogo/a": 10,
        "Gerocultor": 136,               # 4 EJC ~ 136 h/sem por cada 30 usuarios
        "Gerocultor (aux. ruta)": 30,
        "Conductor/a": 30
    }

    if usuarios_ayto <= 0:
        # Devuelve todo en 0
        return {cat: 0.0 for cat in base_requisitos.keys()}

    blocks_completos = usuarios_ayto // 30
    resto = usuarios_ayto % 30
    fraccion = resto / 30.0  # parte fraccionada

    minimos = {}
    for categoria, horas_por_bloque in base_requisitos.items():
        horas_totales = (blocks_completos * horas_por_bloque) + (fraccion * horas_por_bloque)
        minimos[categoria] = horas_totales
    return minimos

def comprobar_cumplimiento_ayuntamiento(usuarios_ayto, horas_dict):
    """
    Devuelve un dict con la comparación (cumple o no) de cada categoría
    vs. las horas mínimas exigidas por Ayuntamiento, calculadas proporcionalmente.
    """
    req = calcular_minimos_ayuntamiento(usuarios_ayto)  # usa cálculo proporcional
    resultado = {}
    for categoria, horas_minimas in req.items():
        horas_aportadas = horas_dict.get(categoria, 0.0)
        cumple = horas_aportadas >= horas_minimas
        resultado[categoria] = {
            "requerido": horas_minimas,
            "aportado": horas_aportadas,
            "cumple": cumple
        }
    return resultado

# ---------------------------------------------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------------------------------------------
st.title("Ádrika - 📊 Cálculo de RATIO de personal - Centros de Día")
st.write("Calcule la ratio de personal según normativa CAM y/o Ayuntamiento (Madrid).")

opcion_tipo = st.selectbox(
    "¿El centro cuenta con plazas concertadas con...?",
    ["CAM", "Ayuntamiento", "Ambos"],
    index=0
)

# -------------------------------------------------------------------------
# Opción SOLO CAM
# -------------------------------------------------------------------------
if opcion_tipo == "CAM":
    st.subheader("🏥 Plazas CAM")
    usuarios_cam = st.number_input("Nº de usuarios (plazas ocupadas CAM)", min_value=0, value=0, step=1, format="%d")

    st.markdown("### Horas semanales de **Atención Directa** (CAM)")
    categorias_cam = [
        "Enfermera/o",
        "Gerocultor",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Trabajador Social",
        "Psicólogo/a"
    ]
    horas_cam = {}
    for cat in categorias_cam:
        horas_cam[cat] = st.number_input(
            f"{cat} (h/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"cam_{cat}"
        )
    
    if st.button("📌 Calcular Ratio"):
        if usuarios_cam == 0:
            st.error("⚠️ Debe introducir un número de usuarios CAM mayor que 0.")
            st.stop()

        # Cálculo CAM
        ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero = calcular_ratio_cam(usuarios_cam, horas_cam)
        
        # Mostramos resultados
        st.subheader("📊 Resultados CAM")
        st.markdown(f"""
        <p style='font-size:18px; color:{"green" if cumple_ratio else "red"};'>
            🔹 <b>Ratio de Atención Directa</b>: {formatear_ratio(ratio_directa)} (mínimo 0,23) 
            → {si_cumple_texto(cumple_ratio)}
        </p>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <p style='font-size:18px; color:{"green" if cumple_gero else "red"};'>
            🔹 <b>Horas de Gerocultores</b>: {horas_gero:.2f} h/semana (mínimo: {horas_min_gero:.2f}) 
            → {si_cumple_texto(cumple_gero)}
        </p>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# Opción SOLO AYUNTAMIENTO
# -------------------------------------------------------------------------
elif opcion_tipo == "Ayuntamiento":
    st.subheader("🏥 Plazas Ayuntamiento")
    usuarios_ayto = st.number_input("Nº de usuarios (plazas ocupadas Ayuntamiento)", min_value=0, value=0, step=1, format="%d")

    # Categorías Ayuntamiento
    categorias_ayto = [
        "Coordinador/a",
        "Enfermera/o",
        "Trabajador Social",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Psicólogo/a",
        "Gerocultor",  
        "Gerocultor (aux. ruta)",
        "Conductor/a"
    ]
    horas_ayto = {}
    st.markdown("### Horas semanales según categorías (Ayuntamiento)")
    for cat in categorias_ayto:
        horas_ayto[cat] = st.number_input(
            f"{cat} (h/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"ayto_{cat}"
        )
    
    if st.button("📌 Calcular Ratio"):
        if usuarios_ayto == 0:
            st.error("⚠️ Debe introducir un número de usuarios (Ayuntamiento) mayor que 0.")
            st.stop()
        
        # Comprobamos cumplimiento
        resultados_ayto = comprobar_cumplimiento_ayuntamiento(usuarios_ayto, horas_ayto)
        
        st.subheader("📊 Resultados Ayuntamiento")
        
        for cat, data_cat in resultados_ayto.items():
            cumple_txt = si_cumple_texto(data_cat["cumple"])
            color = "green" if data_cat["cumple"] else "red"
            st.markdown(f"""
            <p style='font-size:16px; color:{color};'>
                🔹 <b>{cat}</b>: {data_cat["aportado"]:.2f} h/sem 
                (mínimo: {data_cat["requerido"]:.2f}) → {cumple_txt}
            </p>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# Opción AMBOS
# -------------------------------------------------------------------------
else:
    st.subheader("🏥 Plazas CAM y Ayuntamiento")
    usuarios_totales = st.number_input(
        "Nº de usuarios (plazas ocupadas totales del centro)",
        min_value=0, value=0, step=1, format="%d"
    )
    
    st.markdown("""
    **Nota**: Con esta opción se aplicará el **mismo número de usuarios** 
    tanto para la normativa CAM como para la del Ayuntamiento.

    **Además**, para la normativa CAM se **sumarán** las horas de **Gerocultor** 
    y **Gerocultor (aux. ruta)** al calcular las horas de Gerocultores.
    """)

    # Mostramos todas las categorías en un único bloque de inputs
    categorias_todas = [
        "Enfermera/o",
        "Gerocultor",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Trabajador Social",
        "Psicólogo/a",
        "Coordinador/a",               # solo AYTO
        "Gerocultor (aux. ruta)",      # solo AYTO
        "Conductor/a"                  # solo AYTO
    ]
    horas_centro = {}
    st.markdown("### Horas semanales - Personal total del Centro")
    for cat in categorias_todas:
        horas_centro[cat] = st.number_input(
            f"{cat} (h/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"ambos_{cat}"
        )

    if st.button("📌 Calcular Ratio"):
        if usuarios_totales == 0:
            st.error("⚠️ Debe introducir un número de usuarios mayor que 0.")
            st.stop()

        # --- Cálculo CAM (sumando gerocultor ruta) ---
        ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero = (
            calcular_ratio_cam(usuarios_totales, horas_centro, sumar_ruta=True)
        )
        
        st.subheader("📊 Resultados CAM")
        st.markdown(f"""
        <p style='font-size:18px; color:{"green" if cumple_ratio else "red"};'>
            🔹 <b>Ratio de Atención Directa</b>: {formatear_ratio(ratio_directa)} 
            (mínimo 0,23) → {si_cumple_texto(cumple_ratio)}
        </p>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <p style='font-size:18px; color:{"green" if cumple_gero else "red"};'>
            🔹 <b>Horas de Gerocultores (CAM)</b>: {horas_gero:.2f} h/sem 
            (mínimo: {horas_min_gero:.2f}) → {si_cumple_texto(cumple_gero)}
        </p>
        """, unsafe_allow_html=True)

        # --- Cálculo Ayuntamiento (proporcional) ---
        resultados_ayto = comprobar_cumplimiento_ayuntamiento(usuarios_totales, horas_centro)
        
        st.subheader("📊 Resultados Ayuntamiento")
        for cat, data_cat in resultados_ayto.items():
            cumple_txt = si_cumple_texto(data_cat["cumple"])
            color = "green" if data_cat["cumple"] else "red"
            st.markdown(f"""
            <p style='font-size:16px; color:{color};'>
                🔹 <b>{cat}</b>: {data_cat["aportado"]:.2f} h/sem 
                (mínimo: {data_cat["requerido"]:.2f}) → {cumple_txt}
            </p>
            """, unsafe_allow_html=True)