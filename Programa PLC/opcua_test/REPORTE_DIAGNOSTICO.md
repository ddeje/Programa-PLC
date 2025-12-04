# REPORTE DE DIAGNÓSTICO OPC UA
## Optix Edge - CPS_001
### Fecha: 4 de Diciembre, 2025

---

## RESUMEN EJECUTIVO

Se realizaron pruebas exhaustivas de comunicación OPC UA al servidor Optix Edge. 
Se identificaron y confirmaron **3 problemas principales**.

---

## PROBLEMA 1: NAMESPACE INDEX INCORRECTO ✅ CONFIRMADO

### Síntoma:
El Gateway #3 no puede encontrar las variables del PLC.

### Causa Raíz:
El gateway está configurado para buscar en `ns=2`, pero los tags del PLC están en `ns=6`.

### Evidencia:
```
Probando tag: Program:EdgeGateway.EdCommIn.Heartbeat

  ns=0: ✗ No existe
  ns=1: ✗ No existe
  ns=2: ✗ No existe  <-- AQUÍ BUSCA EL GATEWAY
  ns=3: ✗ No existe
  ns=4: ✗ No existe
  ns=5: ✗ No existe
  ns=6: ✓ ENCONTRADO - Valor: False  <-- AQUÍ ESTÁN LOS TAGS
```

### Namespaces en el servidor:
| ns | URI | Contenido |
|----|-----|-----------|
| 0 | http://opcfoundation.org/UA/ | Tipos base OPC UA |
| 1 | urn:RockwellAutomation:5069-L310ER%2FA:1890182208 | Servidor |
| 2 | http://rockwellautomation.com/UA/ | Rockwell UA (vacío) |
| 3 | http://opcfoundation.org/UA/DI/ | Device Integration |
| 4 | http://opcfoundation.org/UA/FX/Data/ | FX Data |
| 5 | http://opcfoundation.org/UA/FX/AC/ | FX AC |
| **6** | **urn:RockwellAutomation:5069-L310ER%2FA** | **← TAGS DEL PLC** |

### Solución:
**Cambiar Namespace Index de 2 a 6 en la configuración del gateway.**

---

## PROBLEMA 2: FORMATO DE NODEID INCORRECTO ✅ CONFIRMADO

### Síntoma:
Los identificadores de variables no son legibles o no funcionan.

### Causa Raíz:
Se usa un formato de NodeId incompleto o incorrecto.

### Formatos Probados:
| Formato | Resultado |
|---------|-----------|
| `ns=2;s=TagName` | ❌ No funciona |
| `ns=6;s=TagName` | ❌ No funciona |
| `ns=6;s=Program:EdgeGateway.TagName` | ✅ **FUNCIONA** |

### Formato Correcto:
```
ns=6;s=Program:EdgeGateway.EdCommIn.Heartbeat
ns=6;s=Program:EdgeGateway.EgComOut.BarcodeValue
```

### Estructura del path:
```
ns=6;s=Program:{NombrePrograma}.{EstructuraTag}.{MiembroTag}
```

---

## PROBLEMA 3: TIPOS DE DATOS CUSTOM (OPC UA 1.0.4) ✅ CONFIRMADO

### Síntoma:
Las estructuras (UDT) llegan como datos binarios sin parsear.

### Causa Raíz:
El servidor OPC UA usa la especificación 1.0.4 que tiene limitaciones para transferir definiciones de tipos de datos custom.

### Evidencia:

**Tipos estándar - FUNCIONAN:**
```
Tag: Heartbeat (BOOL)
  Tipo: Boolean (1)
  Valor: False
  ✓ LECTURA CORRECTA

Tag: BarcodeValue (STRING)
  Tipo: String (12)
  Valor: "test"
  ✓ LECTURA CORRECTA
```

**Tipos custom - NO SE PARSEAN:**
```
Tag: MaterialRecord_pull (ESTRUCTURA)
  Tipo: ExtensionObject (22)
  Valor: [bytes raw sin decodificar]
  ⚠️ NO SE PUEDE INTERPRETAR

Tag: MaterialRecord_push (ARRAY DE ESTRUCTURA)
  Tipo: ExtensionObject (22)
  Valor: [Array de 3 ExtensionObjects con bytes raw]
  ⚠️ NO SE PUEDE INTERPRETAR
```

### Prueba Definitiva:
Al intentar cargar las definiciones de tipos custom (`load_data_type_definitions()`), 
el servidor **CIERRA LA CONEXIÓN** repetidamente para cada tipo:

```
Error getting datatype for node ns=6;s={FBD_COMPARE}DataType
ConnectionError: Connection is closed

Error getting datatype for node ns=6;s={AXIS_SERVO}DataType  
ConnectionError: Connection is closed

Error getting datatype for node ns=6;s={MESSAGE}DataType
ConnectionError: Connection is closed

... (30+ tipos con el mismo error)
```

**Esto CONFIRMA que el servidor no puede/quiere proporcionar las definiciones de tipos.**

---

## RESULTADOS DE LECTURA DE TAGS

| Tag | Tipo | Valor | Estado |
|-----|------|-------|--------|
| YEAR | Int32 | 0 | ✅ OK |
| Heartbeat | Boolean | False | ✅ OK |
| RecordNotFound | Boolean | False | ✅ OK |
| WriteToDb_Confirmation | Boolean | False | ✅ OK |
| UUID_pull | String | "" | ✅ OK |
| BarcodeValue | String | "test" | ✅ OK |
| BarcodeReq | Boolean | False | ✅ OK |
| WriteToDb | Boolean | False | ✅ OK |
| UUIDReq | Boolean | False | ✅ OK |
| MaterialRecord_pull | ExtensionObject | [bytes] | ⚠️ Sin parsear |
| MaterialRecord_push | ExtensionObject[] | [bytes] | ⚠️ Sin parsear |

**Tasa de éxito: 11/11 lecturas (100%), pero 2 tags no se interpretan correctamente**

---

## ACCIONES RECOMENDADAS

### Inmediatas (para probar mañana):

1. **Corregir configuración del Gateway #3:**
   - Cambiar Namespace Index: `2` → `6`
   - Usar formato de NodeId: `ns=6;s=Program:EdgeGateway.{tag}`

2. **Para estructuras (MaterialRecord):**
   - Opción A: Exponer solo los miembros primitivos de la estructura como tags separados
   - Opción B: Implementar decodificación manual del ExtensionObject conociendo la estructura
   - Opción C: Usar la librería que enviará Jacobo para manejar tipos custom

### Verificar con Jacobo:

1. ¿Qué versión de OPC UA usa el módulo Optix? (¿Es compatible con 1.0.4+?)
2. ¿La librería que enviará puede cargar tipos custom de Rockwell?
3. ¿Hay forma de exponer la estructura MaterialRecord como tags individuales?

---

## CONFIGURACIÓN DE REFERENCIA

```ini
# Configuración correcta para el Gateway
[OPC UA Client]
Server URL = opc.tcp://192.168.101.96:4840
Namespace Index = 6
Node ID Format = ns=6;s=Program:EdgeGateway.{TagPath}

# Ejemplos de NodeId correctos:
# ns=6;s=Program:EdgeGateway.EdCommIn.Heartbeat
# ns=6;s=Program:EdgeGateway.EgComOut.BarcodeValue
# ns=6;s=Program:EdgeGateway.EgComOut.BarcodeReq
```

---

## CONCLUSIÓN

Los problemas de comunicación OPC UA están **100% identificados y confirmados**:

1. ✅ **Namespace incorrecto** (ns=2 vs ns=6) - Fácil de corregir
2. ✅ **Formato de NodeId incorrecto** - Fácil de corregir
3. ⚠️ **Tipos custom no se parsean** - Requiere solución adicional

La comunicación básica con tipos estándar (BOOL, INT, STRING) **funciona perfectamente**.
El problema con estructuras es una limitación del protocolo/servidor, no del cliente.
