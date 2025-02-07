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

def calcular_horas_gerocultores(plazas):
    """
    Se requieren 225 horas semanales por cada 35 usuarios o fracción equivalente.
    """
    bloques = math.ceil(plazas / 35)
    return bloques * 225

def formatear_ratio(valor):
    if valor is None or not math.isfinite(valor):
        return "Valor no válido"
    return f"{Decimal(str(valor)).quantize(Decimal('0.00'))}".replace('.', ',')

def si_cumple_texto(cumple: bool) -> str:
    """
    Devuelve un texto con emoji en verde (✅) si cumple o rojo (❌) si no cumple, para uso en Streamlit.
    """
    return "✅ CUMPLE" if cumple else "❌ NO CUMPLE"

# ---------------------------------------------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------------------------------------------
st.title("Ádrika - 📊 Cálculo de RATIO de personal - Centros de Día (CAM)")

st.subheader("🏥 Ocupación del Centro de Día")
ocupacion = st.number_input(
    "Ingrese el número de usuarios (plazas ocupadas o autorizadas)",
    min_value=0,
    value=0,
    step=1,
    format="%d"
)

# Sección: Horas de Atención Directa
st.subheader("🔹 Horas semanales de Atención Directa")
horas_directas = {}
categorias_directas = [
    "Enfermero/a",
    "Gerocultor",
    "Fisioterapeuta",
    "Terapeuta Ocupacional",
    "Trabajador/a Social",
    "Psicólogo/a"
]
for cat in categorias_directas:
    horas_directas[cat] = st.number_input(
        f"{cat} (horas/semana)",
        min_value=0.0,
        format="%.2f",
        key=f"directas_{cat}"
    )

# BOTÓN Calcular
if st.button("📌 Calcular Ratio (CAM)"):
    if ocupacion == 0:
        st.error("⚠️ Debe introducir el número de usuarios (mayor que 0).")
        st.stop()

    # Cálculo de EJC totales
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(v) for v in horas_directas.values())
    ratio_directa = total_eq_directa / ocupacion  # EJC por usuario

    # Cálculo de cumplimiento de gerocultores
    horas_requeridas_gerocultores = calcular_horas_gerocultores(ocupacion)
    horas_introducidas_gerocultores = horas_directas.get("Gerocultor", 0)
    cumple_gerocultores = horas_introducidas_gerocultores >= horas_requeridas_gerocultores

    st.subheader("📊 Resultados del Cálculo de Ratios")
    cumple_ratio_directa = ratio_directa >= 0.23

    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if cumple_ratio_directa else "red"};'>
        🔹 <b>Ratio de Atención Directa</b>: {ratio_directa:.2f} (mínimo 0.23) → {si_cumple_texto(cumple_ratio_directa)}
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style='font-size:18px; color:{"green" if cumple_gerocultores else "red"};'>
        🔹 <b>Horas de Gerocultores</b>: {horas_introducidas_gerocultores:.2f} / {horas_requeridas_gerocultores:.2f} h/sem → {si_cumple_texto(cumple_gerocultores)}
    </p>
    """, unsafe_allow_html=True)

    # GUARDAR EN HTML (Informe completo)
    st.markdown("---")
    st.subheader("¿Desea generar el INFORME en HTML con todos los datos?")
    guardar_informe = st.checkbox("Marcar para indicar periodo y generar descarga")

    if guardar_informe:
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha inicio", value=date.today())
        with col2:
            fecha_fin = st.date_input("Fecha fin", value=date.today())

        if st.button("Generar HTML"):
            html_informe = f"""
            <!DOCTYPE html>
            <html lang='es'>
            <head>
              <meta charset='UTF-8'>
              <title>Informe Ratios - Centros de Día (CAM)</title>
              <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .verde {{ color: green; font-weight: bold; }}
                .rojo {{ color: red; font-weight: bold; }}
              </style>
            </head>
            <body>
              <h1>Informe de Ratios - Centros de Día (CAM)</h1>
              <p><b>Periodo:</b> {fecha_inicio} al {fecha_fin}</p>
              <p><b>Usuarios atendidos:</b> {ocupacion}</p>
              <p><b>Ratio de Atención Directa:</b> {ratio_directa:.2f} (mínimo 0.23) → 
                <span class='{"verde" if cumple_ratio_directa else "rojo"}'>{si_cumple_texto(cumple_ratio_directa)}</span>
              </p>
              <p><b>Horas de Gerocultores:</b> {horas_introducidas_gerocultores:.2f} / {horas_requeridas_gerocultores:.2f} h/sem →
                <span class='{"verde" if cumple_gerocultores else "rojo"}'>{si_cumple_texto(cumple_gerocultores)}</span>
              </p>
            </body>
            </html>
            """
            st.download_button(
                label="Descargar HTML",
                data=html_informe,
                file_name="informe_centros_dia_cam.html",
                mime="text/html"
            )
