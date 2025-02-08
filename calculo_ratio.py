import streamlit as st
import math
from decimal import Decimal
from datetime import date
import os

# ---------------------------------------------------------------------------------------------
# MUESTRA DEL LOGO CON MANEJO DE ERROR (ruta absoluta)
# ---------------------------------------------------------------------------------------------
logo_path = r"c:\pruebas\logo.png"  # Ruta absoluta al logo en tu ordenador
if os.path.exists(logo_path):
    st.image(logo_path, width=200)
else:
    st.warning(f"Logo no encontrado en la ruta: {logo_path}")

# ---------------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------------------------
def calcular_equivalentes_jornada_completa(horas_semanales):
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def calcular_horas(plazas):
    """
    Horas semanales requeridas para Fisioterapia y Terapia Ocupacional (CAM):
    - Hasta 50 residentes: 4h/día (20h/sem)
    - Cada 25 plazas adicionales (o fracción): +2h/día (10h/sem)
    """
    dias_semana = 5
    base_horas_diarias = 4.0

    if plazas <= 50:
        horas_diarias = base_horas_diarias
    else:
        plazas_adicionales = plazas - 50
        incrementos_enteros = plazas_adicionales // 25
        resto = plazas_adicionales % 25
        horas_adicionales_enteras = incrementos_enteros * 2.0
        horas_adicionales_parciales = (resto / 25.0) * 2.0
        horas_diarias = base_horas_diarias + horas_adicionales_enteras + horas_adicionales_parciales

    return horas_diarias * dias_semana

def formatear_ratio(valor):
    """ Formatea un número con dos decimales usando coma como separador decimal. """
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    # Para ratios pequeñas no usamos separador de miles
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

def formatear_numero(valor):
    """
    Formatea un número de forma que:
      - Se muestran dos decimales.
      - Se usa punto como separador de miles y coma como separador decimal.
    Ejemplo: 644706.77 -> "644.706,77"
    """
    formatted = f"{valor:,.2f}"  # Por ejemplo, "644,706.77"
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return formatted

def si_cumple_texto(cumple: bool) -> str:
    """
    Devuelve un texto con emoji en verde (✅) si cumple o rojo (❌) si no cumple.
    """
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

# ---------------------------------------------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------------------------------------------
st.title("Ádrika - 📊 Cálculo de RATIO de personal - CAM")

st.markdown("### **Seleccione el tipo de cálculo que desea realizar:**")
modo_calculo = st.selectbox(
    "",
    [
        "Cálculo RATIO CAM AM atención residencial", 
        "Cálculo RATIO CAM Orden 2680-2024 Acreditación de centros"
    ]
)

# Ocupación
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
    categorias_no_directas = [
        "Limpieza",
        "Cocina",
        "Mantenimiento"
    ]

    # Sección: Horas de Atención Directa
    st.subheader("🔹 Horas semanales de Atención Directa")
    horas_directas = {}
    for cat in categorias_directas:
        horas_directas[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_{cat}"
        )

    # Sección: Horas de Atención No Directa
    st.subheader("🔹 Horas semanales de Atención No Directa")
    horas_no_directas = {}
    for cat in categorias_no_directas:
        horas_no_directas[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"nodirectas_{cat}"
        )

    # BOTÓN Calcular
    if st.button("📌 Calcular Ratio (CAM AM)"):
        if ocupacion == 0:
            st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
            st.stop()

        # Cálculo de EJC totales
        total_eq_directa = sum(calcular_equivalentes_jornada_completa(v) for v in horas_directas.values())
        total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(v) for v in horas_no_directas.values())

        # Ratios por cada 100 residentes
        ratio_directa = (total_eq_directa / ocupacion) * 100
        ratio_no_directa = (total_eq_no_directa / ocupacion) * 100

        # Guardar en session_state
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

    # MOSTRAR RESULTADOS si están calculados
    if st.session_state.get("cam_calculated"):
        res = st.session_state["cam_resultados"]
        td = res["total_eq_directa"]
        tnd = res["total_eq_no_directa"]
        rd = res["ratio_directa"]     # ratio (por 100)
        rnd = res["ratio_no_directa"] # ratio (por 100)

        st.subheader("📊 Resultados del Cálculo de Ratios")
        # Determinamos si cumple
        cumple_directa = (rd / 100) >= 0.47
        cumple_no_directa = (rnd / 100) >= 0.15

        st.markdown(f"""
        <p style='font-size:18px; color:{"green" if cumple_directa else "red"};'>
            🔹 <b>Atención Directa</b> → Total EQ: <b>{td:.2f}</b> | 
            Ratio: <b>{rd:.2f}</b> por cada 100 residentes
        </p>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <p style='font-size:18px; color:{"green" if cumple_no_directa else "red"};'>
            🔹 <b>Atención No Directa</b> → Total EQ: <b>{tnd:.2f}</b> | 
            Ratio: <b>{rnd:.2f}</b> por cada 100 residentes
        </p>
        """, unsafe_allow_html=True)

        st.subheader("✅ Verificación de cumplimiento con la CAM")
        # Gerocultores
        eq_gerocultores = calcular_equivalentes_jornada_completa(
            res["horas_directas"].get("Gerocultor", 0)
        )
        ratio_gero = eq_gerocultores / res["ocupacion"] if res["ocupacion"] else 0
        cumple_gero = (ratio_gero >= 0.33)

        st.markdown(f"- **Atención Directa**: {si_cumple_texto(cumple_directa)} (Mínimo 0,47). Ratio: {rd/100:.2f}")
        st.markdown(f"- **Atención No Directa**: {si_cumple_texto(cumple_no_directa)} (Mínimo 0,15). Ratio: {rnd/100:.2f}")
        st.markdown(f"- **Gerocultores**: {si_cumple_texto(cumple_gero)} (Mínimo 0,33). Ratio: {ratio_gero:.2f}")

        # Cálculo de horas Fisioterapia / TO
        st.subheader("🩺 Cálculo de horas Fisioterapia y Terapia Ocupacional")
        st.write(f"**Plazas ocupadas:** {res['ocupacion']} residentes")
        horas_req_terapia = calcular_horas(res["ocupacion"])
        h_fisio = res["horas_directas"].get("Fisioterapeuta", 0)
        h_to = res["horas_directas"].get("Terapeuta Ocupacional", 0)

        cumple_fisio = (h_fisio >= horas_req_terapia)
        cumple_to = (h_to >= horas_req_terapia)

        st.markdown(f"""
        🔹 **Fisioterapeuta**: Horas requeridas/semana: **{horas_req_terapia:.2f}**. 
        Horas introducidas: **{h_fisio:.2f}** → {si_cumple_texto(cumple_fisio)}
        """)
        st.markdown(f"""
        🔹 **Terapeuta Ocupacional**: Horas requeridas/semana: **{horas_req_terapia:.2f}**.
        Horas introducidas: **{h_to:.2f}** → {si_cumple_texto(cumple_to)}
        """)

        # Requisitos específicos
        st.subheader("🔎 Verificación de requisitos específicos")

        horas_ts = res["horas_directas"].get("Trabajador Social", 0)
        cumple_ts = (horas_ts > 0)

        horas_med = res["horas_directas"].get("Médico", 0)
        cumple_med = (horas_med >= 5)

        horas_enf = res["horas_directas"].get("ATS/DUE (Enfermería)", 0)
        cumple_enf = (horas_enf >= 168)

        st.markdown(f"""
        🔹 **Trabajador Social**: Contratación obligatoria. Horas introducidas: **{horas_ts:.2f}** → {si_cumple_texto(cumple_ts)}
        """)
        st.markdown(f"""
        🔹 **Médico**: Presencia de lunes a viernes (≥5h/sem). Horas introducidas: **{horas_med:.2f}** → {si_cumple_texto(cumple_med)} 
        (siempre y cuando haya habido presencia L-V)
        """)
        st.markdown(f"""
        🔹 **Enfermería (ATS/DUE)**: Presencia 24h/día, 7 días/sem (≥168h/sem). Horas introducidas: **{horas_enf:.2f}** → {si_cumple_texto(cumple_enf)}
        (siempre y cuando se haya cubierto 24h/día, 7d/sem.)
        """)

        st.subheader("ℹ️ Información sobre las ratios")
        st.write("- **Atención Directa**: Mínimo de 0,47 (EJC) por residente.")
        st.write("- **Gerocultores**: Mínimo de 0,33 (EJC) por residente.")
        st.write("- **Fisioterapeuta y Terapeuta Ocupacional**: 4 horas/día (20h/sem) para 1-50 plazas; "
                 "+2h/día (10h/sem) por cada 25 plazas o fracción.")
        st.write("- **Trabajador Social**: Contratación obligatoria (>0).")
        st.write("- **Médico**: Presencia física de lunes a viernes (≥5h/sem).")
        st.write("- **Enfermería**: 24h/día, 7 días (≥168h/sem).")
        st.write("- **Atención No Directa**: Mínimo de 0,15 (EJC) por residente.")
        st.write("- **Psicólogo/a y Animador sociocultural**: Servicios opcionales.")

        # --------------------------------------------------------------------
        # GUARDAR EN HTML (Informe completo CAM AM)
        # --------------------------------------------------------------------
        st.markdown("---")
        st.subheader("¿Desea generar el INFORME semanal en HTML con todos los datos? (CAM AM)")
        guardar_cam = st.checkbox("Marcar para indicar periodo y generar descarga (CAM AM)")

        if guardar_cam:
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha inicio (CAM AM)", value=date.today())
            with col2:
                fecha_fin = st.date_input("Fecha fin (CAM AM)", value=date.today())

            if st.button("Generar HTML (CAM AM)"):
                # Preparar tablas con horas
                tabla_directa = ""
                for cat, h in res["horas_directas"].items():
                    tabla_directa += f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>"

                tabla_no_directa = ""
                for cat, h in res["horas_no_directas"].items():
                    tabla_no_directa += f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>"

                # Disclaimers de cumplimiento
                str_directa = "Sí (>=0,47)" if cumple_directa else "No (<0,47)"
                str_nodirecta = "Sí (>=0,15)" if cumple_no_directa else "No (<0,15)"
                str_gero = "Sí (>=0,33)" if cumple_gero else "No (<0,33)"
                str_fisio = "Sí" if cumple_fisio else "No"
                str_to = "Sí" if cumple_to else "No"
                str_ts = "Sí (>0)" if cumple_ts else "No (0h)"
                str_med = "Sí (>=5h)" if cumple_med else "No (<5h)"
                str_enf = "Sí (>=168h)" if cumple_enf else "No (<168h)"

                html_cam = f"""\

<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - CAM AM</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px;
      line-height: 1.4;
      color: #333;
    }}
    h1, h2, h3 {{
      color: #333;
    }}
    table {{
      border-collapse: collapse;
      margin: 10px 0;
    }}
    th, td {{
      border: 1px solid #aaa;
      padding: 8px;
    }}
    .verde {{
      color: green;
      font-weight: bold;
    }}
    .rojo {{
      color: red;
      font-weight: bold;
    }}
    .seccion {{
      margin-bottom: 1em;
    }}
    .info-req ul {{
      list-style: disc;
      margin-left: 20px;
    }}
  </style>
</head>
<body>
  <h1>Informe de Ratios Semanal (CAM AM)</h1>
  <p><b>Periodo:</b> {fecha_inicio} al {fecha_fin}</p>
  <p><b>Plazas ocupadas:</b> {res['ocupacion']} residentes</p>

  <div class="seccion">
    <h2>Horas Introducidas - Atención Directa</h2>
    <table>
      <tr><th>Categoría</th><th>Horas/sem</th></tr>
      {tabla_directa}
    </table>

    <h2>Horas Introducidas - Atención No Directa</h2>
    <table>
      <tr><th>Categoría</th><th>Horas/sem</th></tr>
      {tabla_no_directa}
    </table>
  </div>

  <div class="seccion">
    <h2>Resultados Principales</h2>
    <p><b>Atención Directa</b>: Total EJC = {td:.2f} | Ratio = {rd:.2f} por cada 100 residentes → 
       <span class='{"verde" if cumple_directa else "rojo"}'>{str_directa}</span>
    </p>
    <p><b>Atención No Directa</b>: Total EJC = {tnd:.2f} | Ratio = {rnd:.2f} por cada 100 residentes → 
       <span class='{"verde" if cumple_no_directa else "rojo"}'>{str_nodirecta}</span>
    </p>
    <p><b>Gerocultores</b>: EJC = {eq_gerocultores:.2f}, Ratio {ratio_gero:.2f} → 
       <span class='{"verde" if cumple_gero else "rojo"}'>{str_gero}</span>
    </p>
  </div>

  <div class="seccion">
    <h2>Fisioterapeuta y Terapeuta Ocupacional</h2>
    <p>Horas requeridas (según plazas): {horas_req_terapia:.2f} h/sem</p>
    <p>Fisioterapeuta: {h_fisio:.2f} → 
       <span class='{"verde" if cumple_fisio else "rojo"}'>{str_fisio}</span>
    </p>
    <p>Terapeuta Ocupacional: {h_to:.2f} → 
       <span class='{"verde" if cumple_to else "rojo"}'>{str_to}</span>
    </p>
  </div>

  <div class="seccion">
    <h2>Verificación de requisitos específicos</h2>
    <p>Trabajador Social: {horas_ts:.2f} → <span class='{"verde" if cumple_ts else "rojo"}'>{str_ts}</span></p>
    <p>Médico (≥5h/sem, L-V): {horas_med:.2f} → <span class='{"verde" if cumple_med else "rojo"}'>{str_med}</span>
       (siempre que haya presencia L-V)</p>
    <p>Enfermería (≥168h/sem, 24h/día): {horas_enf:.2f} → <span class='{"verde" if cumple_enf else "rojo"}'>{str_enf}</span>
       (siempre que se cubra 24h/día, 7d/sem)</p>
  </div>

  <hr>
  <p>Informe generado automáticamente desde la aplicación (CAM AM).</p>
</body>
</html>
"""
                st.download_button(
                    label="Descargar HTML",
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
    st.markdown("- **0,45** si la residencia tiene más de 50 plazas autorizadas.\n"
                "- **0,37** si la residencia tiene 50 o menos plazas autorizadas.")

    categorias_directas_2 = [
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
    horas_directas_2 = {}

    st.subheader("🔹 Horas semanales de Atención Directa")
    for cat in categorias_directas_2:
        horas_directas_2[cat] = st.number_input(
            f"{cat} (horas/semana)",
            min_value=0.0,
            format="%.2f",
            key=f"directas_2_{cat}"
        )

    # Botón para Calcular (Orden 2680-2024)
    if st.button("📌 Calcular Ratio (Orden 2680-2024)"):
        if ocupacion == 0:
            st.error("⚠️ Debe introducir el número de residentes (mayor que 0).")
            st.stop()

        total_eq_directa_2 = sum(calcular_equivalentes_jornada_completa(h) for h in horas_directas_2.values())
        ratio_directa_2 = total_eq_directa_2 / ocupacion  # EJC/residente

        # Determinamos la ratio mínima según el número de residentes
        if ocupacion > 50:
            ratio_minima_2 = 0.45
        else:
            ratio_minima_2 = 0.37

        # Cálculo del déficit y coste adicional
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

    # Mostrar resultados si se ha calculado
    if st.session_state.get("orden2680_calculated"):
        r2 = st.session_state["orden2680_resultados"]
        td2 = r2["total_eq_directa"]
        rd2 = r2["ratio_directa"]  # EJC/residente
        rmin2 = r2["ratio_minima"]

        st.subheader("📊 Resultado del Cálculo de Ratio (Atención Directa)")

        # Mostrar resultados numéricos (opcional)
        st.write(f"**Total de EJC de Atención Directa:** {formatear_numero(td2)}")
        st.write(f"**Ratio de Atención Directa (EJC/residente):** {formatear_numero(rd2)}")
        st.write(f"**Ratio Mínima Requerida:** {formatear_numero(rmin2)}")
        st.write(f"**EJC requeridos:** {formatear_numero(r2['ejc_requerido'])}")
        st.write(f"**Déficit de EJC:** {formatear_numero(r2['deficit'])}")
        st.write(f"**Coste adicional anual estimado:** {formatear_numero(r2['coste_adicional'])} € (Coste por persona: {formatear_numero(r2['coste_por_persona'])} €/año)")

        # Mostrar mensaje personalizado en función del cumplimiento de la ratio, con saltos de línea
        if r2["deficit"] > 0:
            explanation = (
                f"La ratio según los datos obtenidos es de {formatear_numero(rd2)}.<br>"
                f"La ratio mínima por la ocupación de la residencia es de {formatear_numero(rmin2)}.<br>"
                f"Para cumplir en esa ratio habría que contratar a {formatear_numero(r2['deficit'])} empleados.<br>"
                f"Como mínimo el coste anual de personal se incrementaría en {formatear_numero(r2['coste_adicional'])} euros.<br>"
                f"(Se estima como mínimo un coste por persona de {formatear_numero(r2['coste_por_persona'])} €/año)."
            )
            st.markdown(f"<p style='font-size:18px; color:red;'>{explanation}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:18px; color:green;'>El centro CUMPLE con la ratio mínima requerida.</p>", unsafe_allow_html=True)

        # --------------------------------------------------------------------
        # GUARDAR EN HTML (Informe completo para Orden 2680-2024)
        # --------------------------------------------------------------------
        st.markdown("---")
        st.subheader("¿Desea generar el INFORME semanal en HTML (Orden 2680-2024)?")
        guardar_orden = st.checkbox("Marcar para indicar periodo y generar descarga")

        if guardar_orden:
            c1, c2 = st.columns(2)
            with c1:
                fecha_i2 = st.date_input("Fecha inicio (Orden 2680)", value=date.today())
            with c2:
                fecha_f2 = st.date_input("Fecha fin (Orden 2680)", value=date.today())

            if st.button("Generar HTML (Orden 2680-2024)"):
                # Tabla de horas introducidas
                tabla_dir_2 = ""
                for cat, h in r2["horas_directas"].items():
                    tabla_dir_2 += f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>"

                # Preparar explicación personalizada en líneas separadas
                if r2["deficit"] > 0:
                    html_explanation = (
                        f"La ratio según los datos obtenidos es de {formatear_numero(rd2)}.<br>"
                        f"La ratio mínima por la ocupación de la residencia es de {formatear_numero(rmin2)}.<br>"
                        f"Para cumplir en esa ratio habría que contratar a {formatear_numero(r2['deficit'])} empleados.<br>"
                        f"Como mínimo el coste anual de personal se incrementaría en {formatear_numero(r2['coste_adicional'])} euros.<br>"
                        f"(Se estima como mínimo un coste por persona de {formatear_numero(r2['coste_por_persona'])} €/año)."
                    )
                    color_explanation = "red"
                else:
                    html_explanation = "El centro CUMPLE con la ratio mínima requerida."
                    color_explanation = "green"

                html_orden = f"""\

<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - Orden 2680-2024</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px;
      color: #333;
    }}
    h1, h2, h3 {{
      color: #333;
    }}
    table {{
      border-collapse: collapse;
      margin: 10px 0;
    }}
    th, td {{
      border: 1px solid #aaa;
      padding: 8px;
    }}
    .verde {{
      color: green;
      font-weight: bold;
    }}
    .rojo {{
      color: red;
      font-weight: bold;
    }}
  </style>
</head>
<body>
  <h1>Informe de Ratios Semanal (Orden 2680-2024)</h1>
  <p><b>Periodo:</b> {fecha_i2} al {fecha_f2}</p>
  <p><b>Plazas autorizadas/ocupadas:</b> {r2['ocupacion']}</p>

  <h2>Horas Introducidas (Atención Directa)</h2>
  <table>
    <tr><th>Categoría</th><th>Horas/sem</th></tr>
    {tabla_dir_2}
  </table>

  <h2>Resultado</h2>
  <p><b>Total EJC de Atención Directa:</b> {formatear_numero(td2)}</p>
  <p><b>Ratio de Atención Directa (EJC/residente):</b> {formatear_numero(rd2)}</p>
  <p><b>Ratio Mínima Requerida:</b> {formatear_numero(rmin2)}</p>
  <p><b>EJC requeridos:</b> {formatear_numero(r2['ejc_requerido'])}</p>
  <p><b>Déficit de EJC:</b> {formatear_numero(r2['deficit'])}</p>
  <p><b>Coste adicional anual estimado:</b> {formatear_numero(r2['coste_adicional'])} €</p>
  <p style="font-size:18px; color:{color_explanation};">
    {html_explanation}
  </p>

  <hr>
  <p>Informe generado automáticamente desde la aplicación (Orden 2680-2024).</p>
</body>
</html>
"""
                st.download_button(
                    label="Descargar HTML",
                    data=html_orden,
                    file_name="informe_orden_2680-2024.html",
                    mime="text/html"
                )