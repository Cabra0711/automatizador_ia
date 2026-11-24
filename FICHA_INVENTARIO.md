# Ficha de Inventario de Automatización
## Talento Andino S.A.S. — Sistema de Clasificación y Gestión de Solicitudes RRHH

| Campo | Detalle |
| :--- | :--- |
| **Nombre de la Automatización** | Sistema Automatizado de Recepción, Clasificación con IA y Auditoría de Solicitudes de RRHH |
| **Código Interno** | AUT-RRHH-2026-001 |
| **Versión** | 1.0.0 (Producción / Release Candidate) |
| **Fecha de Inventario** | Noviembre 2026 |
| **Líder de Negocio (Product Owner)** | Gerencia de Talento Humano — Talento Andino S.A.S. |
| **Líder Técnico / Desarrollador** | Automatizador de Inteligencia Artificial (RPA & AI Engineer) |
| **Área Operativa** | Recursos Humanos / Nómina y Compensación |

---

### 1. Propósito y Alcance del Proceso
Automatizar el ciclo de vida de recepción, enmascaramiento de datos personales, clasificación semántica inteligente, extracción de fechas y auditoría de reglas de negocio para solicitudes de empleados (Vacaciones, Incapacidades, Certificados Laborales, Actualizaciones de Datos y Consultas Generales), implementando un enfoque de **Human-in-the-Loop** para derivar a revisión manual únicamente los casos atípicos o que incumplan políticas organizacionales.

---

### 2. Disparador (Trigger)
- **Modo Asistido / Batch Local (Opción A - Actual)**: Ejecución programada vía Power Automate para escritorio o ejecución por lotes (`ejecutar_pipeline.bat` / `main.py`).
- **Modo Continuo / Event-Driven (Opción B/C - Nube)**: 
  - Recepción de correo electrónico entrante en el buzón compartido `rrhh@talentoandino.com`.
  - Carga de archivo consolidado de novedades en SharePoint / OneDrive (`/Solicitudes_Entrantes/`).

---

### 3. Entradas (Inputs)
1. **`empleados.csv`**:
   - Maestro de colaboradores (ID, Nombre, Correo, Área, Cargo, Fecha de Ingreso, Días Disponibles de Vacaciones, Documento).
   - Incluye controles de limpieza: eliminación de registros duplicados, normalización de correos electrónicos y asignación por defecto a campos de área vacíos.
2. **`solicitudes.json`**:
   - Registro de interacciones entrantes vía correo, formulario web y chat.
   - Atributos: ID de solicitud, ID de empleado, fecha de recepción, canal de recepción, texto en lenguaje natural y categoría de referencia.
3. **API REST Festivos Colombia (Nager.Date)**:
   - Endpoint: `https://date.nager.at/api/v3/PublicHolidays/2026/CO`.
   - Backup local: `festivos_2026_backup.json` (tolerancia a fallos de red).
4. **Google Gemini LLM (Opcional vía API Key)**:
   - Procesamiento semántico con enmascaramiento previo de privacidad.

---

### 4. Salidas (Outputs)
1. **`talento_andino.db`**: Base de datos SQLite normalizada con tablas indexadas `empleados` y `solicitudes`.
2. **`reporte_solicitudes.csv`** y **`reporte_solicitudes.json`**:
   - Reporte estructurado para RRHH con 10 columnas obligatorias:
     `id`, `empleado`, `area`, `categoria`, `confianza`, `fechas`, `dias_habiles`, `saldo_suficiente`, `requiere_revision`, `motivo`.
3. **`resultados_sql/consultas_mision1.json`**:
   - Reporte analítico de solicitudes por categoría y área, empleados no registrados en nómina y colaboradores con saldo crítico de vacaciones (< 5 días).
4. **`pipeline_execution.log`** y **`ejecucion_log.txt`**: Trazabilidad completa con marcas de tiempo (timestamp) y códigos de estado.
5. **Notificaciones / Alertas**: Mensajes emergentes en pantalla (PAD) o Adaptive Cards en Teams con botones de acción para analistas de RRHH.

---

### 5. Reglas de Negocio y Criterios de Revisión Humana
La inteligencia artificial jamás autoriza unilateralmente una solicitud que vulnere las políticas corporativas. Se elevan automáticamente a **Revisión Humana obligatoria (`requiere_revision = 'Sí'`)** bajo los siguientes criterios:
1. **Empleado Inexistente**: Solicitante con identificador no hallado en la nómina activa de la compañía.
2. **Saldo Insuficiente de Vacaciones**: Colaborador que solicita más días hábiles de los que tiene legalmente acumulados.
3. **Vacaciones sin Fechas**: Peticiones ambiguas de descanso sin rangos cronológicos precisos.
4. **Baja Confianza en la Clasificación**: Estimación del modelo por debajo del 80% (`confianza < 0.80`).
5. **Categoría No Estándar**: Peticiones catalogadas como `OTRO` que requieren gestión personalizada de bienestar o relaciones laborales.

---

### 6. Matriz de Riesgos y Controles

| Riesgo Identificado | Severidad | Probabilidad | Control Implementado |
| :--- | :---: | :---: | :--- |
| **Fuga o exposición de datos personales sensibles (Habeas Data)** | Alta | Baja | Módulo de enmascaramiento previo (`regex`) que anonimiza cédulas, celulares y correos antes de enviar cualquier texto al modelo de IA externo. |
| **Indisponibilidad de la API pública de festivos** | Media | Media | Mecanismo de reintentos exponenciales con persistencia en caché local (`festivos_2026_backup.json`). |
| **Agotamiento de cuota o indisponibilidad de API de IA** | Media | Media | Arquitectura desacoplada con motor heurístico resiliente de respaldo que garantiza 100% de continuidad operacional. |
| **Aprobación errónea de vacaciones sin saldo** | Alta | Baja | Validación cruzada obligatoria en backend entre el cálculo de días hábiles y el saldo registrado en base de datos. |
| **Exposición involuntaria de secretos o credenciales** | Crítica | Baja | Gestión de credenciales mediante `.env`, `.env.example` y exclusión estricta en `.gitignore`. |

---

### 7. Monitoreo, Soporte y Auditoría
- **Logs de Auditoría**: Archivos `ejecucion_log.txt` y `pipeline_execution.log` con detalle de cada corrida.
- **SLA de Atención**: Los casos marcados para revisión humana deben ser gestionados por el equipo de RRHH en un plazo máximo de 24 horas hábiles.
- **Canal de Soporte de la Automatización**: Centro de Excelencia RPA & AI (`soporte.automatizacion@talentoandino.com`).

