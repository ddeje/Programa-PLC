"""
Verificar si el NodeId corto funciona
ns=9;s=EgComIn_Heartbeat
"""

import asyncio
from asyncua import Client

SERVER_URL = "opc.tcp://192.168.101.100:55533"
NODE_ID_CORTO = "ns=9;s=EgComIn_Heartbeat"

async def main():
    print(f"Servidor: {SERVER_URL}")
    print(f"Probando NodeId CORTO: {NODE_ID_CORTO}")
    print("-" * 60)
    
    client = Client(SERVER_URL)
    client.timeout = 10
    
    try:
        await client.connect()
        print("✓ Conectado")
        
        node = client.get_node(NODE_ID_CORTO)
        value = await node.read_value()
        print(f"✓ Valor: {value}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
