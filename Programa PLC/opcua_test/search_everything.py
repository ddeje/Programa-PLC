"""
Explorar TODO el servidor buscando EgComIn_Heartbeat en cualquier ubicación
"""

import asyncio
from asyncua import Client

SERVER_URL = "opc.tcp://192.168.101.100:55533"

found_nodes = []

async def browse_everything(node, path="", level=0, max_level=15):
    if level > max_level:
        return
    
    try:
        children = await node.get_children()
        for child in children:
            try:
                name = await child.read_browse_name()
                node_id = child.nodeid
                current_path = f"{path}/{name.Name}" if path else name.Name
                
                # Buscar cualquier cosa con EgCom o Heartbeat
                name_lower = name.Name.lower()
                if 'egcom' in name_lower or 'heartbeat' in name_lower or 'edgegateway' in name_lower:
                    found_nodes.append({
                        'path': current_path,
                        'name': name.Name,
                        'nodeid': str(node_id),
                        'ns': node_id.NamespaceIndex
                    })
                
                await browse_everything(child, current_path, level + 1, max_level)
            except:
                pass
    except:
        pass

async def main():
    print(f"Explorando TODO: {SERVER_URL}")
    print("=" * 80)
    
    client = Client(SERVER_URL)
    client.timeout = 60
    
    try:
        await client.connect()
        print("✓ Conectado\n")
        
        # Explorar desde Root
        root = client.get_root_node()
        await browse_everything(root, "", 0, 15)
        
        print(f"Encontrados {len(found_nodes)} nodos relevantes:\n")
        print("-" * 80)
        
        for n in found_nodes:
            print(f"Nombre: {n['name']}")
            print(f"  Path: {n['path']}")
            print(f"  NodeId: {n['nodeid']}")
            print(f"  Namespace: ns={n['ns']}")
            print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
