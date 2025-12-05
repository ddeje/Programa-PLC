"""
============================================================
TEST DE COMUNICACIÓN OPC UA - Edge Gateway
============================================================
Python <-> Optix Edge <-> PLC (Rockwell)

Tags:
  - EgComIn_Heartbeat
  - EgComIn_RecordNotFound
============================================================
"""
import asyncio
from asyncua import Client

# Configuración
SERVER_URL = "opc.tcp://192.168.101.100:59100"

# NodeIds de los tags
TAGS = {
    "EgComIn_Heartbeat": "ns=9;g=32dd019a-bfe0-a2ee-8825-85d7ac63864c",
    "EgComIn_RecordNotFound": "ns=9;g=7f1a722d-3cd6-817c-ee6e-b0c7f698010a",
}

async def main():
    print("="*60)
    print("  TEST DE COMUNICACIÓN - EDGE GATEWAY")
    print("="*60)
    
    client = Client(SERVER_URL, timeout=10)
    
    try:
        # Conectar
        print(f"\n[1] Conectando a {SERVER_URL}...")
        await client.connect()
        print("    ✅ CONECTADO")
        
        # Leer tags
        print("\n[2] Leyendo tags...")
        for name, node_id in TAGS.items():
            node = client.get_node(node_id)
            val = await node.read_value()
            print(f"    ✅ {name} = {val}")
        
        # Escribir Heartbeat
        print("\n[3] Probando escritura...")
        hb = client.get_node(TAGS["EgComIn_Heartbeat"])
        
        original = await hb.read_value()
        print(f"    Valor original: {original}")
        
        await hb.write_value(True)
        nuevo = await hb.read_value()
        print(f"    ✅ Escrito True -> Leído: {nuevo}")
        
        await hb.write_value(False)
        final = await hb.read_value()
        print(f"    ✅ Escrito False -> Leído: {final}")
        
        # Resultado
        print("\n" + "="*60)
        print("  ✅ COMUNICACIÓN EXITOSA")
        print("="*60)
        print("""
  Python puede:
    ✅ Conectarse a Optix Edge (OPC UA)
    ✅ Leer tags del PLC
    ✅ Escribir tags al PLC
""")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
    finally:
        await client.disconnect()
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
