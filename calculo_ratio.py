#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def solicitar_horas_semanales(categorias):
    """
    Solicita al usuario las horas semanales para cada categoría
    y devuelve un diccionario con la categoría como clave y
    las horas semanales como valor.
    """
    horas_semanales = {}
    for cat in categorias:
        while True:
            try:
                valor = input(f"Ingrese las horas semanales para '{cat}': ")
                horas = float(valor.replace(",", "."))
                if horas < 0:
                    print("Error: Las horas semanales no pueden ser negativas.")
                    continue
                horas_semanales[cat] = horas
                break
            except ValueError:
                print("Error: Introduce un valor numérico válido.")
    return horas_semanales

def calcular_equivalentes_jornada_completa(horas_semanales):
    """
    Convierte las horas semanales en equivalentes a jornada completa.
    """
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    return horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA

def main():
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
    
    print("=== Cálculo de Ratio de Personal - Comunidad de Madrid ===")
    print("Se solicitarán las horas semanales (por fichaje) para cada categoría.\n")
    
    # Solicitar horas semanales
    print("-> Horas semanales de Atención Directa")
    horas_directas = solicitar_horas_semanales(categorias_directas)
    
    print("\n-> Horas semanales de Atención No Directa")
    horas_no_directas = solicitar_horas_semanales(categorias_no_directas)
    
    # Solicitar la ocupación media
    while True:
        try:
            ocupacion_str = input("\nIngrese la ocupación media (número de residentes): ")
            ocupacion = float(ocupacion_str.replace(",", "."))
            if ocupacion <= 0:
                print("La ocupación debe ser mayor que cero.")
            else:
                break
        except ValueError:
            print("Error: Introduce un valor numérico válido.")
    
    if ocupacion == 0:
        print("Error: La ocupación no puede ser cero. Fin del programa.")
        return
    
    # Cálculo de equivalentes a jornada completa
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in horas_directas.values())
    total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in horas_no_directas.values())
    
    # Cálculo de ratios
    ratio_directa = (total_eq_directa / ocupacion) * 100
    ratio_no_directa = (total_eq_no_directa / ocupacion) * 100
    
    # Mostrar resultados
    print("\n=== Resultados del Cálculo de Ratios ===")
    print(f"Atención Directa  -> Total EQ: {total_eq_directa:,.2f} | Ratio: {ratio_directa:,.2f} por cada 100 residentes")
    print(f"Atención No Directa -> Total EQ: {total_eq_no_directa:,.2f} | Ratio: {ratio_no_directa:,.2f} por cada 100 residentes")
    
    # Verificación de cumplimiento
    ratio_directa_por_residente = ratio_directa / 100
    ratio_no_directa_por_residente = ratio_no_directa / 100
    
    print("\n=== Verificación de cumplimiento con la CAM ===")
    if ratio_directa_por_residente >= 0.47:
        print(f"- Atención Directa: ✅ OK (>= 0,47). Ratio: {ratio_directa_por_residente:.2f}")
    else:
        print(f"- Atención Directa: ❌ NO CUMPLE (< 0,47). Ratio: {ratio_directa_por_residente:.2f}")
    
    if ratio_no_directa_por_residente >= 0.15:
        print(f"- Atención No Directa: ✅ OK (>= 0,15). Ratio: {ratio_no_directa_por_residente:.2f}")
    else:
        print(f"- Atención No Directa: ❌ NO CUMPLE (< 0,15). Ratio: {ratio_no_directa_por_residente:.2f}")

if __name__ == "__main__":
    main()