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
                horas_semanales[cat] = horas
                break
            except ValueError:
                print("Error: Por favor, introduce un valor numérico válido.")
    return horas_semanales

def calcular_equivalentes_jornada_completa(horas_semanales):
    """
    1) Multiplica las horas semanales por 52,14 para anualizarlas.
    2) Divide el resultado por 1.772 (horas/año a jornada completa).
    Retorna el número de trabajadores equivalentes a jornada completa.
    """
    HORAS_ANUALES_JORNADA_COMPLETA = 1772
    SEMANAS_AL_ANO = 52.14
    horas_anuales = horas_semanales * SEMANAS_AL_ANO
    eq_jornada = horas_anuales / HORAS_ANUALES_JORNADA_COMPLETA
    return eq_jornada

def main():
    # Categorías exigidas por la Comunidad de Madrid
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
    
    # 1. Solicitar horas semanales de atención directa
    print("-> Horas semanales de Atención Directa (personal en contacto directo con el residente)")
    horas_directas = solicitar_horas_semanales(categorias_directas)
    
    # 2. Solicitar horas semanales de atención no directa
    print("\n-> Horas semanales de Atención No Directa (limpieza, cocina, mantenimiento)")
    horas_no_directas = solicitar_horas_semanales(categorias_no_directas)
    
    # 3. Solicitar la ocupación media (nº de residentes)
    while True:
        try:
            ocupacion_str = input("\nIngrese la ocupación media (número de residentes) de la residencia: ")
            ocupacion = float(ocupacion_str.replace(",", "."))
            if ocupacion <= 0:
                print("La ocupación debe ser mayor que cero.")
            else:
                break
        except ValueError:
            print("Error: Por favor, introduce un valor numérico válido.")
    
    # 4. Calcular equivalentes a jornada completa (atención directa)
    total_eq_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in horas_directas.values())
    
    # 5. Calcular equivalentes a jornada completa (atención no directa)
    total_eq_no_directa = sum(calcular_equivalentes_jornada_completa(hs) for hs in horas_no_directas.values())
    
    # 6. Calcular la ratio por cada 100 residentes
    #    ratio = (total_equivalentes / ocupacion) * 100
    ratio_directa = (total_eq_directa / ocupacion) * 100
    ratio_no_directa = (total_eq_no_directa / ocupacion) * 100
    
    # 7. Mostrar resultados
    print("\n=== Resultados del Cálculo de Ratios ===")
    print(f"Atención Directa  -> Total EQ: {total_eq_directa:.2f} | Ratio: {ratio_directa:.2f} por cada 100 residentes")
    print(f"Atención No Directa -> Total EQ: {total_eq_no_directa:.2f} | Ratio: {ratio_no_directa:.2f} por cada 100 residentes")
    
    # 8. Verificación de cumplimiento (ratios mínimas: 0.47 y 0.15)
    ratio_directa_por_residente = ratio_directa / 100
    ratio_no_directa_por_residente = ratio_no_directa / 100
    
    cumple_directa = ratio_directa_por_residente >= 0.47
    cumple_no_directa = ratio_no_directa_por_residente >= 0.15
    
    print("\n=== Verificación de cumplimiento con la CAM ===")
    if cumple_directa:
        print(f"- Atención Directa: OK (>= 0,47). Ratio: {ratio_directa_por_residente:.2f}")
    else:
        print(f"- Atención Directa: NO CUMPLE (< 0,47). Ratio: {ratio_directa_por_residente:.2f}")
    
    if cumple_no_directa:
        print(f"- Atención No Directa: OK (>= 0,15). Ratio: {ratio_no_directa_por_residente:.2f}")
    else:
        print(f"- Atención No Directa: NO CUMPLE (< 0,15). Ratio: {ratio_no_directa_por_residente:.2f}")

if __name__ == "__main__":
    main()