import streamlit as st
import math
import base64
from decimal import Decimal
from datetime import date

# ---------------------------------------------------------------------------------------------
# Función para convertir imagen a Base64 con manejo de errores
# ---------------------------------------------------------------------------------------------
def get_base64_image(image_path):
    """
    Intenta abrir el archivo de imagen en modo binario, lo codifica en Base64
    y retorna la cadena en formato data URI.
    Si ocurre un error, muestra un mensaje y retorna None.
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        # Ajusta el MIME type según la extensión (aquí se asume PNG; para JPG, usar "image/jpeg")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        st.error(f"Error al cargar el logo desde '{image_path}': {e}. Asegúrate de que el archivo esté en la misma carpeta que app.py y se haya subido al repositorio.")
        return None

# Usamos "logo.png" porque el archivo está en la misma carpeta que app.py
logo_data_uri = get_base64_image("logo.png")

# ---------------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES (cálculos y formateos)
# ---------------------------------------------------------------------------------------------
def calcular_equivalentes_jornada_completa(horas_semanales):
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    return (horas_semanales * SEMANAS_AL_ANO) / HORAS_ANUALES_JORNADA_COMPLETA

def calcular_horas(plazas):
    """
    Calcula las horas semanales requeridas para Fisioterapia y Terapia Ocupacional (CAM):
      - Hasta 50 residentes: 4h/día (20h/sem)
      - Para cada 25 plazas adicionales (o fracción): +2h/día (10h/sem)
    """
    dias_semana = 5
    base_horas_diarias = 4.0
    if plazas <= 50:
        return base_horas_diarias * dias_semana
    else:
        plazas_adicionales = plazas - 50
        incrementos_enteros = plazas_adicionales // 25
        resto = plazas_adicionales % 25
        horas_adicionales = incrementos_enteros * 2.0 + (resto / 25.0) * 2.0
        return (base_horas_diarias + horas_adicionales) * dias_semana

def formatear_ratio(valor):
    """ Formatea un número (para ratios) con dos decimales y separador decimal con coma. """
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

def formatear_numero(valor):
    """
    Formatea un número con dos decimales, usando punto como separador de miles y coma como separador decimal.
    Ejemplo: 644706.77 -> "644.706,77"
    """
    if not isinstance(valor, (int, float)):
        return str(valor)
    formatted = f"{valor:,.2f}"
    # Reemplazamos el punto decimal por coma, y la coma de miles por punto
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

def si_cumple_texto(cumple: bool) -> str:
    """ Devuelve '✅ CUMPLE' si cumple o '❌ NO CUMPLE' en caso contrario. """
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

# ---------------------------------------------------------------------------------------------
# BLOQUE DE BRANDING CON LOGO (sin sombreado, sin texto adicional)
# ---------------------------------------------------------------------------------------------
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

# Mostrar el branding al inicio de la app
st.markdown(branding_html, unsafe_allow_html=True)

# Título principal de la app
st.markdown("<h2 style='text-align: center;'>📊 Cálculo de RATIO de personal - CAM</h2>", unsafe_allow_html=True)

st.markdown("### **Seleccione el tipo de cálculo que desea realizar:**")
modo_calculo = st.selectbox(
    "",
    [
        "Cálculo RATIO CAM AM atención residencial",
        "Cálculo RATIO CAM Orden 2680-2024 Acreditación de centros"
    ]
)

# Entrada de datos: Ocupación
st.subheader("🏥 Ocupación de la Residencia")
ocupacion = st.number_input(
    "Ingrese el número de residentes (plazas ocupadas o autorizadas)",
    min_value=0,
    value=0,
    step=1,
    format="%d"
)

# ===============================================================
# MODO 1: CÁLCULO RATIO CAM AM ATENCIÓN RESIDENCIAL
# ===============================================================
if modo_calculo == "Cálculo RATIO CAM AM atención residencial":
    st.write("**Modo de cálculo según normativa CAM AM (Atención Residencial).**")
    categorias_directas = [
        "Médico", "ATS/DUE (Enfermería)", "Gerocultor", "Fisioterapeuta",
        "Terapeuta Ocupacional", "Trabajador Social", "Psicólogo/a",
        "Animador sociocultural / TASOC", "Director/a"
    ]
    categorias_no_directas = ["Limpieza", "Cocina", "Mantenimiento"]

    st.subheader("🔹 Horas semanales de Atención Directa")
    horas_directas = {}
    for cat in categorias_directas:
        horas_directas[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_{cat}"
        )
    st.subheader("🔹 Horas semanales de Atención No Directa")
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
        
    # ------------------------
    # MUESTRA DE RESULTADOS (en pantalla)
    # ------------------------
    if st.session_state.get("cam_calculated"):
        res = st.session_state["cam_resultados"]
        td = res["total_eq_directa"]
        tnd = res["total_eq_no_directa"]
        rd = res["ratio_directa"]       # valor en %
        rnd = res["ratio_no_directa"]   # valor en %

        st.subheader("📊 Resultados del Cálculo de Ratios")
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
        eq_gerocultores = calcular_equivalentes_jornada_completa(
            res["horas_directas"].get("Gerocultor", 0)
        )
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
        horas_req_terapia = calcular_horas(res["ocupacion"])
        h_fisio = res["horas_directas"].get("Fisioterapeuta", 0)
        h_to = res["horas_directas"].get("Terapeuta Ocupacional", 0)

        # FISIO
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

        # TERAPIA OCUPACIONAL
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

        # --- INFO RATIOS ---
        st.subheader("ℹ️ Información sobre las ratios")
        st.write("- Atención Directa: Mínimo 0,47 (EJC) por residente.")
        st.write("- Gerocultores: Mínimo 0,33 (EJC) por residente.")
        st.write("- Fisioterapia y Terapia Ocupacional: 4h/día (20h/sem) para 1-50 plazas; +2h/día (10h/sem) por cada 25 plazas o fracción.")
        st.write("- Trabajador Social: Contratación obligatoria (>0).")
        st.write("- Médico: Presencia física de lunes a viernes (mínimo 5h/sem).")
        st.write("- Enfermería: 24h/día, 7d/sem (mínimo 168h/sem).")
        st.write("- Atención No Directa: Mínimo 0,15 (EJC) por residente.")
        st.write("- Psicólogo/a y Animador sociocultural: Servicios opcionales.")
        
        # -------------------------------------------------------------------------------------
        # INFORME HTML DETALLADO: INCLUYE TODAS LAS SECCIONES Y COLORES (CAM AM)
        # -------------------------------------------------------------------------------------
        st.markdown("---")
        st.subheader("¿Desea generar y descargar el INFORME semanal en HTML? (CAM AM)")
        guardar_cam = st.checkbox("Marcar para indicar periodo y generar/descargar el HTML (CAM AM)")
        if guardar_cam:
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha inicio (CAM AM)", value=date.today())
            with col2:
                fecha_fin = st.date_input("Fecha fin (CAM AM)", value=date.today())

            # Construimos las líneas HTML con el mismo color y texto que en la app:
            # (usamos las mismas variables color_* y si_cumple_texto)

            # Para generar los párrafos con color y negrita solo en "CUMPLE"/"NO CUMPLE", definimos una pequeña función:
            def linea_html(texto, color, cumple):
                """
                texto: la parte "Atención Directa (mínimo 0,47): 0,45 →"
                color: "green" o "red"
                cumple: bool => True/False => pondremos <span style='font-weight:bold;'>(✅ CUMPLE)</span> ...
                """
                return (
                    f"<p style='color:{color};'>"
                    f"{texto} "
                    f"<span style='font-weight:bold;'>{si_cumple_texto(cumple)}</span>"
                    f"</p>"
                )

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
      <img src="{logo_data_uri}" style="max-width: 200px; height: auto;" alt="Logo">
    </a>
  </div>

  <p><b>Periodo:</b> {fecha_inicio} al {fecha_fin}</p>
  <p><b>Plazas ocupadas:</b> {res['ocupacion']} residentes</p>

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
      <img src="{logo_data_uri}" style="max-width: 200px; height: auto;" alt="Logo">
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

# ===============================================================
# MODO 2: CÁLCULO RATIO CAM Orden 2680-2024 (solo atención directa)
# ===============================================================
else:
    st.write("**Modo de cálculo según la Orden 2680-2024 (Acreditación de centros).**")
    st.write("Para residencias de personas mayores, la ratio mínima de personal de atención directa es:")
    st.markdown("- **0,45** si la residencia tiene más de 50 plazas autorizadas.\n- **0,37** si la residencia tiene 50 o menos plazas autorizadas.")
    categorias_directas_2 = [
        "Médico", "ATS/DUE (Enfermería)", "Gerocultor", "Fisioterapeuta",
        "Terapeuta Ocupacional", "Trabajador Social", "Psicólogo/a",
        "Animador sociocultural / TASOC", "Director/a"
    ]
    horas_directas_2 = {}
    st.subheader("🔹 Horas semanales de Atención Directa")
    for cat in categorias_directas_2:
        horas_directas_2[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_2_{cat}"
        )

    if st.button("📌 Calcular Ratio (Orden 2680-2024)"):
        if ocupacion == 0:
            st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
            st.stop()

        total_eq_directa_2 = sum(calcular_equivalentes_jornada_completa(h) for h in horas_directas_2.values())
        ratio_directa_2 = total_eq_directa_2 / ocupacion  # EJC/residente
        ratio_minima_2 = 0.45 if ocupacion > 50 else 0.37
        ejc_requerido = ocupacion * ratio_minima_2
        deficit = max(ejc_requerido - total_eq_directa_2, 0)
        coste_por_persona = 17000 * 1.32  # 22.440 €/año
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

    # ------------------------
    # MUESTRA DE RESULTADOS (en pantalla)
    # ------------------------
    if st.session_state.get("orden2680_calculated"):
        r2 = st.session_state["orden2680_resultados"]
        td2 = r2["total_eq_directa"]
        rd2 = r2["ratio_directa"]
        rmin2 = r2["ratio_minima"]
        cumple_orden = (rd2 >= rmin2)

        st.subheader("📊 Resultados del Cálculo de Ratio")
        st.markdown(
            f"🔹 Atención Directa → Total EQ: **{formatear_numero(td2)}** | "
            f"Ratio: **{formatear_numero(rd2)}** por cada residente"
        )

        st.subheader("✅ Verificación de cumplimiento con la Orden 2680-2024")
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
                f"La ratio según los datos obtenidos es de {formatear_numero(rd2)}.<br>"
                f"La ratio mínima por la ocupación de la residencia es de {formatear_numero(rmin2)}.<br>"
                f"Para cumplir en esa ratio habría que contratar a {formatear_numero(r2['deficit'])} empleados.<br>"
                f"<span style='display: inline-block; font-weight: bold; background-color: yellow; padding: 0.2em;'>"
                f"Como mínimo el coste anual de personal se incrementaría en {formatear_numero(r2['coste_adicional'])} euros."
                f"</span><br>(Se estima como mínimo un coste por persona de {formatear_numero(r2['coste_por_persona'])} €/año)."
            )
            st.markdown(f"<p style='font-size:18px; color:red;'>{explanation}</p>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<p style='font-size:18px; color:green;'>"
                "El centro CUMPLE con la ratio mínima requerida."
                "</p>", unsafe_allow_html=True
            )

        # -----------------------------------------------------------------
        # INFORME HTML DETALLADO (Orden 2680-2024): generamos un informe
        # -----------------------------------------------------------------
        st.markdown("---")
        st.subheader("¿Desea generar y descargar el INFORME semanal en HTML? (Orden 2680-2024)")
        guardar_orden = st.checkbox("Marcar para indicar periodo y generar/descargar el HTML (Orden 2680-2024)")
        if guardar_orden:
            col1, col2 = st.columns(2)
            with col1:
                fecha_i2 = st.date_input("Fecha inicio (Orden 2680)", value=date.today())
            with col2:
                fecha_f2 = st.date_input("Fecha fin (Orden 2680)", value=date.today())

            # Vamos a generar un informe muy similar, con todos los datos:
            # (En este caso, la norma solo pide ratio de at. directa, pero mostramos todo).
            # Para ello, copiamos la lógica de color_orden y si_cumple_texto(cumple_orden), etc.

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
      <img src="{logo_data_uri}" style="max-width: 200px; height: auto;" alt="Logo">
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
      color_orden,
      cumple_orden
  )}

  {"".join([
      f"<p style='font-size:18px; color:red;'>{(
        'La ratio según los datos obtenidos es de ' + formatear_numero(rd2) + '.<br>'
        'La ratio mínima por la ocupación de la residencia es de ' + formatear_numero(rmin2) + '.<br>'
        'Para cumplir en esa ratio habría que contratar a ' + formatear_numero(r2['deficit']) + ' empleados.<br>'
        f'<span style="display: inline-block; font-weight: bold; background-color: yellow; padding: 0.2em;">'
        'Como mínimo el coste anual de personal se incrementaría en ' + formatear_numero(r2['coste_adicional']) + ' euros.'
        '</span><br>(Se estima como mínimo un coste por persona de ' + formatear_numero(r2['coste_por_persona']) + ' €/año).'
      )}</p>"
  ]) if r2["deficit"] > 0 else f"<p style='font-size:18px; color:green;'>El centro CUMPLE con la ratio mínima requerida.</p>"}

  <hr>
  <p>Informe generado automáticamente desde la aplicación (Orden 2680-2024).</p>
  <div class="branding">
    <a href="https://www.mayores.ai" target="_blank" style="color: blue; text-decoration: none; font-size: 20px;">
      <img src="{logo_data_uri}" style="max-width: 200px; height: auto;" alt="Logo">
    </a>
  </div>
</body>
</html>"""

            st.download_button(
                label="Generar y Descargar HTML (Orden 2680-2024)",
                data=html_orden,
                file_name="informe_orden_2680-2024.html",
                mime="text/html"
            )

# ---------------------------------------------------------------------------------------------
# Al final de la aplicación, se añade el branding (igual que al inicio)
st.markdown(branding_html, unsafe_allow_html=True)