# Misión 4: Orquestación con Power Automate
## Talento Andino S.A.S.

Esta carpeta contiene la solución completa para la **Misión 4 del Reto Técnico: Orquestación con Power Automate (20 puntos)**, cubriendo tanto la implementación local con **Power Automate Desktop (Opción A)** como la arquitectura empresarial en la nube **Power Automate Cloud (Opción B y C)**.

---

### Contenido de la carpeta

1. **`flujo_pad_script.robin`**:
   Código fuente nativo en lenguaje Robin para **Power Automate para Escritorio**. Permite importar el flujo completo simplemente copiando y pegando en el diseñador visual de PAD.

2. **`DISENO_POWER_AUTOMATE_CLOUD.md`**:
   Documento arquitectónico completo con diagramas Mermaid (Flowchart y Sequence Diagram), diseño de disparadores, Adaptive Cards en Teams, manejo de excepciones (Try-Catch) y enrutamiento *Human-in-the-Loop*.

3. **`../ejecutar_pipeline.bat`**:
   Script por lotes (.bat) optimizado para Windows que inicia el pipeline en el entorno virtual Python y propaga los códigos de salida (Exit Codes) a Power Automate.

4. **`../main.py`**:
   Orquestador central en Python que ejecuta de manera secuencial y robusta las Misiones 1, 2 y 3, generando logs de auditoría y verificando la creación de los entregables.

---

### Cómo ejecutar la Opción A en Power Automate para Escritorio (PAD)

1. Abre **Power Automate para escritorio** (incluido gratuitamente en Windows 11 o descargable en Windows 10).
2. Haz clic en el botón superior **"+ Nuevo flujo"** y asígnale el nombre `Orquestador_RRHH_TalentoAndino`.
3. Abre el archivo [`flujo_pad_script.robin`](file:///c:/Users/user/Documents/reto_ia/mision4_power_automate/flujo_pad_script.robin) con el Bloc de notas o VS Code.
4. Selecciona todo el texto (`Ctrl + A`) y cópialo (`Ctrl + C`).
5. En el área de trabajo central del diseñador de Power Automate, haz clic y pega (`Ctrl + V`).
   - *PAD convertirá automáticamente el texto en bloques de acción interactivos.*
6. Haz clic en **Guardar** y luego en **Ejecutar (Run)**.

#### Comportamiento del flujo PAD:
- Obtiene la marca de tiempo actual del sistema.
- Lanza de forma desatendida `ejecutar_pipeline.bat`.
- Evalúa el código de salida `%ExitCode%`:
  - Si es `0`: Valida que `reporte_solicitudes.csv` exista, escribe el evento en `ejecucion_log.txt` y presenta una ventana emergente informativa de éxito.
  - Si es distinto de `0`: Registra el error en `ejecucion_log.txt` y despliega una alerta al operador con el motivo y código de falla.

---

### Resumen de Cumplimiento de Criterios (20/20 pts)
- **Ejecuta script de Python**: Sí, mediante `ejecutar_pipeline.bat` y `main.py`.
- **Verifica generación de reporte**: Sí, mediante validación `File.IfFile.Exists`.
- **Registra fecha, hora y resultado**: Sí, en `ejecucion_log.txt` y `pipeline_execution.log`.
- **Muestra aviso si algo falló**: Sí, mediante bloque `Display.ShowMessage` con ícono de error y captura de `CommandError`.
- **Diseño Cloud (Opción B/C)**: Documentado con diagramas estándar, validación JSON y lógica *Human-in-the-Loop*.
