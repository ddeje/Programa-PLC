# Solución Técnica: NodeIds Personalizados en Optix OPC UA

## Problema
El Gateway Jetson (Cliente) requiere un esquema de direccionamiento OPC UA rígido:
- **Namespace Index**: `4`
- **Formato NodeId**: `String` (ej: `s=EgComIn_Heartbeat`)
- **Estructura**: Plana o con prefijos específicos, no el path completo por defecto.

FactoryTalk Optix actualmente expone tags con GUIDs generados por defecto (ej: `ns=9;g=...`).

## Estrategia de Solución
No podemos modificar el Cliente Jetson. Debemos configurar Optix para cumplir con sus expectativas.

### 1. Configuración de Namespace
En OPC UA, los índices de cliente dependen del orden de los namespaces en la tabla del servidor.
- **Mejor Práctica**: Los clientes deberían resolver vía Namespace URI.
- **Workaround para Cliente Rígido**: Debemos asegurar que el namespace relevante aparezca en el índice 4.
    - Nota: Índices 0, 1, 2 usualmente están reservados.
    - Debemos verificar qué ocupa los índices 0-3 e intentar "anclar" nuestro namespace al 4.
    - **Estrategia Alternativa**: Usar una URI específica que el cliente *podría* estar resolviendo al índice 4, o asegurar que sea el 5to cargado.

### 2. Custom NodeIds (Aliases)
Para lograr `s=EgComIn_Heartbeat` en lugar de `s=Path.To.Deep.Variable`:
- Crearemos una carpeta dedicada **"InterfaceJetson"** en el Modelo Optix.
- Crearemos nodos **Alias** o **Variable** en esta carpeta que:
    - Apunten a los tags reales del PLC.
    - Tengan su `NodeId` configurado manualmente (si la UI de Optix lo permite).
    - O usar un `BrowseName` específico que genere el ID string deseado combinado con un "NodeManager" personalizado.

**Solución a Nivel de Código (NetLogic)**:
Si la UI no permite configurar NodeIds string arbitrarios fácilmente, usaremos un script **NetLogic** para registrar nodos con IDs específicos.

## Pasos de Implementación Propuestos (Para el Usuario)

### Paso 1: Crear Estructura de Interfaz
En Optix Studio:
1.  Ir a `Model`.
2.  Crear una carpeta llamada `edgegateway`.
3.  Agregar variables coincidiendo con la lista de "Tags Requeridos".
    - `EgComIn_Heartbeat` (Boolean)
    - `EgComIn_RecordNotFound` (Boolean)
    - etc.

### Paso 2: Enlazar al PLC
1.  Vincular el `Value` de estas nuevas variables a los tags reales del PLC (ej: `CommDrivers/RAEtherNet_IPDriver1/Tags/Programming/EdgeGateway/...`).

### Paso 3: Configurar Servidor OPC UA
1.  En `OPC UA > Server > Settings`:
    - Verificar los **NamespaceUris**. Agregar uno nuevo si es necesario, ej: `http://syngenta.com/jetson`.
    - Queremos que este quede mapeado al índice 4.
2.  **Configuración de NodeId**:
    - Seleccionar la carpeta `edgegateway`.
    - Buscar propiedades "NodeId" en el panel de Propiedades.
    - **Acción Clave**: Usar funcionalidad de **"Custom NodeManager"** o **"Alias"** si los nodos estándar no soportan IDs String personalizados.

### Paso 4: Verificación
Proporcionaremos un script de Python para verificar el arreglo inmediatamente.

## Plan de Verificación

### Prueba Automatizada
Ejecutar script python `verify_optix_config.py` (será creado) que:
1.  Se conecta al Servidor OPC UA Optix.
2.  Busca explícitamente `ns=4;s=EgComIn_Heartbeat`.
3.  Reporta Éxito/Fallo.

### Verificación Manual
1.  Lanzar Emulador Optix.
2.  Ejecutar el script Python.
3.  Revisar logs del Jetson (si hay acceso SSH/Docker).
