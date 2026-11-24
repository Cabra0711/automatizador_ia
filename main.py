"""
Pipeline Principal de Automatización - Talento Andino S.A.S.
Integra las Misiones 1, 2 y 3 en una sola ejecución orquestada.
Diseñado para ser ejecutado directamente o invocado por Power Automate.
"""

import sys
import os
import time
from datetime import datetime

# Importar las fases
from mision1_db import start_db, cargar_y_limpiar_empleados, cargar_solicitudes, ejecutar_consultas
from mision2_festivos import obtener_festivos
from mision3_ia import ejecutar_mision3

LOG_FILE = "pipeline_execution.log"

def log_mensaje(mensaje: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"
    print(linea)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")

def main():
    inicio_tiempo = time.time()
    log_mensaje("=== INICIANDO PIPELINE COMPLETO DE TALENTO ANDINO ===")
    
    try:
        # FASE 1: Datos y SQL (Misión 1)
        log_mensaje("[Fase 1/3] Iniciando base de datos SQLite y limpieza de datos...")
        conexion = start_db()
        cargar_y_limpiar_empleados(conexion)
        cargar_solicitudes(conexion)
        ejecutar_consultas(conexion)
        conexion.close()
        log_mensaje("[Fase 1/3] OK - Base de datos creada y consultas guardadas.")

        # FASE 2: API REST de Festivos (Misión 2)
        log_mensaje("[Fase 2/3] Obteniendo festivos colombianos (Nager.Date API)...")
        festivos = obtener_festivos()
        log_mensaje(f"[Fase 2/3] OK - Festivos cargados: {len(festivos)} fechas.")

        # FASE 3: Enmascaramiento, IA y Revisión Humana (Misión 3)
        log_mensaje("[Fase 3/3] Clasificando con IA, validando reglas y generando reporte...")
        reporte, metricas = ejecutar_mision3()
        log_mensaje(f"[Fase 3/3] OK - Exactitud: {metricas['exactitud_porcentaje']}% | Reporte generado con {len(reporte)} filas.")

        # Verificación de entregable final
        if not os.path.exists("reporte_solicitudes.csv"):
            raise FileNotFoundError("El archivo reporte_solicitudes.csv no fue generado.")

        duracion = round(time.time() - inicio_tiempo, 2)
        log_mensaje(f"=== PIPELINE FINALIZADO CON ÉXITO EN {duracion}s ===")
        sys.exit(0)

    except Exception as e:
        log_mensaje(f"FATAL ERROR durante el pipeline: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
