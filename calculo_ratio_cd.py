import streamlit as st
import math
import base64
from decimal import Decimal
from datetime import date

# ---------------------------------------------------------------------------------------------
# 1) BRANDING Y LOGO
# ---------------------------------------------------------------------------------------------
def get_base64_image(image_path: str) -> str:
    """Lee un archivo de imagen y lo convierte a una cadena Base64 (data URI)."""
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        st.error(f"No se pudo cargar el logo desde '{image_path}': {e}")
        return None

# Suponemos que tienes "logo.png" en la misma carpeta que la app
logo_data_uri = get_base64_image("logo.png")

# Construimos el HTML del branding (si no hay logo, ponemos sólo la URL).
if logo_data_uri:
    branding_html = f"""
    <div style="text-align: center; padding: 10px; margin-bottom: 10px;">
      <a href="https://www.mayores.ai" target="_blank">
        <img src="{logo_data_uri}" style="max-width: 200px; height: auto;" alt="Logo">
      </a>
    </div>
    """
else:
    branding_html = """
    <div style="text-align: center; padding: 10px; margin-bottom: 10px; font-size: 20px; color: blue;">
      <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none;">
        www.mayores.ai
      </a>
    </div>
    """

st.markdown(branding_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------------------------
# 2) FUNCIONES DE CÁLCULO Y FORMATEO
# ---------------------------------------------------------------------------------------------
def calcular_equivalentes_jornada_completa(horas_semanales: float) -> float:
    """Convierte horas semanales en EJC, asumiendo 1772 h/año y ~52.14 sem/año."""
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def formatear_numero(valor) -> str:
    """
    Devuelve un número con 2 decimales, separador decimal = ',', 
    y separador de miles = '.' 
    Ej: 12345.678 -> '12.345,68'
    """
    if not isinstance(valor, (int, float)):
        return str(valor)
    formatted = f"{valor:,.2f}"
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

def formatear_ratio(valor) -> str:
    """Formatea un float con 2 decimales y sustituye '.' por ',' para ratios."""
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

def si_cumple_texto(cumple: bool) -> str:
    """Devuelve '✅ CUMPLE' o '❌ NO CUMPLE'."""
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

def colorear_linea(texto: str, cumple: bool) -> str:
    """
    Envuelve 'texto' en un <p> con color verde o rojo, 
    y añade en negrita la parte 'CUMPLE' o 'NO CUMPLE'.
    Uso: st.markdown(colorear_linea("...", boolCumple), unsafe_allow_html=True)
    """
    color = "green" if cumple else "red"
    return (
        f"<p style='color:{color};'>"
        f"{texto} "
        f"<span style='font-weight:bold;'>{si_cumple_texto(cumple)}</span>"
        f"</p>"
    )


# ---------------------------------------------------------------------------------------------
# 3) LÓGICA DE REQUISITOS (CAM y Ayuntamiento)
# ---------------------------------------------------------------------------------------------
def calcular_horas_gerocultores_cam(usuarios_cam: int) -> float:
    """
    Calcula las horas mínimas requeridas para Gerocultores según normativa CAM:
      225 horas semanales por cada 35 usuarios o fracción.
    """
    bloques_completos = usuarios_cam // 35
    resto = usuarios_cam % 35
    horas_totales = bloques_completos * 225 + (resto / 35) * 225
    return horas_totales

def calcular_ratio_cam(usuarios_cam: int, horas_dict: dict, sumar_ruta=False):
    """
    Devuelve:
      ratio_directa (EJC/usuario)
      si_cumple_ratio (bool) => >= 0,23
      horas_gero (float)
      horas_min_gero (float)
      si_cumple_gero (bool)

    :param sumar_ruta: Sumar "Gerocultor (aux. ruta)" a "Gerocultor".
    """
    # 1) Ratio global 0,23 EJC/usuario (Enfermero, Gerocultor, Fisio, TO, TS, Psicólogo)
    total_ejc_directa = 0.0
    for cat in ["Enfermera/o", "Gerocultor", "Fisioterapeuta", "Terapeuta Ocupacional",
                "Trabajador Social", "Psicólogo/a"]:
        horas_sem = horas_dict.get(cat, 0.0)
        total_ejc_directa += calcular_equivalentes_jornada_completa(horas_sem)

    ratio_directa = total_ejc_directa / usuarios_cam if usuarios_cam > 0 else 0
    cumple_ratio = (ratio_directa >= 0.23)

    # 2) Horas mínimas gerocultores CAM
    horas_min_gero = calcular_horas_gerocultores_cam(usuarios_cam)

    if sumar_ruta:
        horas_gero = horas_dict.get("Gerocultor", 0.0) + horas_dict.get("Gerocultor (aux. ruta)", 0.0)
    else:
        horas_gero = horas_dict.get("Gerocultor", 0.0)

    cumple_gero = (horas_gero >= horas_min_gero)

    return ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero

def calcular_minimos_ayuntamiento(usuarios_ayto: int) -> dict:
    """
    Calcula las horas mínimas requeridas POR CATEGORÍA, de forma proporcional
    a bloques de 30 usuarios o fracción.
    """
    base_requisitos = {
        "Coordinador/a": 15,
        "Enfermera/o": 10,
        "Trabajador Social": 10,
        "Fisioterapeuta": 20,
        "Terapeuta Ocupacional": 20,
        "Psicólogo/a": 10,
        "Gerocultor": 136,  # 4 EJC ~ 136 h/sem por cada 30 usuarios
        "Gerocultor (aux. ruta)": 30,
        "Conductor/a": 30
    }
    if usuarios_ayto <= 0:
        # Devuelve todo en 0
        return {cat: 0.0 for cat in base_requisitos.keys()}

    blocks_completos = usuarios_ayto // 30
    resto = usuarios_ayto % 30
    fraccion = resto / 30.0

    minimos = {}
    for categoria, horas_por_bloque in base_requisitos.items():
        horas_totales = (blocks_completos * horas_por_bloque) + (fraccion * horas_por_bloque)
        minimos[categoria] = horas_totales
    return minimos

def comprobar_cumplimiento_ayuntamiento(usuarios_ayto: int, horas_dict: dict) -> dict:
    """
    Devuelve un dict con la comparación (cumple o no) de cada categoría
    vs. las horas mínimas exigidas por Ayuntamiento, calculadas proporcionalmente.
    """
    req = calcular_minimos_ayuntamiento(usuarios_ayto)
    resultado = {}
    for categoria, horas_req in req.items():
        horas_aportadas = horas_dict.get(categoria, 0.0)
        cumple = (horas_aportadas >= horas_req)
        resultado[categoria] = {
            "requerido": horas_req,
            "aportado": horas_aportadas,
            "cumple": cumple
        }
    return resultado

# ---------------------------------------------------------------------------------------------
# 4) INTERFAZ PRINCIPAL
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
    categorias_cam = ["Enfermera/o", "Gerocultor", "Fisioterapeuta", "Terapeuta Ocupacional", "Trabajador Social", "Psicólogo/a"]
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

        # --- Cálculo CAM ---
        ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero = calcular_ratio_cam(usuarios_cam, horas_cam)
        
        st.subheader("📊 Resultados CAM")
        # Ratio de Atención Directa
        st.markdown(
            colorear_linea(
                f"🔹 **Ratio de Atención Directa**: {formatear_ratio(ratio_directa)} (mínimo 0,23) →",
                cumple_ratio
            ),
            unsafe_allow_html=True
        )

        # Horas de Gerocultores
        st.markdown(
            colorear_linea(
                f"🔹 **Horas de Gerocultores**: {formatear_numero(horas_gero)} h/sem (mínimo: {formatear_numero(horas_min_gero)}) →",
                cumple_gero
            ),
            unsafe_allow_html=True
        )

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
        
        # --- Comprobamos cumplimiento ---
        resultados_ayto = comprobar_cumplimiento_ayuntamiento(usuarios_ayto, horas_ayto)
        
        st.subheader("📊 Resultados Ayuntamiento")
        for cat, data_cat in resultados_ayto.items():
            cumple = data_cat["cumple"]
            color_linea = colorear_linea(
                f"🔹 **{cat}**: {formatear_numero(data_cat['aportado'])} h/sem (mínimo: {formatear_numero(data_cat['requerido'])}) →",
                cumple
            )
            st.markdown(color_linea, unsafe_allow_html=True)

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

    **Además**, para la normativa CAM se **sumarán** las horas de 
    **Gerocultor (aux. ruta)** a las de **Gerocultor**.
    """)

    # Mostramos todas las categorías en un único bloque de inputs
    categorias_todas = [
        "Enfermera/o",
        "Gerocultor",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Trabajador Social",
        "Psicólogo/a",
        "Coordinador/a",        # solo AYTO
        "Gerocultor (aux. ruta)",  # solo AYTO
        "Conductor/a"              # solo AYTO
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
        # Ratio de Atención Directa
        st.markdown(
            colorear_linea(
                f"🔹 **Ratio de Atención Directa**: {formatear_ratio(ratio_directa)} (mínimo 0,23) →",
                cumple_ratio
            ),
            unsafe_allow_html=True
        )
        # Gerocultores
        st.markdown(
            colorear_linea(
                f"🔹 **Horas de Gerocultores (CAM)**: {formatear_numero(horas_gero)} h/sem (mínimo: {formatear_numero(horas_min_gero)}) →",
                cumple_gero
            ),
            unsafe_allow_html=True
        )

        # --- Cálculo Ayuntamiento (proporcional) ---
        resultados_ayto = comprobar_cumplimiento_ayuntamiento(usuarios_totales, horas_centro)
        
        st.subheader("📊 Resultados Ayuntamiento")
        for cat, data_cat in resultados_ayto.items():
            cumple = data_cat["cumple"]
            color_linea = colorear_linea(
                f"🔹 **{cat}**: {formatear_numero(data_cat['aportado'])} h/sem (mínimo: {formatear_numero(data_cat['requerido'])}) →",
                cumple
            )
            st.markdown(color_linea, unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------
# Al final, repetimos el branding (opcional)
# ---------------------------------------------------------------------------------------------
st.markdown(branding_html, unsafe_allow_html=True)