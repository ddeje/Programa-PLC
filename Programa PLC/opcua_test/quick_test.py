"""
Test rápido de tags EgComIn - ns=9
"""
import asyncio
from asyncua import Client

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    client = Client(url, timeout=10)
    
    print("Conectando...")
    await client.connect()
    print("✅ Conectado!\n")
    
    # Probar diferentes formatos
    tags = [
        "ns=9;s=EgComIn_Heartbeat",
        "ns=9;s=GlobalVars.EgComIn_Heartbeat",
        "ns=9;s=EgComIn_RecordNotFound",
        "ns=9;s=GlobalVars.EgComIn_RecordNotFound",
    ]
    
    for tag in tags:
        try:
            node = client.get_node(tag)
            val = await node.read_value()
            print(f"✅ {tag} = {val}")
        except Exception as e:
            print(f"❌ {tag}")
    
    await client.disconnect()
    print("\nDesconectado")

asyncio.run(main())
