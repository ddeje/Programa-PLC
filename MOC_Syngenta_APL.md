# Método de Control Operacional (MOC)
## Syngenta Corn Processing Control System (APL)

**Fecha:** 02 de Diciembre, 2025
**Sistema:** Simulador de Procesamiento de Maíz (APL)
**Ubicación:** Planta de Procesamiento

---

### 1. Propósito y Alcance
Este documento establece los procedimientos operativos estándar para el control seguro y eficiente del flujo de material en la línea de procesamiento de maíz, desde la entrada (Sheller) hasta la salida final, pasando por las etapas de Vmek y Tratamiento (Treater).

### 2. Descripción del Sistema
El sistema es una línea de procesamiento automatizada con control centralizado.
*   **Etapas del Proceso:**
    1.  **Input / Sheller:** Recepción y escaneo de lotes.
    2.  **Vmek Hopper:** Tolva intermedia.
    3.  **Treater Hopper:** Tolva de tratamiento químico.
    4.  **Final Output:** Salida del producto terminado.
*   **Mecanismo de Control:** 3 Compuertas (Gates) controladas digitalmente.
*   **Roles:**
    *   **Operador (Input Station):** Responsable de escanear y confirmar nuevos lotes.
    *   **Receiver (Control Room):** Responsable del flujo global, operación de compuertas y monitoreo.

### 3. Responsabilidades y Roles

| Rol | Responsabilidades Clave |
| :--- | :--- |
| **Receiver (Control Maestro)** | • Iniciar/Detener el sistema (Start/Stop).<br>• Controlar el flujo de material ("Process Next").<br>• Operar compuertas manualmente si es necesario.<br>• Monitorear el estado de todas las tolvas. |
| **Operador (Input)** | • Escanear nuevos grupos de material.<br>• Confirmar la integridad del lote antes de liberarlo.<br>• Asegurar que la entrada no esté bloqueada. |

### 4. Procedimientos Operativos

#### 4.1. Arranque del Sistema (Start-up)
1.  Verificar que no haya condiciones de alarma activas.
2.  El **Receiver** debe presionar el botón **"START"** en el panel de control.
3.  Confirmar que el indicador de estado cambie a **"SYSTEM ACTIVE"** (verde).
4.  Verificar que el log del sistema indique: *"System Started. Receiver active and controlling flow."*

#### 4.2. Ingreso de Material (Input Station)
1.  El **Operador** verifica que la etapa "Input / Sheller" esté vacía.
2.  Presionar el botón **"1. Scan Group"**.
    *   *El sistema generará un ID de lote único (ej. MAT-123).*
    *   *El estado cambiará a "Pending" (amarillo).*
3.  El Operador verifica los datos y presiona **"2. Confirm & Release"**.
    *   *El lote queda confirmado y listo para ser procesado por el Receiver.*

#### 4.3. Procesamiento y Transferencia (Flujo Normal)
El flujo es controlado por el **Receiver** utilizando el botón inteligente **"Process Next Material"**.

1.  **Transferencia Input → Vmek (Gate 1):**
    *   Condición: Input tiene material confirmado Y Vmek está vacío.
    *   Acción: Receiver activa Gate 1.
2.  **Transferencia Vmek → Treater (Gate 2):**
    *   Condición: Vmek tiene material Y Treater está vacío.
    *   Acción: Receiver activa Gate 2.
3.  **Transferencia Treater → Output (Gate 3):**
    *   Condición: Treater tiene material Y Output está vacío.
    *   Acción: Receiver activa Gate 3.

#### 4.4. Parada del Sistema (Shutdown)
1.  El **Receiver** presiona el botón **"STOP"**.
2.  Todas las compuertas (Gates 1, 2 y 3) se cerrarán automáticamente por seguridad.
3.  El estado cambiará a **"SYSTEM STOPPED"** (rojo).
4.  Los controles de operación se bloquearán.

### 5. Interlocks y Seguridad (Lógica de Control)

El sistema cuenta con las siguientes protecciones automáticas (Interlocks) para prevenir errores:

*   **Protección de Sobrellenado (Destination Full):** No se puede abrir una compuerta si la etapa de destino ya tiene material.
*   **Protección de Vacío (Source Empty):** No se puede abrir una compuerta si la etapa de origen no tiene material.
*   **Bloqueo de Confirmación:** El material en la entrada no puede moverse hasta que el Operador lo haya confirmado ("Confirm Scan").
*   **Parada de Emergencia:** Al presionar STOP, todo el flujo se detiene inmediatamente.

### 6. Manejo de Anormalidades

| Condición | Acción Requerida |
| :--- | :--- |
| **"Input Occupied"** | El Operador intenta escanear pero ya hay material. Debe esperar a que el Receiver mueva el material actual. |
| **"Destination Full"** | El Receiver intenta mover material pero la siguiente tolva está llena. Debe vaciar la tolva siguiente primero (flujo hacia adelante). |
| **Falla de Energía** | El sistema regresa al estado "STOPPED" por defecto al reiniciar. |

### 7. Sistema de Asistencia (AI)
El sistema cuenta con un asistente "Syngenta AI" integrado.
*   **Uso:** Consultar dudas sobre el estado actual o procedimientos.
*   **Configuración:** Requiere API Key de Gemini configurada en el menú de ajustes (⚙️).

---
*Documento generado automáticamente para Syngenta APL System.*
