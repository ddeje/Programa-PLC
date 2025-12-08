"""
Prueba simple para leer EgComIn_Heartbeat desde Optix
Servidor: 192.168.101.100:55533
"""

import asyncio
from asyncua import Client

SERVER_URL = "opc.tcp://192.168.101.100:55533"

# NodeId CORRECTO (path completo)
NODE_ID = "ns=9;s=CPS001.CommDrivers.RAEtherNet_IPDriver1.RAEtherNet_IPStation1.Tags.Program:EdgeGateway.EgComIn_Heartbeat"

async def main():
    print(f"Conectando a: {SERVER_URL}")
    print(f"NodeId: {NODE_ID}")
    print("-" * 70)
    
    client = Client(SERVER_URL)
    client.timeout = 10
    
    try:
        await client.connect()
        print("✓ Conectado al servidor OPC UA")
        
        # Obtener el nodo
        node = client.get_node(NODE_ID)
        
        # Leer el valor
        value = await node.read_value()
        print(f"\n✓ EgComIn_Heartbeat = {value}")
        
        # Monitorear por unos segundos
        print("\nMonitoreando valor por 10 segundos...")
        print("-" * 70)
        for i in range(10):
            value = await node.read_value()
            print(f"  [{i+1}] Heartbeat: {value}")
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("-" * 70)
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
