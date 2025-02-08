import streamlit as st
import math
from decimal import Decimal
from datetime import date

# ---------------------------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------------------------
def calcular_equivalentes_jornada_completa(horas_semanales):
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def calcular_horas_gerocultores(usuarios):
    """
    Para cada 35 usuarios o fracción, se requieren 225 horas semanales.
    Se redondea hacia arriba (por cada fracción se exige el bloque completo).
    """
    return math.ceil(usuarios / 35) * 225

def formatear_ratio(valor):
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

def si_cumple_texto(cumple: bool) -> str:
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

# ---------------------------------------------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------------------------------------------
st.title("Ádrika - 📊 Cálculo de la RATIO de personal - Centros de Día CAM")
st.write("Calcule la ratio de personal de atención directa para Centros de Día con plazas concertadas con la CAM.")

st.markdown("### **Requisitos**")
st.markdown("""
1. El personal de atención directa (enfermera/o, gerocultor, fisioterapeuta, terapeuta ocupacional, trabajador/a social y psicólogo/a) **debe** alcanzar una ratio mínima de **0,23 EJC por usuario**.  
2. Para la categoría de **Gerocultor**, se exigirán **225 horas semanales** por cada **35 usuarios o fracción equivalente**.  
3. Solo se incluirá al personal que esté prestando sus servicios de forma efectiva en el centro durante el periodo de cómputo.
""")

# Datos básicos
st.subheader("🏥 Datos del Centro de Día")
usuarios = st.number_input(
    "Ingrese el número de usuarios (plazas ocupadas)",
    min_value=0,
    value=0,
    step=1,
    format="%d"
)

# Horas semanales de atención directa
st.markdown("### Horas semanales de **Atención Directa**")
# Se consideran solo las categorías obligatorias según el requisito
categorias_directas = [
    "Enfermera/o",
    "Gerocultor",
    "Fisioterapeuta",
    "Terapeuta Ocupacional",
    "Trabajador Social",
    "Psicólogo/a"
]

horas_directas = {}
for cat in categorias_directas:
    horas_directas[cat] = st.number_input(
        f"{cat} (horas/semana)",
        min_value=0.0,
        format="%.2f",
        key=f"centro_{cat}"
    )

# Botón para calcular
if st.button("📌 Calcular Ratio"):
    if usuarios == 0:
        st.error("⚠️ Debe introducir el número de usuarios (mayor que 0).")
        st.stop()
    
    # Calcular el total de equivalentes a jornada completa de atención directa
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(h) for h in horas_directas.values())
    ratio_directa = total_eq_directa / usuarios  # EJC por usuario

    cumple_ratio = ratio_directa >= 0.23

    # Calcular las horas mínimas exigidas para Gerocultores
    horas_min_gero = calcular_horas_gerocultores(usuarios)
    horas_gero = horas_directas.get("Gerocultor", 0)
    cumple_gero = horas_gero >= horas_min_gero

    # Guardamos los resultados en el session_state para poder usarlos en el HTML
    st.session_state["centro_calculated"] = True
    st.session_state["centro_resultados"] = {
        "usuarios": usuarios,
        "horas_directas": horas_directas,
        "total_eq_directa": total_eq_directa,
        "ratio_directa": ratio_directa,
        "horas_min_gero": horas_min_gero,
        "horas_gero": horas_gero,
        "cumple_ratio": cumple_ratio,
        "cumple_gero": cumple_gero
    }

# Mostrar resultados si se han calculado
if st.session_state.get("centro_calculated"):
    res = st.session_state["centro_resultados"]

    st.subheader("📊 Resultados del Cálculo de Ratios")
    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if res["cumple_ratio"] else "red"};'>
        🔹 <b>Ratio de Atención Directa</b>: {formatear_ratio(res["ratio_directa"])} (mínimo 0,23) → {si_cumple_texto(res["cumple_ratio"])}
    </p>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if res["cumple_gero"] else "red"};'>
        🔹 <b>Horas de Gerocultores</b>: {res["horas_gero"]:.2f} h/semana (mínimo requerido: {res["horas_min_gero"]} h/semana) → {si_cumple_texto(res["cumple_gero"])}
    </p>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------------------
    # GENERAR INFORME EN HTML
    # --------------------------------------------------------------------
    st.markdown("---")
    st.subheader("Generar Informe en HTML")
    guardar_informe = st.checkbox("Marcar para indicar periodo y generar descarga")

    if guardar_informe:
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha inicio", value=date.today(), key="centro_fecha_inicio")
        with col2:
            fecha_fin = st.date_input("Fecha fin", value=date.today(), key="centro_fecha_fin")

        if st.button("Generar HTML Informe"):
            # Preparar tabla de horas introducidas
            tabla_directa = ""
            for cat, h in res["horas_directas"].items():
                tabla_directa += f"<tr><td>{cat}</td><td>{h:.2f} h/sem</td></tr>"

            # Definir los textos de cumplimiento
            str_ratio = "Sí (>= 0,23)" if res["cumple_ratio"] else "No (< 0,23)"
            str_gero = f"Sí (>= {res['horas_min_gero']} h/sem)" if res["cumple_gero"] else f"No (< {res['horas_min_gero']} h/sem)"

            # Generar el HTML del informe
            html_informe = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Informe Ratios - Centros de Día CAM</title>
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
      width: 100%;
    }}
    th, td {{
      border: 1px solid #aaa;
      padding: 8px;
      text-align: left;
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
  </style>
</head>
<body>
  <h1>Informe de Ratios - Centros de Día CAM</h1>
  <p><b>Periodo:</b> {fecha_inicio} al {fecha_fin}</p>
  <p><b>Usuarios (Plazas ocupadas):</b> {res["usuarios"]}</p>
  
  <div class="seccion">
    <h2>Horas Introducidas - Atención Directa</h2>
    <table>
      <tr>
        <th>Categoría</th>
        <th>Horas/semana</th>
      </tr>
      {tabla_directa}
    </table>
  </div>
  
  <div class="seccion">
    <h2>Resultados Principales</h2>
    <p><b>Ratio de Atención Directa:</b> {formatear_ratio(res["ratio_directa"])} → <span class='{"verde" if res["cumple_ratio"] else "rojo"}'>{str_ratio}</span> (mínimo 0,23)</p>
    <p><b>Horas de Gerocultores:</b> {res["horas_gero"]:.2f} h/semana → <span class='{"verde" if res["cumple_gero"] else "rojo"}'>{str_gero}</span> (mínimo requerido: {res["horas_min_gero"]} h/semana)</p>
  </div>
  
  <hr>
  <p>Informe generado automáticamente desde la aplicación (Centros de Día CAM).</p>
</body>
</html>
"""
            st.download_button(
                label="Descargar HTML",
                data=html_informe,
                file_name="informe_centros_dia_cam.html",
                mime="text/html"
            )