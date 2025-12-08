"""
Explorar el servidor OPC UA de Optix para encontrar tags disponibles
Servidor: 192.168.101.100:55533
"""

import asyncio
from asyncua import Client, ua

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def browse_node(node, level=0, max_level=3):
    """Navegar recursivamente los nodos"""
    if level > max_level:
        return
    
    indent = "  " * level
    try:
        children = await node.get_children()
        for child in children:
            try:
                name = await child.read_browse_name()
                node_id = child.nodeid
                print(f"{indent}├─ {name.Name} [{node_id}]")
                
                # Si es namespace 9, explorar más profundo
                if node_id.NamespaceIndex == 9 or level < 2:
                    await browse_node(child, level + 1, max_level)
            except Exception as e:
                pass
    except Exception as e:
        pass

async def main():
    print(f"Explorando: {SERVER_URL}")
    print("=" * 70)
    
    client = Client(SERVER_URL)
    client.timeout = 15
    
    try:
        await client.connect()
        print("✓ Conectado al servidor OPC UA\n")
        
        # Mostrar namespaces
        ns_array = await client.get_namespace_array()
        print("Namespaces disponibles:")
        for i, ns in enumerate(ns_array):
            print(f"  ns={i}: {ns}")
        print()
        
        # Buscar en Objects
        print("Explorando Objects...")
        print("-" * 70)
        objects = client.get_objects_node()
        await browse_node(objects, 0, 4)
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("\n" + "=" * 70)
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
