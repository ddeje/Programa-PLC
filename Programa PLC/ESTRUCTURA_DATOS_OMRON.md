# Estructura de Datos - PLC Omron

## Conexión OPC UA
- **IP**: 192.168.101.100
- **Puerto**: 55533
- **URL**: `opc.tcp://192.168.101.100:55533`

---

## Variables UUID en GlobalVars

### 1. EgComIn_UUID_pull
**NodeId**: `ns=4;s=EgComIn_UUID_pull`

Array de 5 elementos del tipo `Syngenta_UUID_Struct`:

```
EgComIn_UUID_pull[0]
    ├── ContainerUUID (string)
    └── ALTID (string)

EgComIn_UUID_pull[1]
    ├── ContainerUUID (string)
    └── ALTID (string)

EgComIn_UUID_pull[2]
    ├── ContainerUUID (string)
    └── ALTID (string)

EgComIn_UUID_pull[3]
    ├── ContainerUUID (string)
    └── ALTID (string)

EgComIn_UUID_pull[4]
    ├── ContainerUUID (string)
    └── ALTID (string)
```

**Propósito**: Recibir hasta 5 UUIDs de contenedores con sus IDs alternativos del sistema pull.

---

### 2. DBoard_ContainerUUID1/2/3
| Variable | NodeId | Tipo |
|----------|--------|------|
| `DBoard_ContainerUUID1` | `ns=4;s=DBoard_ContainerUUID1` | String |
| `DBoard_ContainerUUID2` | `ns=4;s=DBoard_ContainerUUID2` | String |
| `DBoard_ContainerUUID3` | `ns=4;s=DBoard_ContainerUUID3` | String |

**Propósito**: Mostrar UUIDs en dashboard.

---

### 3. EgComOut_UUIDReq
**NodeId**: `ns=4;s=EgComOut_UUIDReq`

| Tipo | Descripción |
|------|-------------|
| BOOL | Flag para solicitar UUIDs |

---

### 4. Syn_FileWriteOut_ContainerUUID
**NodeId**: `ns=4;s=Syn_FileWriteOut_ContainerUUID`

| Tipo | Descripción |
|------|-------------|
| Array[3] de String | UUIDs para escribir a archivo |

---

## Tipo de Dato Personalizado

### Syngenta_UUID_Struct
Definido en el diccionario de tipos del namespace 4:

```xml
<opc:StructuredType Name="Syngenta_UUID_Struct" BaseType="ua:ExtensionObject">
    <opc:Field Name="ContainerUUID" TypeName="opc:CharArray"/>
    <opc:Field Name="ALTID" TypeName="opc:CharArray"/>
</opc:StructuredType>
```

| Campo | Tipo |
|-------|------|
| ContainerUUID | CharArray (String) |
| ALTID | CharArray (String) |

---

## Paths OPC UA

Las variables se pueden acceder por dos paths equivalentes:
- `Objects/DeviceSet/Configuration/Resources/Master_CPU/GlobalVars/[variable]`
- `Objects/Master_CPU/GlobalVars/[variable]`

---

*Documentación generada: Diciembre 2024*
