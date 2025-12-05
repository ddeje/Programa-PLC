# PASO 1: Cambiar Puerto del OPC UA Server en FactoryTalk Optix

## 📋 RESUMEN DEL PROBLEMA

El Jetson Edge Gateway (NVIDIA) intenta conectarse al servidor OPC UA en:
- **IP**: `192.168.101.100`
- **Puerto**: `55533`

Pero FactoryTalk Optix Edge está configurado en:
- **IP**: `192.168.101.100` ✅ (Correcto)
- **Puerto**: `59100` ❌ (Incorrecto)

---

## ✅ ACCIÓN REQUERIDA

### Cambiar el puerto del OPC UA Server de `59100` a `55533`

### Pasos en FactoryTalk Optix Studio:

1. Abrir el proyecto de FactoryTalk Optix
2. En el panel izquierdo, buscar **"OPC-UA Server"** o **"Servers"**
3. Hacer clic en la configuración del servidor OPC UA
4. Buscar el campo **"Port"** o **"Puerto"**
5. Cambiar el valor de `59100` a `55533`
6. Guardar el proyecto
7. Desplegar/Deploy al dispositivo Edge

---

## 🔍 VERIFICACIÓN

Después de cambiar el puerto, verificar desde la PC con Python:

```python
import asyncio
from asyncua import Client

async def test():
    # Probar con el nuevo puerto
    c = Client('opc.tcp://192.168.101.100:55533', timeout=10)
    await c.connect()
    print("✅ Conexión exitosa al puerto 55533!")
    await c.disconnect()

asyncio.run(test())
```

O con UaExpert:
- Conectar a: `opc.tcp://192.168.101.100:55533`

---

## 📊 CONTEXTO TÉCNICO

### ¿Por qué puerto 55533?

El sistema anterior usaba un PLC OMRON que tenía su servidor OPC UA en el puerto `55533`. El Jetson Edge Gateway tiene esta configuración **hardcodeada** en un contenedor Docker que no podemos modificar:

```
OPCUA_URL={"APLMXPV03AL23":"opc.tcp://192.168.101.100:55533/"}
```

### Dispositivos en la red:

| Dispositivo | IP | Puerto OPC UA | Rol |
|-------------|-----|---------------|-----|
| FactoryTalk Optix Edge | 192.168.101.100 | 55533 (cambiar) | Servidor OPC UA |
| Rockwell PLC | 192.168.101.96 | N/A | PLC (EtherNet/IP) |
| Jetson Edge Gateway | 192.168.101.110 | N/A | Cliente OPC UA |
| PC Desarrollo | 192.168.101.200 | N/A | Desarrollo/Testing |

---

## ⚠️ NOTAS IMPORTANTES

1. **NO modificar el código del Jetson** - No tenemos acceso para cambiar la configuración del contenedor Docker.

2. **El puerto 55533 debe estar libre** - Asegurarse de que ningún otro servicio use este puerto en la máquina de Optix.

3. **Firewall** - Verificar que el firewall permita conexiones entrantes en el puerto 55533.

4. **Después de este paso**, continuar con el **PASO 2** para configurar los tags correctamente.

---

## 📞 CONTACTO

Si hay problemas, revisar los logs del Jetson ejecutando en su terminal:
```bash
docker logs almaco_apl_opcua-almacoAplOpcua-1 --tail 50
```

Buscar mensajes que digan "Connected" en lugar de "Could not connect".
