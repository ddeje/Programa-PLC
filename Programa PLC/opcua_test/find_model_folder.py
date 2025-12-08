"""
Buscar carpeta Model en TODO el servidor OPC UA
"""

import asyncio
from asyncua import Client

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def browse_for_model(node, path="", level=0, max_level=6):
    """Buscar nodos que contengan Model"""
    if level > max_level:
        return
    
    try:
        children = await node.get_children()
        for child in children:
            try:
                name = await child.read_browse_name()
                node_id = child.nodeid
                current_path = f"{path}/{name.Name}" if path else name.Name
                
                # Si contiene Model o EgCom, mostrar
                if 'model' in name.Name.lower() or 'egcom' in name.Name.lower():
                    print(f"✓ {current_path}")
                    print(f"  NodeId: {node_id}")
                
                await browse_for_model(child, current_path, level + 1, max_level)
            except:
                pass
    except:
        pass

async def main():
    print(f"Buscando 'Model' en TODO el servidor: {SERVER_URL}")
    print("=" * 80)
    
    client = Client(SERVER_URL)
    client.timeout = 60
    
    try:
        await client.connect()
        print("✓ Conectado\n")
        
        # Mostrar namespaces
        ns_array = await client.get_namespace_array()
        print("Namespaces:")
        for i, ns in enumerate(ns_array):
            print(f"  ns={i}: {ns}")
        print()
        
        # Buscar en Objects
        print("Buscando en Objects...")
        print("-" * 80)
        objects = client.get_objects_node()
        await browse_for_model(objects, "Objects", 0, 8)
        
        # Buscar también en Root
        print("\n" + "-" * 80)
        print("Buscando en Root...")
        root = client.get_root_node()
        await browse_for_model(root, "Root", 0, 8)
        
        # Probar NodeIds específicos con "Model"
        print("\n" + "=" * 80)
        print("Probando NodeIds con 'Model'...")
        print("-" * 80)
        
        test_nodeids = [
            "ns=9;s=Model",
            "ns=9;s=CPS001.Model",
            "ns=9;s=Model.EgComIn_Heartbeat",
            "ns=1;s=Model",
            "ns=1;s=Model.EgComIn_Heartbeat",
            "ns=11;s=Model",
            "ns=11;s=Model.EgComIn_Heartbeat",
        ]
        
        for nid in test_nodeids:
            try:
                node = client.get_node(nid)
                name = await node.read_browse_name()
                print(f"✓ {nid} -> {name.Name}")
            except Exception as e:
                print(f"✗ {nid} -> No existe")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
