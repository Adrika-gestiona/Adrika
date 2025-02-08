import streamlit as st
import math
import base64
from decimal import Decimal
from datetime import date

# ---------------------------------------------------------------------------------------------
# Función para convertir imagen a Base64
# ---------------------------------------------------------------------------------------------
def get_base64_image(image_path):
    """
    Abre el archivo de imagen en modo binario, lo codifica en Base64
    y retorna la cadena en formato data URI.
    """
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    # Suponiendo que el logo es PNG; si es JPG, cambiar "image/png" por "image/jpeg"
    return f"data:image/png;base64,{encoded}"

# Obtén la cadena Base64 del logo (asegúrate de que el archivo esté en la carpeta "assets")
logo_data_uri = get_base64_image("assets/logo.png")

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
    formatted = f"{valor:,.2f}"  # Ejemplo: "644,706.77"
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

def si_cumple_texto(cumple: bool) -> str:
    """ Devuelve '✅ CUMPLE' si cumple o '❌ NO CUMPLE' en caso contrario. """
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

# ---------------------------------------------------------------------------------------------
# BLOQUE DE BRANDING CON LOGO (sin sombreado ni texto adicional)
# ---------------------------------------------------------------------------------------------
branding_html = f"""
<div style="text-align: center; padding: 10px; margin-bottom: 10px;">
  <a href="https://www.mayores.ai" target="_blank">
    <img src="{logo_data_uri}" style="max-width: 200px; height: auto;" alt="Logo">
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
        
    if st.session_state.get("cam_calculated"):
        res = st.session_state["cam_resultados"]
        td = res["total_eq_directa"]
        tnd = res["total_eq_no_directa"]
        rd = res["ratio_directa"]
        rnd = res["ratio_no_directa"]
        st.subheader("📊 Resultados del Cálculo de Ratios")
        st.markdown(f"🔹 Atención Directa → Total EQ: **{td:.2f}** | Ratio: **{rd:.2f}** por cada 100 residentes")
        st.markdown(f"🔹 Atención No Directa → Total EQ: **{tnd:.2f}** | Ratio: **{rnd:.2f}** por cada 100 residentes")
        st.subheader("✅ Verificación de cumplimiento con la CAM")
        eq_gerocultores = calcular_equivalentes_jornada_completa(res["horas_directas"].get("Gerocultor", 0))
        ratio_gero = eq_gerocultores / res["ocupacion"] if res["ocupacion"] else 0
        cumple_gero = (ratio_gero >= 0.33)
        st.markdown(f"Atención Directa: {si_cumple_texto((rd/100) >= 0.47)} (Mínimo 0,47). Ratio: **{(rd/100):.2f}**")
        st.markdown(f"Atención No Directa: {si_cumple_texto((rnd/100) >= 0.15)} (Mínimo 0,15). Ratio: **{(rnd/100):.2f}**")
        st.markdown(f"Gerocultores: {si_cumple_texto(cumple_gero)} (Mínimo 0,33). Ratio: **{ratio_gero:.2f}**")
        st.subheader("🩺 Cálculo de horas Fisioterapia y Terapia Ocupacional")
        st.write(f"**Plazas ocupadas:** {res['ocupacion']} residentes")
        horas_req_terapia = calcular_horas(res["ocupacion"])
        h_fisio = res["horas_directas"].get("Fisioterapeuta", 0)
        h_to = res["horas_directas"].get("Terapeuta Ocupacional", 0)
        st.markdown(f"🔹 Fisioterapeuta → Horas requeridas/semana: **{horas_req_terapia:.2f}** | Horas introducidas: **{h_fisio:.2f}** → {si_cumple_texto(h_fisio >= horas_req_terapia)}")
        st.markdown(f"🔹 Terapeuta Ocupacional → Horas requeridas/semana: **{horas_req_terapia:.2f}** | Horas introducidas: **{h_to:.2f}** → {si_cumple_texto(h_to >= horas_req_terapia)}")
        st.subheader("🔎 Verificación de requisitos específicos")
        horas_ts = res["horas_directas"].get("Trabajador Social", 0)
        cumple_ts = (horas_ts > 0)
        horas_med = res["horas_directas"].get("Médico", 0)
        cumple_med = (horas_med >= 5)
        horas_enf = res["horas_directas"].get("ATS/DUE (Enfermería)", 0)
        cumple_enf = (horas_enf >= 168)
        st.markdown(f"Trabajador Social: Horas introducidas: **{horas_ts:.2f}** → {si_cumple_texto(cumple_ts)}")
        st.markdown(f"Médico: Horas introducidas: **{horas_med:.2f}** → {si_cumple_texto(cumple_med)} (mínimo 5h/sem)")
        st.markdown(f"Enfermería (ATS/DUE): Horas introducidas: **{horas_enf:.2f}** → {si_cumple_texto(cumple_enf)} (mínimo 168h/sem)")
        st.subheader("ℹ️ Información sobre las ratios")
        st.write("- Atención Directa: Mínimo 0,47 (EJC) por residente.")
        st.write("- Gerocultores: Mínimo 0,33 (EJC) por residente.")
        st.write("- Fisioterapia y Terapia Ocupacional: 4h/día (20h/sem) para 1-50 plazas; +2h/día (10h/sem) por cada 25 plazas o fracción.")
        st.write("- Trabajador Social: Contratación obligatoria (>0).")
        st.write("- Médico: Presencia física de lunes a viernes (mínimo 5h/sem).")
        st.write("- Enfermería: 24h/día, 7d/sem (mínimo 168h/sem).")
        st.write("- Atención No Directa: Mínimo 0,15 (EJC) por residente.")
        st.write("- Psicólogo/a y Animador sociocultural: Servicios opcionales.")
        
        st.markdown("---")
        st.subheader("¿Desea generar y descargar el INFORME semanal en HTML? (CAM AM)")
        guardar_cam = st.checkbox("Marcar para indicar periodo y generar/descargar el HTML (CAM AM)")
        if guardar_cam:
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha inicio (CAM AM)", value=date.today())
            with col2:
                fecha_fin = st.date_input("Fecha fin (CAM AM)", value=date.today())
            html_cam = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - CAM AM</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.4; color: #333; }}
    h1, h2, h3 {{ color: #333; }}
    table {{ border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid #aaa; padding: 8px; }}
    .verde {{ color: green; font-weight: bold; }}
    .rojo {{ color: red; font-weight: bold; }}
    .branding {{ text-align: center; padding: 10px; margin-top: 10px; }}
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
  <div>
    <h2>Horas Introducidas</h2>
    <table>
      <tr><th>Categoría</th><th>Horas/sem</th></tr>
      {''.join(f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>" for cat, h in res["horas_directas"].items())}
    </table>
    <table>
      <tr><th>Categoría</th><th>Horas/sem</th></tr>
      {''.join(f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>" for cat, h in res["horas_no_directas"].items())}
    </table>
  </div>
  <div>
    <h2>Resultados Principales</h2>
    <p>Atención Directa → Total EQ: <b>{td:.2f}</b> | Ratio: <b>{rd:.2f}</b> por cada 100 residentes</p>
    <p>Atención No Directa → Total EQ: <b>{tnd:.2f}</b> | Ratio: <b>{rnd:.2f}</b> por cada 100 residentes</p>
    <p>Gerocultores → {"Sí (>=0,33)" if cumple_gero else "No (<0,33)"} (Mínimo 0,33). Ratio: <b>{ratio_gero:.2f}</b></p>
  </div>
  <div>
    <h2>Verificación de cumplimiento</h2>
    <p>Atención Directa: {"Sí (>=0,47)" if (rd/100) >= 0.47 else "No (<0,47)"} (Mínimo 0,47). Ratio: <b>{(rd/100):.2f}</b></p>
    <p>Atención No Directa: {"Sí (>=0,15)" if (rnd/100) >= 0.15 else "No (<0,15)"} (Mínimo 0,15). Ratio: <b>{(rnd/100):.2f}</b></p>
  </div>
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
        horas_directas_2[cat] = st.number_input(f"{cat} (horas/semana)", min_value=0.0, format="%.2f", key=f"directas_2_{cat}")
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
    if st.session_state.get("orden2680_calculated"):
        r2 = st.session_state["orden2680_resultados"]
        td2 = r2["total_eq_directa"]
        rd2 = r2["ratio_directa"]
        rmin2 = r2["ratio_minima"]
        cumple_orden = (rd2 >= rmin2)
        st.subheader("📊 Resultados del Cálculo de Ratio")
        st.markdown(f"🔹 Atención Directa → Total EQ: **{formatear_numero(td2)}** | Ratio: **{formatear_numero(rd2)}** por cada residente")
        st.subheader("✅ Verificación de cumplimiento con la Orden 2680-2024")
        st.markdown(f"Atención Directa: {si_cumple_texto(cumple_orden)} (Mínimo {formatear_numero(rmin2)}) | Ratio: **{formatear_numero(rd2)}**")
        if r2["deficit"] > 0:
            explanation = (
                f"La ratio según los datos obtenidos es de {formatear_numero(rd2)}.<br>"
                f"La ratio mínima por la ocupación de la residencia es de {formatear_numero(rmin2)}.<br>"
                f"Para cumplir en esa ratio habría que contratar a {formatear_numero(r2['deficit'])} empleados.<br>"
                f"<span style='display: inline-block; font-weight: bold; background-color: yellow; padding: 0.2em;'>Como mínimo el coste anual de personal se incrementaría en {formatear_numero(r2['coste_adicional'])} euros.</span><br>"
                f"(Se estima como mínimo un coste por persona de {formatear_numero(r2['coste_por_persona'])} €/año)."
            )
            st.markdown(f"<p style='font-size:18px; color:red;'>{explanation}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:18px; color:green;'>El centro CUMPLE con la ratio mínima requerida.</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("¿Desea generar y descargar el INFORME semanal en HTML? (Orden 2680-2024)")
        guardar_orden = st.checkbox("Marcar para indicar periodo y generar/descargar el HTML (Orden 2680-2024)")
        if guardar_orden:
            col1, col2 = st.columns(2)
            with col1:
                fecha_i2 = st.date_input("Fecha inicio (Orden 2680)", value=date.today())
            with col2:
                fecha_f2 = st.date_input("Fecha fin (Orden 2680)", value=date.today())
            html_orden = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - Orden 2680-2024</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
    h1, h2, h3 {{ color: #333; }}
    table {{ border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid #aaa; padding: 8px; }}
    .verde {{ color: green; font-weight: bold; }}
    .rojo {{ color: red; font-weight: bold; }}
    .branding {{ text-align: center; padding: 10px; margin-top: 10px; }}
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
    {''.join(f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>" for cat, h in r2["horas_directas"].items())}
  </table>
  <h2>Resultado</h2>
  <p><b>Total EJC de Atención Directa:</b> {formatear_numero(td2)}</p>
  <p><b>Ratio de Atención Directa (EJC/residente):</b> {formatear_numero(rd2)}</p>
  <p><b>Ratio Mínima Requerida:</b> {formatear_numero(rmin2)}</p>
  <p><b>EJC requeridos:</b> {formatear_numero(r2['ejc_requerido'])}</p>
  <p><b>Déficit de EJC:</b> {formatear_numero(r2['deficit'])}</p>
  <p><b>Coste adicional anual estimado:</b> {formatear_numero(r2['coste_adicional'])} €</p>
  <p style="font-size:18px; color:{'red' if r2['deficit']>0 else 'green'};">
    {"".join([
      f"La ratio según los datos obtenidos es de {formatear_numero(rd2)}.<br>",
      f"La ratio mínima por la ocupación de la residencia es de {formatear_numero(rmin2)}.<br>",
      f"Para cumplir en esa ratio habría que contratar a {formatear_numero(r2['deficit'])} empleados.<br>",
      f"<span style='display: inline-block; font-weight: bold; background-color: yellow; padding: 0.2em;'>Como mínimo el coste anual de personal se incrementaría en {formatear_numero(r2['coste_adicional'])} euros.</span><br>",
      f"(Se estima como mínimo un coste por persona de {formatear_numero(r2['coste_por_persona'])} €/año)."
    ]) if r2["deficit"] > 0 else "El centro CUMPLE con la ratio mínima requerida."}
  </p>
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