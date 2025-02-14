import streamlit as st
import math
import base64
from decimal import Decimal
from datetime import date

# ---------------------------------------------------------------------------------------------
# Inyección de CSS personalizado para dar un nuevo toque al front-end y títulos enmarcados
# ---------------------------------------------------------------------------------------------
custom_css = """
<style>
/* Estilo global */
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(to right, #ece9e6, #ffffff);
    color: #333;
    margin: 0;
    padding: 0;
}
/* Encabezados básicos */
h1, h2, h3 {
    color: #2c3e50;
    text-align: center;
}
/* Botones personalizados */
div.stButton > button {
    background-color: #2c3e50;
    color: white;
    border-radius: 5px;
    padding: 0.5em 1em;
    border: none;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    transition: background-color 0.3s ease;
}
div.stButton > button:hover {
    background-color: #34495e;
}
/* Inputs y select */
input, select, .stNumberInput > div > input {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 0.5em;
}
/* Tablas */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
}
table, th, td {
    border: 1px solid #ddd;
}
th, td {
    padding: 0.5em;
    text-align: center;
}
/* Sección de branding */
.branding {
    text-align: center;
    padding: 20px;
    margin-bottom: 20px;
}
/* Estilo para títulos enmarcados */
.framed-title {
    font-size: 1.5em;
    border: 2px solid #2c3e50;
    border-radius: 8px;
    padding: 10px 20px;
    background-color: #f7f7f7;
    margin: 20px auto;
    width: fit-content;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------
# 1) BRANDING Y logo_pad (logo ampliado a 1800px, 3 veces mayor)
# ---------------------------------------------------------------------------------------------
def get_base64_image(image_path: str) -> str:
    """
    Lee un archivo de imagen y lo convierte a una cadena Base64 (data URI).
    Devuelve None si hay problema al leer el archivo.
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        st.error(f"No se pudo cargar el logo_pad desde '{image_path}': {e}")
        return None

# Ajusta aquí si el logo_pad se llama diferente o está en otra carpeta
logo_pad_data_uri = get_base64_image("logo_pad.png")

# Construimos el HTML del branding
if logo_pad_data_uri:
    branding_html = f"""
    <div class="branding">
      <a href="https://www.mayores.ai" target="_blank">
        <img src="{logo_pad_data_uri}" style="max-width: 1800px; height: auto;" alt="logo_pad">
      </a>
    </div>
    """
else:
    branding_html = """
    <div class="branding" style="font-size: 20px; color: blue;">
      <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none;">
        www.mayores.ai
      </a>
    </div>
    """

# ---------------------------------------------------------------------------------------------
# 2) FUNCIONES DE CÁLCULO Y FORMATEO (COMUNES A TODA LA APP)
# ---------------------------------------------------------------------------------------------
def calcular_equivalentes_jornada_completa(horas_semanales: float) -> float:
    """
    Convierte horas semanales en EJC, asumiendo 1772 h/año y ~52.14 sem/año.
    """
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO  # Corregido SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def formatear_numero(valor) -> str:
    """
    Devuelve un número con 2 decimales, separador decimal = ',',
    y separador de miles = '.'.
    Ej: 12345.678 -> '12.345,68'
    """
    if not isinstance(valor, (int, float)):
        return str(valor)
    formatted = f"{valor:,.2f}"
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

def formatear_ratio(valor) -> str:
    """
    Formatea un float con 2 decimales y sustituye '.' por ',' para ratios.
    """
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
    """
    color = "green" if cumple else "red"
    return (
        f"<p style='color:{color};'>"
        f"{texto} "
        f"<span style='font-weight:bold;'>{si_cumple_texto(cumple)}</span>"
        f"</p>"
    )

# ---------------------------------------------------------------------------------------------
# FUNCIONES ESPECÍFICAS PARA RESIDENCIAS (CAM y Orden 2680/2024)
# ---------------------------------------------------------------------------------------------
def calcular_horas_fisio_to_residencia(plazas: int) -> float:
    """
    Calcula las horas semanales requeridas para Fisioterapia / Terapia Ocupacional (CAM):
      - Hasta 50 residentes: 4h/día (20h/sem)
      - Para cada 25 plazas adicionales (o fracción): +2h/día (10h/sem)
    """
    dias_semana = 5
    base_horas_diarias = 4.0
    if plazas <= 50:
        return base_horas_diarias * dias_semana  # 20 semanales
    else:
        plazas_adicionales = plazas - 50
        incrementos_enteros = plazas_adicionales // 25
        resto = plazas_adicionales % 25
        horas_adicionales = incrementos_enteros * 2.0 + (resto / 25.0) * 2.0
        return (base_horas_diarias + horas_adicionales) * dias_semana

# ---------------------------------------------------------------------------------------------
# FUNCIONES ESPECÍFICAS PARA CENTROS DE DÍA (CAM y Ayuntamiento)
# ---------------------------------------------------------------------------------------------
def calcular_horas_gerocultores_cam(usuarios_cam: int) -> float:
    """
    Centros de día CAM:
    225 horas semanales de gerocultores por cada 35 usuarios o fracción.
    """
    bloques_completos = usuarios_cam // 35
    resto = usuarios_cam % 35
    horas_totales = bloques_completos * 225 + (resto / 35) * 225
    return horas_totales

def calcular_ratio_cam_cd(usuarios_cam: int, horas_dict: dict, sumar_ruta=False):
    """
    Devuelve:
      ratio_directa (EJC/usuario)
      si_cumple_ratio (bool) => >= 0.23
      horas_gero (float)
      horas_min_gero (float)
      si_cumple_gero (bool)

    :param sumar_ruta: si True, suma "Gerocultor (aux. ruta)" a "Gerocultor".
    """
    # 1) Ratio global 0,23 EJC/usuario (Enfermera/o, Gerocultor, Fisio, TO, TS, Psicólogo/a)
    total_ejc_directa = 0.0
    for cat in ["Enfermera/o", "Gerocultor", "Fisioterapeuta", "Terapeuta Ocupacional",
                "Trabajador Social", "Psicólogo_pad/a"]:
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
    Centros de día Ayuntamiento de Madrid:
    Horas mínimas por bloque de 30 usuarios (o fracción).
    """
    base_requisitos = {
        "Coordinador/a": 15,
        "Enfermera/o": 10,
        "Trabajador Social": 10,
        "Fisioterapeuta": 20,
        "Terapeuta Ocupacional": 20,
        "Psicólogo_pad/a": 10,
        "Gerocultor": 136,   # 4 EJC ~ 136 h/sem
        "Gerocultor (aux. ruta)": 30,
        "Conductor/a": 30
    }
    if usuarios_ayto <= 0:
        return {cat: 0.0 for cat in base_requisitos}

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
    Compara las horas aportadas vs. horas mínimas Ayuntamiento (para centros de día).
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
# LANZAMIENTO DEL BRANDING Y TÍTULO PRINCIPAL
# ---------------------------------------------------------------------------------------------
st.markdown(branding_html, unsafe_allow_html=True)
st.markdown("<h2 class='framed-title'>📊 Cálculo de ratios Residencias y Centro de Día CAM</h2>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------
# 3) MENÚ PRINCIPAL CON 5 OPCIONES
# ---------------------------------------------------------------------------------------------
opcion_calculo = st.selectbox(
    "Seleccione el tipo de Ratio que desea calcular:",
    [
        "1. Ratio Residencia Orden 2680/2024",
        "2. Ratio Residencia AM CAM cálculo ratio",
        "3. Ratio Centro de Día AM CAM (modo prueba)",
        "4. Ratio Centro de Día Ayto. de Madrid (modo prueba)",
        "5. Ratio Centro de Día AM CAM y Ayto. de Madrid (modo prueba)"
    ]
)

# ---------------------------------------------------------------------------------------------
# 4) LÓGICA PARA RESIDENCIAS
# ---------------------------------------------------------------------------------------------

# -------- Opción 1: Ratio Residencia Orden 2680/2024 --------
if opcion_calculo == "1. Ratio Residencia Orden 2680/2024":
    st.markdown("<h3 class='framed-title'>Cálculo de RATIO Orden 2680/2024 - Acreditación de centros</h3>", unsafe_allow_html=True)
    
    # Entrada de datos: Ocupación
    st.markdown("<h3 class='framed-title'>🏥 Ocupación de la Residencia</h3>", unsafe_allow_html=True)
    ocupacion = st.number_input(
        "Ingrese el número de residentes (plazas ocupadas o autorizadas)",
        min_value=0,
        value=0,
        step=1,
        format="%d"
    )

    st.write("**Ratio mínima de personal de atención directa**, según la norma:")
    st.markdown("- **0,45** si la residencia tiene más de 50 plazas autorizadas.")
    st.markdown("- **0,37** si la residencia tiene 50 o menos plazas autorizadas.")

    # Título para las horas de Atención Directa
    st.markdown("<h3 class='framed-title'>🔹 Horas semanales de Atención Directa (Orden 2680/2024)</h3>", unsafe_allow_html=True)
    categorias_directas_2 = [
        "Médico", "ATS/DUE (Enfermería)", "Gerocultor", "Fisioterapeuta",
        "Terapeuta Ocupacional", "Trabajador Social", "Psicólogo_pad/a",
        "Animador sociocultural / TASOC", "Director/a"
    ]
    horas_directas_2 = {}
    for cat in categorias_directas_2:
        horas_directas_2[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_2_{cat}"
        )

    if st.button("📌 Calcular Ratio (Orden 2680/2024)"):
        if ocupacion == 0:
            st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
            st.stop()

        total_eq_directa_2 = sum(calcular_equivalentes_jornada_completa(h) for h in horas_directas_2.values())
        ratio_directa_2 = total_eq_directa_2 / ocupacion  # EJC/residente
        if ocupacion > 50:
            ratio_minima_2 = 0.45
        else:
            ratio_minima_2 = 0.37

        ejc_requerido = ocupacion * ratio_minima_2
        deficit = max(ejc_requerido - total_eq_directa_2, 0)

        # Ejemplo de estimación de costes:
        coste_por_persona = 17000 * 1.32  # ~22.440 €/año
        coste_adicional = deficit * coste_por_persona

        st.session_state["orden2680_calculated"] = True
        st.session_state["orden2680_resultados"] = {
            "ocupacion": ocupacion,
            "horas_directas": horas_directas_2,
            "total_eq_directa": total_eq_directa_2,
            "ratio_directa": ratio_directa_2,
            "ratio_minima": ratio_minima_2,
            "ejc_requerido": ejc_requerido,
            "deficit": deficit,
            "coste_adicional": coste_adicional,
            "coste_por_persona": coste_por_persona
        }

    if st.session_state.get("orden2680_calculated"):
        r2 = st.session_state["orden2680_resultados"]
        td2 = r2["total_eq_directa"]
        rd2 = r2["ratio_directa"]
        rmin2 = r2["ratio_minima"]
        cumple_orden = (rd2 >= rmin2)

        st.subheader("📊 Resultados del Cálculo de Ratio (Orden 2680/2024)")
        st.markdown(
            f"🔹 Atención Directa → Total EQ: **{formatear_numero(td2)}** | "
            f"Ratio: **{formatear_numero(rd2)}** por cada residente"
        )
        color_orden = "green" if cumple_orden else "red"
        st.markdown(
            f"<p style='color:{color_orden};'>"
            f"Atención Directa (mínimo {formatear_numero(rmin2)}): {formatear_numero(rd2)} → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_orden)}</span>"
            f"</p>",
            unsafe_allow_html=True
        )

        if r2["deficit"] > 0:
            explanation = (
                f"La ratio obtenida es {formatear_numero(rd2)}.<br>"
                f"La ratio mínima es {formatear_numero(rmin2)}.<br>"
                f"Habría que contratar {formatear_numero(r2['deficit'])} empleados más.<br>"
                f"<span style='display: inline-block; font-weight: bold; background-color: yellow; padding: 0.2em;'>"
                f"El coste anual adicional estimado es {formatear_numero(r2['coste_adicional'])} €."
                f"</span><br>(Coste base por persona: {formatear_numero(r2['coste_por_persona'])} €/año)."
            )
            st.markdown(f"<p style='font-size:18px; color:red;'>{explanation}</p>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='font-size:18px; color:green;'>"
                "El centro CUMPLE con la ratio mínima requerida."
                "</p>", unsafe_allow_html=True
            )

        # Informe HTML detallado (Orden 2680/2024)
        st.markdown("---")
        st.subheader("¿Desea generar y descargar el INFORME semanal en HTML? (Orden 2680/2024)")
        guardar_orden = st.checkbox("Marcar para indicar periodo y generar/descargar el HTML (Orden 2680/2024)")
        if guardar_orden:
            col1, col2 = st.columns(2)
            with col1:
                fecha_i2 = st.date_input("Fecha inicio (Orden 2680)", value=date.today())
            with col2:
                fecha_f2 = st.date_input("Fecha fin (Orden 2680)", value=date.today())

            def linea_html_orden(texto, color, cumple):
                return (
                    f"<p style='color:{color};'>"
                    f"{texto} "
                    f"<span style='font-weight:bold;'>{si_cumple_texto(cumple)}</span>"
                    f"</p>"
                )

            html_orden = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - Orden 2680-2024</title>
  <style>
    body {{
      font-family: Arial, sans-serif; margin: 20px; color: #333;
    }}
    h1, h2, h3 {{
      color: #333;
    }}
    table {{
      border-collapse: collapse; margin: 10px 0;
    }}
    th, td {{
      border: 1px solid #aaa; padding: 8px;
    }}
    .branding {{
      text-align: center; padding: 10px; margin-top: 10px;
    }}
  </style>
</head>
<body>
  <h1>Informe de Ratios Semanal (Orden 2680-2024)</h1>
  <div class="branding">
    <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none; font-size: 20px;">
      <img src="{logo_pad_data_uri}" style="max-width: 1800px; height: auto;" alt="logo_pad">
    </a>
  </div>

  <p><b>Periodo:</b> {fecha_i2} al {fecha_f2}</p>
  <p><b>Plazas autorizadas/ocupadas:</b> {r2['ocupacion']}</p>

  <h2>Horas Introducidas (Atención Directa)</h2>
  <table>
    <tr><th>Categoría</th><th>Horas/sem</th></tr>
    {"".join(f"<tr><td>{cat}</td><td>{formatear_numero(h):s} h/sem</td></tr>" for cat, h in r2["horas_directas"].items())}
  </table>

  <h2>Resultado</h2>
  <p><b>Total EJC de Atención Directa:</b> {formatear_numero(td2)}</p>
  <p><b>Ratio de Atención Directa (EJC/residente):</b> {formatear_numero(rd2)}</p>
  <p><b>Ratio Mínima Requerida:</b> {formatear_numero(rmin2)}</p>
  <p><b>EJC requeridos:</b> {formatear_numero(r2['ejc_requerido'])}</p>
  <p><b>Déficit de EJC:</b> {formatear_numero(r2['deficit'])}</p>
  <p><b>Coste adicional anual estimado:</b> {formatear_numero(r2['coste_adicional'])} €</p>

  <h2>Verificación de cumplimiento</h2>
  {linea_html_orden(
      f"Atención Directa (mínimo {formatear_numero(rmin2)}): {formatear_numero(rd2)} →",
      "green" if cumple_orden else "red",
      cumple_orden
  )}

  {"".join([
      f"<p style='font-size:18px; color:red;'>{(
        'La ratio según los datos obtenidos es de ' + formatear_numero(rd2) + '.<br>'
        'La ratio mínima por la ocupación de la residencia es de ' + formatear_numero(rmin2) + '.<br>'
        'Para cumplir en esa ratio habría que contratar a ' + formatear_numero(r2['deficit']) + ' empleados.<br>'
        f'<span style="display: inline-block; font-weight: bold; background-color: yellow; padding: 0.2em;">'
        'Como mínimo el coste anual de personal se incrementaría en ' + formatear_numero(r2['coste_adicional']) + ' euros.'
        '</span><br>(Se estima un coste por persona de ' + formatear_numero(r2['coste_por_persona']) + ' €/año).'
      )}</p>"
  ]) if r2["deficit"] > 0 else f"<p style='font-size:18px; color:green;'>El centro CUMPLE con la ratio mínima requerida.</p>"}

  <hr>
  <p>Informe generado automáticamente desde la aplicación (Orden 2680-2024).</p>
  <div class="branding">
    <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none; font-size: 20px;">
      <img src="{logo_pad_data_uri}" style="max-width: 1800px; height: auto;" alt="logo_pad">
    </a>
  </div>
</body>
</html>"""

            st.download_button(
                label="Generar y Descargar HTML (Orden 2680/2024)",
                data=html_orden,
                file_name="informe_orden_2680-2024.html",
                mime="text/html"
            )

# -------- Opción 2: Ratio Residencia AM CAM --------
elif opcion_calculo == "2. Ratio Residencia AM CAM cálculo ratio":
    st.markdown("<h3 class='framed-title'>Cálculo de RATIO CAM AM - Atención Residencial</h3>", unsafe_allow_html=True)
    
    # Entrada de datos: Ocupación
    st.markdown("<h3 class='framed-title'>🏥 Ocupación de la Residencia</h3>", unsafe_allow_html=True)
    ocupacion = st.number_input(
        "Ingrese el número de residentes (plazas ocupadas o autorizadas)",
        min_value=0,
        value=0,
        step=1,
        format="%d"
    )

    # Títulos para los bloques de horas
    st.markdown("<h3 class='framed-title'>🔹 Horas semanales de Atención Directa</h3>", unsafe_allow_html=True)
    categorias_directas = [
        "Médico", "ATS/DUE (Enfermería)", "Gerocultor", "Fisioterapeuta",
        "Terapeuta Ocupacional", "Trabajador Social", "Psicólogo_pad/a",
        "Animador sociocultural / TASOC", "Director/a"
    ]
    horas_directas = {}
    for cat in categorias_directas:
        horas_directas[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_{cat}"
        )

    st.markdown("<h3 class='framed-title'>🔹 Horas semanales de Atención No Directa</h3>", unsafe_allow_html=True)
    categorias_no_directas = ["Limpieza", "Cocina", "Mantenimiento"]
    horas_no_directas = {}
    for cat in categorias_no_directas:
        horas_no_directas[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"nodirectas_{cat}"
        )

    if st.button("📌 Calcular Ratio (CAM AM)"):
        if ocupacion == 0:
            st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
            st.stop()

        total_eq_directa = sum(calcular_equivalentes_jornada_completa(v) for v in horas_directas.values())
        total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(v) for v in horas_no_directas.values())
        ratio_directa = (total_eq_directa / ocupacion) * 100
        ratio_no_directa = (total_eq_no_directa / ocupacion) * 100

        st.session_state["cam_calculated"] = True
        st.session_state["cam_resultados"] = {
            "ocupacion": ocupacion,
            "horas_directas": horas_directas,
            "horas_no_directas": horas_no_directas,
            "total_eq_directa": total_eq_directa,
            "total_eq_no_directa": total_eq_no_directa,
            "ratio_directa": ratio_directa,
            "ratio_no_directa": ratio_no_directa
        }

    if st.session_state.get("cam_calculated"):
        res = st.session_state["cam_resultados"]
        td = res["total_eq_directa"]
        tnd = res["total_eq_no_directa"]
        rd = res["ratio_directa"]
        rnd = res["ratio_no_directa"]

        st.subheader("📊 Resultados del Cálculo de Ratios (CAM AM)")
        st.markdown(
            f"🔹 Atención Directa → Total EQ: **{formatear_numero(td)}** | "
            f"Ratio: **{formatear_numero(rd)}** por cada 100 residentes"
        )
        st.markdown(
            f"🔹 Atención No Directa → Total EQ: **{formatear_numero(tnd)}** | "
            f"Ratio: **{formatear_numero(rnd)}** por cada 100 residentes"
        )

        st.subheader("✅ Verificación de cumplimiento con la CAM")

        # --- ATENCIÓN DIRECTA ---
        cumple_directa = (rd / 100) >= 0.47
        color_directa = "green" if cumple_directa else "red"
        st.markdown(
            f"<p style='color:{color_directa};'>"
            f"Atención Directa (mínimo 0,47): {formatear_numero(rd/100)} → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_directa)}</span>"
            f"</p>",
            unsafe_allow_html=True
        )

        # --- ATENCIÓN NO DIRECTA ---
        cumple_nodirecta = (rnd / 100) >= 0.15
        color_nodirecta = "green" if cumple_nodirecta else "red"
        st.markdown(
            f"<p style='color:{color_nodirecta};'>"
            f"Atención No Directa (mínimo 0,15): {formatear_numero(rnd/100)} → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_nodirecta)}</span>"
            f"</p>",
            unsafe_allow_html=True
        )

        # --- GEROCULTORES ---
        eq_gerocultores = calcular_equivalentes_jornada_completa(res["horas_directas"].get("Gerocultor", 0))
        ratio_gero = eq_gerocultores / res["ocupacion"] if res["ocupacion"] else 0
        cumple_gero = (ratio_gero >= 0.33)
        color_gero = "green" if cumple_gero else "red"
        st.markdown(
            f"<p style='color:{color_gero};'>"
            f"Gerocultores (mínimo 0,33): {formatear_numero(ratio_gero)} → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_gero)}</span>"
            f"</p>",
            unsafe_allow_html=True
        )

        # --- HORAS FISIOTERAPIA / T.O. ---
        st.subheader("🩺 Cálculo de horas Fisioterapia y Terapia Ocupacional")
        st.write(f"**Plazas ocupadas:** {res['ocupacion']} residentes")
        horas_req_terapia = calcular_horas_fisio_to_residencia(res["ocupacion"])
        h_fisio = res["horas_directas"].get("Fisioterapeuta", 0)
        h_to = res["horas_directas"].get("Terapeuta Ocupacional", 0)

        cumple_fisio = (h_fisio >= horas_req_terapia)
        color_fisio = "green" if cumple_fisio else "red"
        st.markdown(
            f"<p style='color:{color_fisio};'>"
            f"Fisioterapeuta → Horas requeridas/semana: {formatear_numero(horas_req_terapia)} | "
            f"Horas introducidas: {formatear_numero(h_fisio)} → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_fisio)}</span>"
            f"</p>",
            unsafe_allow_html=True
        )

        cumple_to = (h_to >= horas_req_terapia)
        color_to = "green" if cumple_to else "red"
        st.markdown(
            f"<p style='color:{color_to};'>"
            f"Terapeuta Ocupacional → Horas requeridas/semana: {formatear_numero(horas_req_terapia)} | "
            f"Horas introducidas: {formatear_numero(h_to)} → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_to)}</span>"
            f"</p>",
            unsafe_allow_html=True
        )

        # --- REQUISITOS ESPECÍFICOS ---
        st.subheader("🔎 Verificación de requisitos específicos")
        horas_ts = res["horas_directas"].get("Trabajador Social", 0)
        cumple_ts = (horas_ts > 0)
        horas_med = res["horas_directas"].get("Médico", 0)
        cumple_med = (horas_med >= 5)
        horas_enf = res["horas_directas"].get("ATS/DUE (Enfermería)", 0)
        cumple_enf = (horas_enf >= 168)

        color_ts = "green" if cumple_ts else "red"
        st.markdown(
            f"<p style='color:{color_ts};'>"
            f"Trabajador Social: {formatear_numero(horas_ts)} h/sem → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_ts)}</span> (mínimo > 0)"
            f"</p>",
            unsafe_allow_html=True
        )

        color_med = "green" if cumple_med else "red"
        st.markdown(
            f"<p style='color:{color_med};'>"
            f"Médico: {formatear_numero(horas_med)} h/sem → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_med)}</span> (mínimo 5h/sem)"
            f"</p>",
            unsafe_allow_html=True
        )

        color_enf = "green" if cumple_enf else "red"
        st.markdown(
            f"<p style='color:{color_enf};'>"
            f"Enfermería (ATS/DUE): {formatear_numero(horas_enf)} h/sem → "
            f"<span style='font-weight:bold;'>{si_cumple_texto(cumple_enf)}</span> (mínimo 168h/sem)"
            f"</p>",
            unsafe_allow_html=True
        )

        st.markdown("ℹ️ Información sobre las ratios")
        st.write("- **Atención Directa**: Mínimo 0,47 (EJC) por residente.")
        st.write("- **Gerocultores**: Mínimo 0,33 (EJC) por residente.")
        st.write("- **Fisioterapia y Terapia Ocupacional**: 4h/día (20h/sem) para 1-50 plazas; +2h/día (10h/sem) por cada 25 plazas o fracción.")
        st.write("- **Trabajador Social**: Contratación obligatoria (>0).")
        st.write("- **Médico**: Presencia física mínimo 5h/sem (lunes-viernes).")
        st.write("- **Enfermería**: 24h/día, 7d/sem (mínimo 168h/sem).")
        st.write("- **Atención No Directa**: Mínimo 0,15 (EJC) por residente.")
        st.write("- **Psicólogo_pad/a y Animador**: Opcionales en esta normativa.")

        # INFORME HTML DETALLADO (CAM AM)
        st.markdown("---")
        st.subheader("¿Desea generar y descargar el INFORME semanal en HTML? (CAM AM)")
        guardar_cam = st.checkbox("Marcar para indicar periodo y generar/descargar el HTML (CAM AM)")
        if guardar_cam:
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha inicio (CAM AM)", value=date.today())
            with col2:
                fecha_fin = st.date_input("Fecha fin (CAM AM)", value=date.today())

            # Repetimos variables para el informe
            td = res["total_eq_directa"]
            tnd = res["total_eq_no_directa"]
            rd = res["ratio_directa"]
            rnd = res["ratio_no_directa"]

            cumple_directa = (rd / 100) >= 0.47
            cumple_nodirecta = (rnd / 100) >= 0.15
            eq_gerocultores = calcular_equivalentes_jornada_completa(res["horas_directas"].get("Gerocultor", 0))
            ratio_gero = eq_gerocultores / res["ocupacion"] if res["ocupacion"] else 0
            cumple_gero = (ratio_gero >= 0.33)
            horas_req_terapia = calcular_horas_fisio_to_residencia(res["ocupacion"])
            h_fisio = res["horas_directas"].get("Fisioterapeuta", 0)
            cumple_fisio = (h_fisio >= horas_req_terapia)
            h_to = res["horas_directas"].get("Terapeuta Ocupacional", 0)
            cumple_to = (h_to >= horas_req_terapia)
            horas_ts = res["horas_directas"].get("Trabajador Social", 0)
            cumple_ts = (horas_ts > 0)
            horas_med = res["horas_directas"].get("Médico", 0)
            cumple_med = (horas_med >= 5)
            horas_enf = res["horas_directas"].get("ATS/DUE (Enfermería)", 0)
            cumple_enf = (horas_enf >= 168)

            def linea_html(texto, color, cumple):
                return (
                    f"<p style='color:{color};'>"
                    f"{texto} "
                    f"<span style='font-weight:bold;'>{si_cumple_texto(cumple)}</span>"
                    f"</p>"
                )

            color_directa = "green" if cumple_directa else "red"
            color_nodirecta = "green" if cumple_nodirecta else "red"
            color_gero = "green" if cumple_gero else "red"
            color_fisio = "green" if cumple_fisio else "red"
            color_to = "green" if cumple_to else "red"
            color_ts = "green" if cumple_ts else "red"
            color_med = "green" if cumple_med else "red"
            color_enf = "green" if cumple_enf else "red"

            html_cam = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - CAM AM</title>
  <style>
    body {{
      font-family: Arial, sans-serif; margin: 20px; line-height: 1.4; color: #333;
    }}
    h1, h2, h3 {{
      color: #333;
    }}
    table {{
      border-collapse: collapse; margin: 10px 0;
    }}
    th, td {{
      border: 1px solid #aaa; padding: 8px;
    }}
    .branding {{
      text-align: center; padding: 10px; margin-top: 10px;
    }}
  </style>
</head>
<body>
  <h1>Informe de Ratios Semanal (CAM AM)</h1>
  <div class="branding">
    <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none; font-size: 20px;">
      <img src="{logo_pad_data_uri}" style="max-width: 1800px; height: auto;" alt="logo_pad">
    </a>
  </div>

  <p><b>Periodo:</b> {fecha_inicio} al {fecha_fin}</p>
  <p><b>Plazas ocupadas:</b> {res['ocupacion']} residentes</p>

  <h2>Horas Introducidas (Atención Directa)</h2>
  <table>
    <tr><th>Categoría</th><th>Horas/sem</th></tr>
    {''.join(f"<tr><td>{cat}</td><td>{formatear_numero(h):s} h/sem</td></tr>" for cat, h in res["horas_directas"].items())}
  </table>

  <h2>Horas Introducidas (Atención No Directa)</h2>
  <table>
    <tr><th>Categoría</th><th>Horas/sem</th></tr>
    {''.join(f"<tr><td>{cat}</td><td>{formatear_numero(h):s} h/sem</td></tr>" for cat, h in res["horas_no_directas"].items())}
  </table>

  <h2>Resultados del Cálculo de Ratios</h2>
  <p>🔹 <b>Atención Directa</b> → Total EQ: <b>{formatear_numero(td)}</b> | Ratio: <b>{formatear_numero(rd)}</b> por cada 100 residentes</p>
  <p>🔹 <b>Atención No Directa</b> → Total EQ: <b>{formatear_numero(tnd)}</b> | Ratio: <b>{formatear_numero(rnd)}</b> por cada 100 residentes</p>

  <h2>Verificación de cumplimiento con la CAM</h2>
  {linea_html(
      f"Atención Directa (mínimo 0,47): {formatear_numero(rd/100)} →",
      color_directa,
      cumple_directa
  )}
  {linea_html(
      f"Atención No Directa (mínimo 0,15): {formatear_numero(rnd/100)} →",
      color_nodirecta,
      cumple_nodirecta
  )}
  {linea_html(
      f"Gerocultores (mínimo 0,33): {formatear_numero(ratio_gero)} →",
      color_gero,
      cumple_gero
  )}

  <h2>🩺 Cálculo de horas Fisioterapia y Terapia Ocupacional</h2>
  <p><b>Plazas ocupadas:</b> {res['ocupacion']} residentes</p>
  {linea_html(
      f"Fisioterapeuta → Horas requeridas/semana: {formatear_numero(horas_req_terapia)} | Horas introducidas: {formatear_numero(h_fisio)} →",
      color_fisio,
      cumple_fisio
  )}
  {linea_html(
      f"Terapeuta Ocupacional → Horas requeridas/semana: {formatear_numero(horas_req_terapia)} | Horas introducidas: {formatear_numero(h_to)} →",
      color_to,
      cumple_to
  )}

  <h2>🔎 Verificación de requisitos específicos</h2>
  {linea_html(
      f"Trabajador Social: {formatear_numero(horas_ts)} h/sem → (mínimo > 0)",
      color_ts,
      cumple_ts
  )}
  {linea_html(
      f"Médico: {formatear_numero(horas_med)} h/sem → (mínimo 5h/sem)",
      color_med,
      cumple_med
  )}
  {linea_html(
      f"Enfermería (ATS/DUE): {formatear_numero(horas_enf)} h/sem → (mínimo 168h/sem)",
      color_enf,
      cumple_enf
  )}

  <hr>
  <p>Informe generado automáticamente desde la aplicación (CAM AM).</p>
  <div class="branding">
    <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none; font-size: 20px;">
      <img src="{logo_pad_data_uri}" style="max-width: 1800px; height: auto;" alt="logo_pad">
    </a>
  </div>
</body>
</html>"""

            st.download_button(
                label="Generar y Descargar HTML (CAM AM)",
                data=html_cam,
                file_name="informe_cam_am.html",
                mime="text/html"
            )

# ---------------------------------------------------------------------------------------------
# 5) LÓGICA PARA CENTROS DE DÍA (CAM, Ayto, Ambos) - (modo prueba)
# ---------------------------------------------------------------------------------------------
# (El resto del código para las opciones 3, 4 y 5 se mantiene sin modificaciones específicas en los títulos)

elif opcion_calculo == "3. Ratio Centro de Día AM CAM (modo prueba)":
    st.markdown("<h3 class='framed-title'>Ratio Centro de Día - Normativa CAM (modo prueba)</h3>", unsafe_allow_html=True)
    usuarios_cam = st.number_input(
        "Nº de usuarios (plazas ocupadas CAM)",
        min_value=0, value=0, step=1, format="%d"
    )
    st.markdown("<h3 class='framed-title'>Horas semanales de Atención Directa (CAM)</h3>", unsafe_allow_html=True)
    categorias_cam = [
        "Enfermera/o",
        "Gerocultor",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Trabajador Social",
        "Psicólogo_pad/a"
    ]
    horas_cam = {}
    for cat in categorias_cam:
        horas_cam[cat] = st.number_input(
            f"{cat} (h/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"cd_cam_{cat}"
        )
    if st.button("📌 Calcular Ratio (CAM)"):
        if usuarios_cam == 0:
            st.error("⚠️ Debe introducir un número de usuarios (CAM) mayor que 0.")
            st.stop()
        ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero = calcular_ratio_cam_cd(usuarios_cam, horas_cam)
        st.subheader("📊 Resultados CAM (Centro de Día)")
        st.markdown(
            colorear_linea(
                f"🔹 **Ratio de Atención Directa**: {formatear_ratio(ratio_directa)} (mínimo 0,23) →",
                cumple_ratio
            ),
            unsafe_allow_html=True
        )
        st.markdown(
            colorear_linea(
                f"🔹 **Horas de Gerocultores**: {formatear_numero(horas_gero)} h/sem (mínimo: {formatear_numero(horas_min_gero)}) →",
                cumple_gero
            ),
            unsafe_allow_html=True
        )

elif opcion_calculo == "4. Ratio Centro de Día Ayto. de Madrid (modo prueba)":
    st.markdown("<h3 class='framed-title'>Ratio Centro de Día - Normativa Ayuntamiento de Madrid (modo prueba)</h3>", unsafe_allow_html=True)
    usuarios_ayto = st.number_input(
        "Nº de usuarios (plazas ocupadas Ayuntamiento)",
        min_value=0, value=0, step=1, format="%d"
    )
    categorias_ayto = [
        "Coordinador/a",
        "Enfermera/o",
        "Trabajador Social",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Psicólogo_pad/a",
        "Gerocultor",
        "Gerocultor (aux. ruta)",
        "Conductor/a"
    ]
    horas_ayto = {}
    st.markdown("<h3 class='framed-title'>Horas semanales según categorías (Ayuntamiento)</h3>", unsafe_allow_html=True)
    for cat in categorias_ayto:
        horas_ayto[cat] = st.number_input(
            f"{cat} (h/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"cd_ayto_{cat}"
        )
    if st.button("📌 Calcular Ratio (Ayuntamiento)"):
        if usuarios_ayto == 0:
            st.error("⚠️ Debe introducir un número de usuarios (Ayuntamiento) mayor que 0.")
            st.stop()
        resultados_ayto = comprobar_cumplimiento_ayuntamiento(usuarios_ayto, horas_ayto)
        st.subheader("📊 Resultados Ayuntamiento (Centro de Día)")
        for cat, data_cat in resultados_ayto.items():
            cumple = data_cat["cumple"]
            line_html = colorear_linea(
                f"🔹 **{cat}**: {formatear_numero(data_cat['aportado'])} h/sem (mínimo: {formatear_numero(data_cat['requerido'])}) →",
                cumple
            )
            st.markdown(line_html, unsafe_allow_html=True)

elif opcion_calculo == "5. Ratio Centro de Día AM CAM y Ayto. de Madrid (modo prueba)":
    st.markdown("<h3 class='framed-title'>Ratio Centro de Día - Normativa CAM y Ayuntamiento de Madrid (modo prueba)</h3>", unsafe_allow_html=True)
    usuarios_totales = st.number_input(
        "Nº de usuarios (plazas ocupadas totales)",
        min_value=0, value=0, step=1, format="%d"
    )
    st.markdown("""
    **Nota**: Con esta opción se aplica el mismo número de usuarios
    para la normativa CAM y la del Ayuntamiento.

    **Además**, para la CAM se suman las horas de "Gerocultor (aux. ruta)" a las de "Gerocultor".
    """)
    categorias_todas = [
        "Enfermera/o",
        "Gerocultor",
        "Fisioterapeuta",
        "Terapeuta Ocupacional",
        "Trabajador Social",
        "Psicólogo_pad/a",
        "Coordinador/a",
        "Gerocultor (aux. ruta)",
        "Conductor/a"
    ]
    horas_centro = {}
    st.markdown("<h3 class='framed-title'>Horas semanales - Personal total del Centro</h3>", unsafe_allow_html=True)
    for cat in categorias_todas:
        horas_centro[cat] = st.number_input(
            f"{cat} (h/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"cd_ambos_{cat}"
        )
    if st.button("📌 Calcular Ratio (CAM + Ayuntamiento)"):
        if usuarios_totales == 0:
            st.error("⚠️ Debe introducir un número de usuarios mayor que 0.")
            st.stop()
        # Cálculo CAM (sumando gerocultor ruta)
        ratio_directa, cumple_ratio, horas_gero, horas_min_gero, cumple_gero = calcular_ratio_cam_cd(usuarios_totales, horas_centro, sumar_ruta=True)
        st.subheader("📊 Resultados CAM")
        st.markdown(
            colorear_linea(
                f"🔹 **Ratio de Atención Directa**: {formatear_ratio(ratio_directa)} (mínimo 0,23) →",
                cumple_ratio
            ),
            unsafe_allow_html=True
        )
        st.markdown(
            colorear_linea(
                f"🔹 **Horas de Gerocultores**: {formatear_numero(horas_gero)} h/sem (mínimo: {formatear_numero(horas_min_gero)}) →",
                cumple_gero
            ),
            unsafe_allow_html=True
        )
        # Cálculo Ayuntamiento
        resultados_ayto = comprobar_cumplimiento_ayuntamiento(usuarios_totales, horas_centro)
        st.subheader("📊 Resultados Ayuntamiento")
        for cat, data_cat in resultados_ayto.items():
            cumple = data_cat["cumple"]
            line_html = colorear_linea(
                f"🔹 **{cat}**: {formatear_numero(data_cat['aportado'])} h/sem (mínimo: {formatear_numero(data_cat['requerido'])}) →",
                cumple
            )
            st.markdown(line_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------------------------
# Branding final (opcional)
# ---------------------------------------------------------------------------------------------
st.markdown(branding_html, unsafe_allow_html=True)