# Tags Requeridos para Optix Edge
## Configuración para compatibilidad con Jetson Edge Gateway

**IMPORTANTE**: El Jetson espera tags en **namespace 4** con **NodeID tipo String**.

Formato actual de Optix: `ns=9;g=32dd019a-bfe0-a2ee-8825-85d7ac63864c`
Formato requerido: `ns=4;s=EgComIn_Heartbeat`

---

## 1. Tags EgComIn (PLC → Jetson)
Estos tags los ESCRIBE el PLC/Optix y los LEE el Jetson.

| Tag Name en Optix | NodeID Requerido | Tipo | Descripción |
|-------------------|------------------|------|-------------|
| EgComIn_Heartbeat | `ns=4;s=EgComIn_Heartbeat` | BOOL | Heartbeat del PLC |
| EgComIn_WriteToDb_Confirmation | `ns=4;s=EgComIn_WriteToDb_Confirmation` | BOOL | Confirmación escritura DB |
| EgComIn_RecordNotFound | `ns=4;s=EgComIn_RecordNotFound` | BOOL | Material no encontrado |
| EgComIn_UUID_pull | `ns=4;s=EgComIn_UUID_pull` | STRING | UUID del container |

---

## 2. Tags EgComOut (Jetson → PLC)
Estos tags los ESCRIBE el Jetson y los LEE el PLC/Optix.

| Tag Name en Optix | NodeID Requerido | Tipo | Descripción |
|-------------------|------------------|------|-------------|
| EgComOut_WriteToDb | `ns=4;s=EgComOut_WriteToDb` | BOOL | Request escribir a DB |
| EgComOut_UUIDReq | `ns=4;s=EgComOut_UUIDReq` | STRING | Request de UUID |
| EgComOut_BarcodeValue | `ns=4;s=EgComOut_BarcodeValue` | STRING | Valor barcode escaneado |
| EgComOut_BarcodeReq | `ns=4;s=EgComOut_BarcodeReq` | BOOL | Request de barcode |

---

## 3. Tags Syn_FileReadIn (PLC → Jetson)
Datos del material que el PLC envía al Jetson.

| Tag Name en Optix | NodeID Requerido | Tipo | Descripción |
|-------------------|------------------|------|-------------|
| Syn_FileReadIn_ABARN | `ns=4;s=Syn_FileReadIn_ABARN` | STRING | A-Barn |
| Syn_FileReadIn_BARCD | `ns=4;s=Syn_FileReadIn_BARCD` | STRING | Barcode |
| Syn_FileReadIn_MATID | `ns=4;s=Syn_FileReadIn_MATID` | STRING | Material ID |
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
| Syn_FileReadIn_TRLID | `ns=4;s=Syn_FileReadIn_TRLID` | STRING | Trial ID |
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

## 4. Tags Syn_FileWriteOut (Jetson → PLC)
Datos que el Jetson envía al PLC para escribir.

| Tag Name en Optix | NodeID Requerido | Tipo | Descripción |
|-------------------|------------------|------|-------------|
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

## OPCIONES DE CONFIGURACIÓN EN OPTIX EDGE:

### Opción A: Crear un OPC UA Server personalizado en Optix
1. En Optix, ir a **OPC-UA Server** settings
2. Configurar el namespace URI para que sea ns=4
3. Crear variables con BrowseName que coincidan exactamente
4. Configurar NodeID como String (no GUID)

### Opción B: Usar Aliases/NodeID Override
En algunos casos Optix permite definir el NodeID explícitamente.

### Opción C: Modificar el código del Jetson (NO RECOMENDADO)
El cliente dijo que no puede modificar el código del Jetson.

---

## PRUEBA RÁPIDA
Una vez configurados los tags, desde Python puedes verificar:

```python
import asyncio
from asyncua import Client

async def test():
    c = Client('opc.tcp://192.168.101.100:59100')
    await c.connect()
    
    # Probar leer con el nuevo formato
    node = c.get_node('ns=4;s=EgComIn_Heartbeat')
    val = await node.read_value()
    print(f'Heartbeat = {val}')
    
    await c.disconnect()

asyncio.run(test())
```

---

## CONTENEDORES DOCKER EN JETSON
El Jetson tiene estos servicios corriendo:
- `almaco_apl_opcua` - Cliente OPC UA que lee/escribe tags
- `msg_serializer` - Serializa mensajes
- `vmek_analytics` - Analítica VMEK
- `trial_info_manager` - Gestión de trials
- `redis_server` - Base de datos Redis

El contenedor **almaco_apl_opcua** es el que se conecta a Optix Edge.
