# OPC UA Communication Test Suite

## Propósito
Pruebas básicas de comunicación OPC UA para diagnóstico de problemas identificados en reunión del 4 de diciembre 2025.

## Problemas a Diagnosticar

1. **Namespace Index incorrecto** - El gateway no accede a las variables porque está en el namespace equivocado
2. **Formato de identificadores** - Los NodeId no son legibles o tienen formato incorrecto
3. **Tipos de datos customizados** - OPC UA 1.0.4 tiene problemas con estructuras anidadas

## Requisitos

```bash
# Opción 1: Librería opcua (más simple)
pip install opcua

# Opción 2: Librería asyncua (más moderna, recomendada)
pip install asyncua
```

## Uso Rápido

### 1. Prueba Básica
```bash
python opcua_basic_test.py
```

### 2. Modo Interactivo (para explorar)
```bash
python opcua_basic_test.py -i
```

### 3. Versión Asyncua (moderna)
```bash
python opcua_simple_asyncua.py

# Para explorar la estructura del servidor:
python opcua_simple_asyncua.py explore
```

### 4. Verificar formatos de NodeId
```bash
python test_nodeid_formats.py
```

## Configuración

Editar `config.ini` o modificar las variables al inicio de cada script:

```python
# URL del servidor OPC UA
SERVER_URL = "opc.tcp://192.168.101.96:4840"

# Namespace Index - CRÍTICO
NAMESPACE_INDEX = 2  # Probar 2, 3, 4...
```

## Diagnóstico de Namespace Index

En UaExpert:
1. Conectar al servidor
2. Ir a Address Space panel
3. Navegar Objects > DeviceSet > (PLC)
4. Ver el namespace (ns=X) de las variables

Los PLCs Allen-Bradley típicamente usan:
- `ns=2` para Controller Tags
- `ns=2` o `ns=3` para Program Tags

## Formatos de NodeId para Allen-Bradley

```
# Formato 1: Tag directo
ns=2;s=TagName

# Formato 2: Tag con path de programa
ns=2;s=Program:MainProgram.TagName

# Formato 3: Controller Tags
ns=2;s=Controller Tags.TagName

# Formato 4: I/O directo
ns=2;s=Local:1:I.Data.0
```

## Notas de la Reunión

- Verificar versión OPC UA del módulo Optix (debe ser compatible con 1.0.4)
- Evitar estructuras anidadas en las pruebas iniciales
- Usar solo tipos de datos estándar (BOOL, INT, DINT, REAL, STRING básico)
- Jacobo enviará librería de referencia para comparar

## Archivos

- `opcua_basic_test.py` - Prueba completa con librería opcua
- `opcua_simple_asyncua.py` - Versión moderna con asyncua
- `test_nodeid_formats.py` - Prueba diferentes formatos de NodeId
- `config.ini` - Configuración centralizada

## Resultados Esperados

Si la conexión es exitosa, verás:
```
✓ CONEXIÓN EXITOSA
--- Namespaces Disponibles ---
  ns=0: http://opcfoundation.org/UA/
  ns=1: urn:...
  ns=2: ... <-- Aquí deberían estar tus tags
```

Si hay error de namespace:
```
✗ ERROR: BadNodeIdUnknown
  Posible causa: Namespace Index incorrecto
```
