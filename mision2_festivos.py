from datetime import datetime, timedelta
import json
import os
import time 
import requests

URL_API = "https://date.nager.at/api/v3/PublicHolidays/2026/CO"
ARCHIVO_RESPALDO = "festivos_2026_backup.json"

def obtener_festivos(reintentos=3, timeout=5):
    for intento in range(1, reintentos + 1):
        try:
            respuesta = requests.get(URL_API, timeout=timeout)
            respuesta.raise_for_status()
            datos = respuesta.json()
            with open(ARCHIVO_RESPALDO, mode="w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
            return {item["date"] for item in datos}
        except (requests.RequestException, ValueError) as e:
            if intento < reintentos:
                time.sleep(1)
    if os.path.exists(ARCHIVO_RESPALDO):
        with open(ARCHIVO_RESPALDO, mode="r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return {item["date"] for item in datos}
    else:
        raise RuntimeError("No se pudieron obtener los festivos de la API ni del respaldo local.")

def calcular_dias_habiles(fecha_inicio_str, fecha_fin_str, festivos):
    """
    Calcula días hábiles (lunes a viernes, excluyendo festivos) entre dos fechas YYYY-MM-DD (inclusive).
    """
    if not fecha_inicio_str or not fecha_fin_str:
        return 0

    inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()

    if fin < inicio:
        return 0

    dias_habiles = 0
    actual = inicio
    while actual <= fin:
        # weekday(): 0=Lunes ... 4=Viernes, 5=Sábado, 6=Domingo
        if actual.weekday() < 5 and actual.isoformat() not in festivos:
            dias_habiles += 1
        actual += timedelta(days=1)

    return dias_habiles

if __name__ == "__main__":
    festivos_co = obtener_festivos()
    print(f"Total festivos cargados para 2026: {len(festivos_co)}")

    # Validación rápida con los 3 ejemplos del documento (deben dar 5, 4 y 8)
    print("S01 (14 al 18 dic):", calcular_dias_habiles("2026-12-14", "2026-12-18", festivos_co))
    print("S05 (7 al 11 dic):", calcular_dias_habiles("2026-12-07", "2026-12-11", festivos_co))
    print("S06 (21 al 31 dic):", calcular_dias_habiles("2026-12-21", "2026-12-31", festivos_co))