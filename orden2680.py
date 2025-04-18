import streamlit as st
import pandas as pd
import json
import os
from fpdf import FPDF

# --- Datos internos (completos, reconstruidos desde el Excel) ---
datos_requisitos = [
    {"Bloque": "Recursos materiales y equipamientos", "Subbloque": "Condiciones arquitectónicas", "Requisito": "La estructura del edificio debe garantizar accesibilidad total."},
    {"Bloque": "Recursos materiales y equipamientos", "Subbloque": "Unidades de convivencia", "Requisito": "Cada unidad debe tener un espacio común, como salón o comedor, para sus residentes."},
    {"Bloque": "Recursos materiales y equipamientos", "Subbloque": "Habitaciones", "Requisito": "Las habitaciones deben contar con sistema de llamada y ventilación adecuada."},
    {"Bloque": "Recursos materiales y equipamientos", "Subbloque": "Acceso a internet", "Requisito": "Debe existir conexión a internet en zonas comunes y oficinas administrativas."},
    {"Bloque": "Recursos humanos", "Subbloque": "Tipología", "Requisito": "El personal debe estar cualificado y formado en atención a personas mayores."},
    {"Bloque": "Recursos humanos", "Subbloque": "Ratios mínimas de personal de atención directa", "Requisito": "La ratio mínima de personal se ajustará a la normativa vigente según grado de dependencia."},
    {"Bloque": "Recursos humanos", "Subbloque": "Organización del trabajo", "Requisito": "La planificación de turnos debe garantizar continuidad asistencial."},
    {"Bloque": "Recursos humanos", "Subbloque": "Roles y perfiles profesionales", "Requisito": "Deben definirse funciones y responsabilidades específicas para cada perfil profesional."},
    {"Bloque": "Documentación e información", "Subbloque": "Gestión documental", "Requisito": "La residencia debe tener un sistema ordenado de gestión documental accesible."},
    {"Bloque": "Documentación e información", "Subbloque": "Evaluación de la calidad", "Requisito": "Debe realizarse evaluación anual de la calidad asistencial con indicadores definidos."},
    {"Bloque": "Documentación e información", "Subbloque": "Carta de servicios", "Requisito": "El centro debe tener una carta de servicios clara, accesible y disponible para residentes y familiares."},
    {"Bloque": "Documentación e información", "Subbloque": "Planes de contingencia", "Requisito": "Debe existir un plan de contingencia actualizado para emergencias sanitarias o estructurales."},
    {"Bloque": "Seguridad y accesibilidad", "Subbloque": "Plan de emergencia y autoprotección", "Requisito": "El centro debe disponer de un plan de emergencia vigente y conocido por el personal."},
    {"Bloque": "Seguridad y accesibilidad", "Subbloque": "Información y señalización", "Requisito": "Las rutas de evacuación deben estar claramente señalizadas."},
    {"Bloque": "Resultados de la atención en las personas", "Subbloque": "Plan personal de atención y apoyo al proyecto de vida", "Requisito": "Cada residente debe contar con un plan personalizado de atención."},
    {"Bloque": "Resultados de la atención en las personas", "Subbloque": "Actividades significativas y participación", "Requisito": "El centro debe ofrecer actividades adaptadas y significativas para los residentes."},
    {"Bloque": "Resultados de la atención en las personas", "Subbloque": "Relaciones con el ámbito familiar", "Requisito": "Debe facilitarse la relación e implicación de las familias en la atención."},
    {"Bloque": "Resultados de la atención en las personas", "Subbloque": "Atención libre de sujeciones", "Requisito": "Se debe garantizar una atención sin sujeciones físicas o químicas salvo prescripción clínica."},
    {"Bloque": "Resultados de la atención en las personas", "Subbloque": "Prevención de la malnutrición", "Requisito": "El centro debe aplicar protocolos de detección y prevención de la malnutrición."},
    {"Bloque": "Resultados de la atención en las personas", "Subbloque": "Comité de Ética Asistencial", "Requisito": "Debe constituirse un comité de ética que asesore sobre casos complejos de atención."}
]

# --- Inicialización de datos de evaluación ---
def iniciar_evaluacion():
    return [
        {
            "requisito": item["Requisito"],
            "cumplimiento": "Pendiente",
            "observaciones": ""
        }
        for item in datos_requisitos
    ]

# --- Generar informe PDF ---
def generar_pdf(nombre_centro, evaluacion):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Informe de evaluación - {nombre_centro}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for i, (dato, eval_) in enumerate(zip(datos_requisitos, evaluacion)):
        pdf.multi_cell(0, 8, f"{i+1}. [{eval_['cumplimiento']}] {dato['Bloque']} > {dato['Subbloque']}\n- {dato['Requisito']}\nObs: {eval_['observaciones']}", border=0)
        pdf.ln(2)

    pdf_path = f"informe_{nombre_centro.replace(' ', '_').lower()}.pdf"
    pdf.output(pdf_path)
    return pdf_path

# --- Interfaz ---
st.set_page_config(page_title="Evaluación Orden 2680/2024", layout="wide")
st.title("📋 Evaluación de Cumplimiento - Orden 2680/2024")

centro = st.text_input("Nombre del centro:", "Residencia Ejemplo")
nombre_archivo = f"evaluacion_{centro.replace(' ', '_').lower()}.json"

if os.path.exists(nombre_archivo):
    if st.button("📂 Cargar evaluación existente"):
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            st.session_state.evaluacion = json.load(f)
        st.success("Evaluación cargada correctamente.")

if "evaluacion" not in st.session_state:
    st.session_state.evaluacion = iniciar_evaluacion()

bloques = sorted(set([item["Bloque"] for item in datos_requisitos]))
bloque_sel = st.selectbox("Selecciona un bloque temático:", bloques)

for idx, item in enumerate([r for r in datos_requisitos if r["Bloque"] == bloque_sel]):
    st.markdown(f"### ✅ Requisito {idx + 1}")
    st.markdown(f"**Subbloque:** {item['Subbloque']}")
    st.markdown(f"**Requisito:** {item['Requisito']}")

    cumplimiento = st.radio(
        f"Estado del requisito {idx + 1}",
        ["Cumplido", "No cumplido", "No aplica", "Pendiente"],
        key=f"cumplimiento_{idx}"
    )

    observaciones = st.text_area(
        f"Observaciones (opcional) - Requisito {idx + 1}",
        key=f"observaciones_{idx}"
    )

    st.session_state.evaluacion[idx]["cumplimiento"] = cumplimiento
    st.session_state.evaluacion[idx]["observaciones"] = observaciones

if st.button("⭳ Exportar evaluación a JSON"):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(st.session_state.evaluacion, f, indent=2, ensure_ascii=False)
    st.success(f"Evaluación exportada como '{nombre_archivo}'")

if st.button("🧾 Generar informe PDF"):
    pdf_file = generar_pdf(centro, st.session_state.evaluacion)
    with open(pdf_file, "rb") as f:
        st.download_button("📄 Descargar informe PDF", f, file_name=pdf_file, mime="application/pdf")
