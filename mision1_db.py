import json
import sqlite3
import os
import csv

DB_NAME = "talento_andino.db"

def start_db():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("DROP TABLE IF EXISTS solicitudes")
    cursor.execute("DROP TABLE IF EXISTS empleados")
    #ejecutar consultas SQL y crear tablas de datos para el pipeline ETL
    cursor.execute("CREATE TABLE empleados(id_empleado TEXT PRIMARY KEY, nombre TEXT , correo TEXT, area TEXT, cargo TEXT, fecha_ingreso DATE, dias_vacaciones_disponibles INTEGER, documento TEXT)")
    cursor.execute("CREATE TABLE solicitudes(id_solicitud TEXT PRIMARY KEY ,id_empleado TEXT NOT NULL ,fecha_recepcion DATE NOT NULL ,canal TEXT NOT NULL ,texto TEXT NOT NULL ,etiqueta_esperada TEXT NOT NULL)")
    connect.commit()
    return connect

def cargar_y_limpiar_empleados(connect):
    cursor = connect.cursor()
    ids_vistos = set()
    log_limpieza = []

    with open('empleados.csv', mode="r", encoding="utf-8" ) as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            emp_id = fila["id_empleado"].strip()
            
            if emp_id in ids_vistos:
                mensaje = f"Duplicado que ha sido omitido: {emp_id}"
                log_limpieza.append(mensaje)
                continue

            ids_vistos.add(emp_id)
            correo_orig = fila["correo"]
            correo_limpio = correo_orig.strip().lower()
            if correo_orig != correo_limpio:
                log_limpieza.append(f"El correo se ha sido cambiado y se limpio correctamente{correo_limpio}")

            area_limpia = fila["area"].strip()
            if not area_limpia:
                area_limpia = "Sin Asignar"
                log_limpieza.append(area_limpia)
            cursor.execute("INSERT INTO empleados VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (emp_id, fila["nombre"].strip(), correo_limpio, area_limpia, fila["cargo"].strip(), fila["fecha_ingreso"].strip(), int(fila["dias_vacaciones_disponibles"]), fila["documento"].strip()) )
    connect.commit()

def cargar_solicitudes(connect):
    cursor = connect.cursor()
    with open('solicitudes.json', mode="r", encoding="utf-8") as solicitudes:
        lector = json.load(solicitudes)
        for fila in lector:
            cursor.execute("INSERT INTO solicitudes VALUES (?, ?, ?, ?, ?, ?)",(
                fila["id_solicitud"].strip(),
                fila["id_empleado"].strip(),
                fila["fecha_recepcion"].strip(),
                fila["canal"].strip(),
                fila["texto"].strip(),
                fila["etiqueta_esperada"].strip()
            ))
    connect.commit()

def ejecutar_consultas(connect):
    os.makedirs("resultados_sql", exist_ok=True)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT 
            s.etiqueta_esperada AS categoria,
            COALESCE(e.area, 'Empleado no registrado') AS area,
            COUNT(*) AS total_solicitudes
        FROM solicitudes s
        LEFT JOIN empleados e ON s.id_empleado = e.id_empleado
        GROUP BY s.etiqueta_esperada, area
        ORDER BY total_solicitudes DESC
    """)
    res_a = [{"categoria": r[0], "area": r[1], "total": r[2]} for r in cursor.fetchall()]

    
    cursor.execute("""
        SELECT s.id_solicitud, s.id_empleado, s.fecha_recepcion, s.texto
        FROM solicitudes s
        LEFT JOIN empleados e ON s.id_empleado = e.id_empleado
        WHERE e.id_empleado IS NULL
    """)
    res_b = [{"id_solicitud": r[0], "id_empleado": r[1], "fecha": r[2], "texto": r[3]} for r in cursor.fetchall()]

    
    cursor.execute("""
        SELECT id_empleado, nombre, area, dias_vacaciones_disponibles
        FROM empleados
        WHERE dias_vacaciones_disponibles < 5
    """)
    res_c = [{"id_empleado": r[0], "nombre": r[1], "area": r[2], "dias_disponibles": r[3]} for r in cursor.fetchall()]

    resultados = {
        "a_solicitudes_por_categoria_y_area": res_a,
        "b_solicitudes_empleados_inexistentes": res_b,
        "c_empleados_menos_de_5_dias": res_c
    }

    with open("resultados_sql/consultas_mision1.json", mode="w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print("\n=== RESULTADOS DE CONSULTAS SQL GUARDADOS EN resultados_sql/consultas_mision1.json ===")
    print(json.dumps(resultados, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    conexion = start_db()
    cargar_y_limpiar_empleados(conexion)
    cargar_solicitudes(conexion)
    ejecutar_consultas(conexion)
    conexion.close()



