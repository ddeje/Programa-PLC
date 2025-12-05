# PASO 2: Configurar Tags en FactoryTalk Optix para Jetson

## 📋 RESUMEN

El Jetson Edge Gateway espera los tags OPC UA en un formato específico:
- **Namespace**: `4` (ns=4)
- **Tipo de NodeID**: String (`s=`) NO GUID (`g=`)
- **Estructura**: Jerárquica con prefijos (EgComIn_, EgComOut_, etc.)

### Formato Actual (INCORRECTO):
```
ns=9;g=32dd019a-bfe0-a2ee-8825-85d7ac63864c
```

### Formato Requerido (CORRECTO):
```
ns=4;s=EgComIn_Heartbeat
```

---

## ✅ TAGS A CREAR EN OPTIX

### GRUPO 1: EgComIn (Optix → Jetson)
Tags que Optix/PLC ESCRIBE y el Jetson LEE.

| Nombre del Tag | NodeID Requerido | Tipo | Descripción |
|----------------|------------------|------|-------------|
| EgComIn_Heartbeat | `ns=4;s=EgComIn_Heartbeat` | BOOL | Heartbeat del PLC (pulso cada ~20ms) |
| EgComIn_WriteToDb_Confirmation | `ns=4;s=EgComIn_WriteToDb_Confirmation` | BOOL | Confirmación de escritura a DB |
| EgComIn_RecordNotFound | `ns=4;s=EgComIn_RecordNotFound` | BOOL | Material no encontrado |
| EgComIn_UUID_pull | `ns=4;s=EgComIn_UUID_pull` | ARRAY of STRUCT | Lista de UUIDs de contenedores |

---

### GRUPO 2: EgComOut (Jetson → Optix)
Tags que el Jetson ESCRIBE y Optix/PLC LEE.

| Nombre del Tag | NodeID Requerido | Tipo | Descripción |
|----------------|------------------|------|-------------|
| EgComOut_WriteToDb | `ns=4;s=EgComOut_WriteToDb` | BOOL | Flag para escribir datos a DB |
| EgComOut_UUIDReq | `ns=4;s=EgComOut_UUIDReq` | BOOL | Request de UUIDs |
| EgComOut_BarcodeValue | `ns=4;s=EgComOut_BarcodeValue` | STRING | Valor del barcode escaneado |
| EgComOut_BarcodeReq | `ns=4;s=EgComOut_BarcodeReq` | BOOL | Request cuando se escanea barcode |

---

### GRUPO 3: Syn_FileReadIn (Optix → Jetson)
Información del material que se envía al Jetson después de escanear un barcode.

| Nombre del Tag | NodeID Requerido | Tipo | Descripción |
|----------------|------------------|------|-------------|
| Syn_FileReadIn_ABARN | `ns=4;s=Syn_FileReadIn_ABARN` | STRING | A-Barn |
| Syn_FileReadIn_BARCD | `ns=4;s=Syn_FileReadIn_BARCD` | STRING | Barcode |
| Syn_FileReadIn_MATID | `ns=4;s=Syn_FileReadIn_MATID` | STRING | Material ID |
| Syn_FileReadIn_TRLID | `ns=4;s=Syn_FileReadIn_TRLID` | STRING | Trial ID |
| Syn_FileReadIn_GENCD | `ns=4;s=Syn_FileReadIn_GENCD` | STRING | Gen Code |
| Syn_FileReadIn_ABBRC | `ns=4;s=Syn_FileReadIn_ABBRC` | STRING | Abbreviation |
| Syn_FileReadIn_HGHNM | `ns=4;s=Syn_FileReadIn_HGHNM` | STRING | High Name |
| Syn_FileReadIn_ADMNC | `ns=4;s=Syn_FileReadIn_ADMNC` | STRING | Admin Code |
| Syn_FileReadIn_REMRK | `ns=4;s=Syn_FileReadIn_REMRK` | STRING | Remarks |
| Syn_FileReadIn_CGENES | `ns=4;s=Syn_FileReadIn_CGENES` | STRING | C-Genes |
| Syn_FileReadIn_MINRNG | `ns=4;s=Syn_FileReadIn_MINRNG` | STRING | Min Range |
| Syn_FileReadIn_MINROW | `ns=4;s=Syn_FileReadIn_MINROW` | STRING | Min Row |
| Syn_FileReadIn_CRPNM | `ns=4;s=Syn_FileReadIn_CRPNM` | STRING | Crop Name |
| Syn_FileReadIn_SDTRT | `ns=4;s=Syn_FileReadIn_SDTRT` | STRING | Seed Treatment |
| Syn_FileReadIn_COATI | `ns=4;s=Syn_FileReadIn_COATI` | STRING | Coating |
| Syn_FileReadIn_BGPCD | `ns=4;s=Syn_FileReadIn_BGPCD` | STRING | BGP Code |
| Syn_FileReadIn_EXTNO | `ns=4;s=Syn_FileReadIn_EXTNO` | STRING | Ext Number |
| Syn_FileReadIn_LINCD | `ns=4;s=Syn_FileReadIn_LINCD` | STRING | Line Code |
| Syn_FileReadIn_YEAR | `ns=4;s=Syn_FileReadIn_YEAR` | STRING | Year |
| Syn_FileReadIn_SEACD | `ns=4;s=Syn_FileReadIn_SEACD` | STRING | Season Code |
| Syn_FileReadIn_REG | `ns=4;s=Syn_FileReadIn_REG` | STRING | Region |
| Syn_FileReadIn_RSRGT | `ns=4;s=Syn_FileReadIn_RSRGT` | STRING | Research GT |
| Syn_FileReadIn_SPLOC | `ns=4;s=Syn_FileReadIn_SPLOC` | STRING | SP Location |
| Syn_FileReadIn_CNT | `ns=4;s=Syn_FileReadIn_CNT` | STRING | Count |
| Syn_FileReadIn_GMO | `ns=4;s=Syn_FileReadIn_GMO` | STRING | GMO |
| Syn_FileReadIn_GGORG | `ns=4;s=Syn_FileReadIn_GGORG` | STRING | GG Org |
| Syn_FileReadIn_MVRMK | `ns=4;s=Syn_FileReadIn_MVRMK` | STRING | MV Remark |
| Syn_FileReadIn_SHPHD | `ns=4;s=Syn_FileReadIn_SHPHD` | STRING | Ship Head |
| Syn_FileReadIn_HRVDT | `ns=4;s=Syn_FileReadIn_HRVDT` | STRING | Harvest Date |
| Syn_FileReadIn_BGPNM | `ns=4;s=Syn_FileReadIn_BGPNM` | STRING | BGP Name |
| Syn_FileReadIn_LOSCT | `ns=4;s=Syn_FileReadIn_LOSCT` | STRING | Loss Count |
| Syn_FileReadIn_PMATID | `ns=4;s=Syn_FileReadIn_PMATID` | STRING | Parent Mat ID |

---

### GRUPO 4: Syn_FileWriteOut (Jetson → Optix)
Datos de producción que el Jetson envía para registrar.

| Nombre del Tag | NodeID Requerido | Tipo | Descripción |
|----------------|------------------|------|-------------|
| Syn_FileWriteOut_ABARN | `ns=4;s=Syn_FileWriteOut_ABARN` | STRING | A-Barn |
| Syn_FileWriteOut_BARCD | `ns=4;s=Syn_FileWriteOut_BARCD` | STRING | Barcode |
| Syn_FileWriteOut_MATID | `ns=4;s=Syn_FileWriteOut_MATID` | STRING | Material ID |
| Syn_FileWriteOut_TRLID | `ns=4;s=Syn_FileWriteOut_TRLID` | STRING | Trial ID |
| Syn_FileWriteOut_ContainerUUID | `ns=4;s=Syn_FileWriteOut_ContainerUUID` | STRING | Container UUID |
| Syn_FileWriteOut_ALTID | `ns=4;s=Syn_FileWriteOut_ALTID` | STRING | Alt ID |
| Syn_FileWriteOut_Count1 | `ns=4;s=Syn_FileWriteOut_Count1` | INT | Count 1 |
| Syn_FileWriteOut_Weight1 | `ns=4;s=Syn_FileWriteOut_Weight1` | REAL | Weight 1 |
| Syn_FileWriteOut_Rejected | `ns=4;s=Syn_FileWriteOut_Rejected` | INT | Rejected Count |
| Syn_FileWriteOut_GrossMoisture | `ns=4;s=Syn_FileWriteOut_GrossMoisture` | REAL | Gross Moisture |
| Syn_FileWriteOut_TimeStamp | `ns=4;s=Syn_FileWriteOut_TimeStamp` | STRING | Timestamp |

---

## 🔧 CÓMO CONFIGURAR EN FACTORYTALK OPTIX

### Opción A: Crear un Namespace Personalizado

1. En Optix Studio, crear un nuevo **Namespace** con index `4`
2. Crear las variables/tags dentro de ese namespace
3. Configurar el NodeID como tipo **String** (no GUID)

### Opción B: Usar OPC UA Server Aliases

1. Si Optix lo permite, crear **aliases** para los tags existentes
2. Los aliases deben apuntar a los tags del PLC
3. El formato del alias debe ser `ns=4;s=EgComIn_Heartbeat`

### Opción C: Variables OPC UA Personalizadas

1. Crear variables OPC UA independientes en Optix
2. Enlazarlas a los tags del PLC mediante lógica interna
3. Publicarlas con el NodeID correcto

---

## 📊 MAPEO DE TAGS PLC ↔ OPTIX ↔ JETSON

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│    ROCKWELL PLC     │     │   FACTORYTALK OPTIX │     │   JETSON GATEWAY    │
│   192.168.101.96    │     │   192.168.101.100   │     │   192.168.101.110   │
├─────────────────────┤     ├─────────────────────┤     ├─────────────────────┤
│                     │     │                     │     │                     │
│ EgComIn_Heartbeat   │◄───►│ ns=4;s=EgComIn_     │◄───►│ Lee Heartbeat       │
│ (Program:test_      │     │     Heartbeat       │     │                     │
│  Gateway)           │     │                     │     │                     │
│                     │     │                     │     │                     │
│ EgComIn_RecordNot   │◄───►│ ns=4;s=EgComIn_     │◄───►│ Lee RecordNotFound  │
│ Found               │     │     RecordNotFound  │     │                     │
│                     │     │                     │     │                     │
│ EgComOut_WriteToDb  │◄───►│ ns=4;s=EgComOut_    │◄───►│ Escribe WriteToDb   │
│                     │     │     WriteToDb       │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

---

## ✅ VERIFICACIÓN

Después de configurar los tags, verificar con Python:

```python
import asyncio
from asyncua import Client

async def test():
    c = Client('opc.tcp://192.168.101.100:55533', timeout=10)
    await c.connect()
    
    # Probar leer con el nuevo formato
    heartbeat = c.get_node('ns=4;s=EgComIn_Heartbeat')
    val = await heartbeat.read_value()
    print(f'EgComIn_Heartbeat = {val}')
    
    # Probar escribir
    record_not_found = c.get_node('ns=4;s=EgComIn_RecordNotFound')
    await record_not_found.write_value(True)
    print('RecordNotFound escrito correctamente')
    
    await c.disconnect()
    print('✅ Tags configurados correctamente!')

asyncio.run(test())
```

---

## ⚠️ ERRORES COMUNES

### Error: "BadNodeIdUnknown"
- El NodeID no existe con ese formato
- Verificar que el namespace sea 4 y el identificador sea String

### Error: "BadTypeMismatch"
- El tipo de dato no coincide
- Verificar que BOOL sea BOOL, STRING sea STRING, etc.

### Error: "BadNotWritable"
- El tag no tiene permisos de escritura
- Configurar el tag como Read/Write en Optix

---

## 📝 NOTAS ADICIONALES

1. **El separador es underscore (_)**: `EgComIn_Heartbeat`, no `EgComIn.Heartbeat`

2. **Syn_FileWriteOut usa underscore inicial**: `_MATID`, `_TRLID`, etc.
   - NodeID: `ns=4;s=Syn_FileWriteOut_MATID` (sin el underscore extra al inicio)

3. **UUID_pull es un array de estructuras** - Este es el más complejo:
   ```
   Estructura: Syngenta_UUID_Struct
   - ContainerUUID: STRING
   - ALTID: STRING
   ```

4. **Prioridad de implementación**:
   1. Primero: EgComIn_Heartbeat (para verificar conexión)
   2. Segundo: EgComIn_RecordNotFound y EgComOut_BarcodeReq
   3. Tercero: Los demás tags

---

## 📞 SOPORTE

Si el Jetson aún no puede leer los tags, verificar los logs:
```bash
docker logs almaco_apl_opcua-almacoAplOpcua-1 --tail 100
```

Buscar mensajes como:
- ✅ "Value update is True/False" = Conexión exitosa
- ❌ "Could not connect" = Problema de conexión
- ❌ "BadNodeIdUnknown" = Tag no encontrado
