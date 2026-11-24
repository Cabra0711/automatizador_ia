# Diseño de Arquitectura: Power Automate en la Nube (Opción B y C)
## Talento Andino S.A.S. — Sistema de Automatización de Solicitudes con IA y Human-in-the-Loop

---

### 1. Resumen Ejecutivo
Para dar cumplimiento a la **Misión 4 (Opción B y C)**, este documento presenta el diseño técnico integral de la orquestación en la nube mediante **Power Automate Cloud**. El flujo se activa ante la llegada de nuevas solicitudes (vía correo de RRHH o archivo en SharePoint/OneDrive), orquesta la ejecución del pipeline con IA, analiza los resultados estructurados y canaliza automáticamente las solicitudes que requieren revisión humana hacia los analistas de Recursos Humanos mediante **Adaptive Cards en Microsoft Teams** o correos interactivos de Outlook.

---

### 2. Diagrama de Flujo del Proceso en la Nube (Mermaid Flowchart)

```mermaid
flowchart TD
    Start([Disparador: Nuevo correo en rrhh@talentoandino.com o Archivo en SharePoint]) --> ReadInput[Paso 1: Extraer cuerpo del mensaje y adjuntos]
    ReadInput --> InvokePipeline[Paso 2: Invocar Azure Function / Webhook Python Pipeline]
    
    subgraph Core_Pipeline["Pipeline Python & IA"]
        InvokePipeline --> ETL[Misión 1: Ingesta y Limpieza SQLite]
        ETL --> HolAPI[Misión 2: Consulta Festivos Nager.Date]
        HolAPI --> AIModel[Misión 3: Enmascaramiento y Clasificación Gemini LLM]
        AIModel --> RulesCheck[Misión 3: Validación Reglas de Negocio]
        RulesCheck --> GenReport[Generar reporte_solicitudes.json y CSV]
    end
    
    GenReport --> ReceiveOutput[Paso 3: Power Automate recibe JSON procesado]
    ReceiveOutput --> ParseJSON[Paso 4: Parse JSON con esquema de validación]
    ParseJSON --> ForEachItem[Paso 5: Bucle 'Apply to each' por solicitud]
    
    ForEachItem --> ConditionReview{¿Requiere revisión humana == 'Sí'?}
    
    ConditionReview -- Sí --> SendAdaptiveCard[Paso 6A: Enviar Adaptive Card a Teams / Correo RRHH con Motivo]
    SendAdaptiveCard --> WaitApproval[Esperar decisión del Analista de RRHH: Aprobar / Rechazar]
    WaitApproval --> UpdateDB[Paso 6B: Registrar decisión y comentarios en SQLite / Dataverse]
    WaitApproval --> NotifyEmployee[Paso 6C: Notificar resultado al empleado solicitante]
    
    ConditionReview -- No --> AutoApprove[Paso 7A: Aprobación Directa y Registro automático]
    AutoApprove --> SendConfirmation[Paso 7B: Enviar confirmación al empleado por Correo/Teams]
    
    NotifyEmployee --> EndFlow([Fin del Flujo])
    SendConfirmation --> EndFlow
    
    subgraph Error_Handling["Manejo de Errores (Scope Try-Catch)"]
        InvokePipeline -. Error .-> CatchScope[Paso Error: Capturar Excepción]
        CatchScope --> AlertIT[Notificar a Soporte TI con Stack Trace y ExitCode]
        AlertIT --> LogAudit[Escribir en Log de Auditoría Cloud]
    end
```

---

### 3. Diagrama de Secuencia (Interacción de Componentes)

```mermaid
sequenceDiagram
    autonumber
    actor Empleado
    participant Mail as Correo / Formulario RRHH
    participant PAC as Power Automate Cloud
    participant Engine as Pipeline Python (Azure Function / Host)
    participant Gemini as Gemini AI API
    actor RRHH as Analista de RRHH
    
    Empleado->>Mail: Envía solicitud (ej. vacaciones 21-31 dic)
    Mail->>PAC: Disparador: 'When a new email arrives'
    PAC->>Engine: HTTP POST /procesar_solicitud (Payload)
    Note over Engine: Enmascaramiento de datos personales
    Engine->>Gemini: Prompt JSON con texto anonimizado
    Gemini-->>Engine: JSON estructurado (VACACIONES, fechas)
    Note over Engine: Validación festivos y saldo en SQLite
    Engine-->>PAC: Retorna JSON resultado (requiere_revision: 'Sí', motivo)
    
    alt Requiere Revisión == 'Sí'
        PAC->>RRHH: Adaptive Card en MS Teams con motivo de objeción
        RRHH->>PAC: Acción: Rechazar o Ajustar Fechas
        PAC->>Empleado: Notificación con decisión y explicación de RRHH
    else Aprobación Automática == 'No'
        PAC->>Empleado: Confirmación automática de solicitud tramitada
    end
```

---

### 4. Especificación Detallada de Pasos del Flujo

#### Disparador (Trigger)
- **Opción Correo**: `When a new email arrives (V3)`
  - *Buzón compartido*: `rrhh@talentoandino.com`
  - *Filtro de asunto*: `[Solicitud RRHH]`
- **Opción Archivo**: `When a file is created in a folder (SharePoint / OneDrive)`
  - *Carpeta*: `/TalentoAndino/Solicitudes_Entrantes/`

#### Acción 1: Invocación del Pipeline (HTTP Connector / Azure Automation)
- **Método**: `POST`
- **URI**: `https://api.talentoandino.com/api/v1/pipeline/procesar`
- **Headers**: `Content-Type: application/json`, `X-API-KEY: @{parameters('SecretToken')}`
- **Body**: `@triggerOutputs()?['body']`

#### Acción 2: Parse JSON (Esquema de Validación)
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "empleado": { "type": "string" },
      "area": { "type": "string" },
      "categoria": { "type": "string" },
      "confianza": { "type": "number" },
      "fechas": { "type": "string" },
      "dias_habiles": { "type": "integer" },
      "saldo_suficiente": { "type": "string" },
      "requiere_revision": { "type": "string" },
      "motivo": { "type": "string" }
    },
    "required": ["id", "categoria", "requiere_revision", "motivo"]
  }
}
```

#### Acción 3: Condición y Enrutamiento Human-in-the-Loop
- **Condición**: `items('Apply_to_each')?['requiere_revision']` es igual a `'Sí'`
- **Acción Sí**:
  - Enviar Adaptive Card a Microsoft Teams (Canal *RRHH - Casos Pendientes*):
    - Título: `⚠️ Caso en Revisión: Solicitud @{items('Apply_to_each')?['id']}`
    - Campos visibles: Empleado, Área, Categoría, Días Hábiles, Motivo del Flag.
    - Botones de acción: `[Aprobar Excepcionalmente]`, `[Rechazar Solicitud]`, `[Solicitar Aclaración al Empleado]`.
- **Acción No**:
  - Actualizar sistema nómina / Enviar email de confirmación automática.

---

### 5. Estrategia de Manejo de Errores (Scope Try / Catch / Finally)
1. **Scope Try**: Contiene la llamada HTTP, la serialización JSON y la escritura de logs.
2. **Scope Catch** (configurado con `runAfter: has failed, has timed out`):
   - Captura el error devuelto por la API o el entorno de ejecución.
   - Envía notificación crítica a `soporte.ti@talentoandino.com` con el identificador de ejecución (`workflow().run.id`).
   - Escribe en una lista de SharePoint de errores de auditoría.
3. **Scope Finally**: Registra métricas de tiempo de ejecución y cantidad de solicitudes procesadas.
