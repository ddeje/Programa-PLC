"""
Buscar EgComIn_Heartbeat con los paths vistos en Optix
"""

import asyncio
from asyncua import Client

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def main():
    print(f"Buscando en: {SERVER_URL}")
    print("=" * 80)
    
    client = Client(SERVER_URL)
    client.timeout = 15
    
    # Posibles NodeIds basados en la estructura de Optix
    test_nodeids = [
        # Con edgegateway
        "ns=9;s=EgComIn_Heartbeat",
        "ns=9;s=edgegateway.EgComIn_Heartbeat",
        "ns=9;s=edgegateway/EgComIn_Heartbeat",
        
        # Con OPCUAServer
        "ns=9;s=OPCUAServer.edgegateway.EgComIn_Heartbeat",
        "ns=9;s=OPC-UA Server To Edge Gateway.OPCUAServer.edgegateway.EgComIn_Heartbeat",
        
        # Otros namespaces
        "ns=1;s=EgComIn_Heartbeat",
        "ns=1;s=edgegateway.EgComIn_Heartbeat",
        "ns=4;s=EgComIn_Heartbeat",
        "ns=4;s=edgegateway.EgComIn_Heartbeat",
        "ns=4;s=OPCUAServer.edgegateway.EgComIn_Heartbeat",
        "ns=11;s=EgComIn_Heartbeat",
        "ns=11;s=edgegateway.EgComIn_Heartbeat",
        
        # Model folder
        "ns=9;s=Model.edgegateway.EgComIn_Heartbeat",
        "ns=1;s=Model.edgegateway.EgComIn_Heartbeat",
        "ns=11;s=Model.edgegateway.EgComIn_Heartbeat",
    ]
    
    try:
        await client.connect()
        print("✓ Conectado\n")
        
        print("Probando NodeIds posibles...")
        print("-" * 80)
        
        for nid in test_nodeids:
            try:
                node = client.get_node(nid)
                value = await node.read_value()
                print(f"✓ ENCONTRADO: {nid}")
                print(f"  Valor: {value}\n")
            except:
                print(f"✗ {nid}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
