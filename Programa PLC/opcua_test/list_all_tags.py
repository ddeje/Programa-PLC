"""
Buscar todos los tags, especialmente en carpeta Model
"""

import asyncio
from asyncua import Client

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def browse_all(node, path="", results=None, level=0, max_level=10):
    if results is None:
        results = []
    if level > max_level:
        return results
    
    try:
        children = await node.get_children()
        for child in children:
            try:
                name = await child.read_browse_name()
                node_id = child.nodeid
                current_path = f"{path}/{name.Name}" if path else name.Name
                
                # Guardar info del nodo
                results.append({
                    'path': current_path,
                    'name': name.Name,
                    'nodeid': str(node_id)
                })
                
                await browse_all(child, current_path, results, level + 1, max_level)
            except:
                pass
    except:
        pass
    
    return results

async def main():
    print(f"Explorando: {SERVER_URL}")
    print("=" * 80)
    
    client = Client(SERVER_URL)
    client.timeout = 30
    
    try:
        await client.connect()
        print("✓ Conectado\n")
        
        # Explorar desde CPS001
        cps_node = client.get_node("ns=9;s=CPS001")
        all_nodes = await browse_all(cps_node, "CPS001", max_level=12)
        
        # Buscar nodos que contengan "Model" o "EgCom"
        print("=" * 80)
        print("NODOS QUE CONTIENEN 'Model':")
        print("-" * 80)
        model_nodes = [n for n in all_nodes if 'model' in n['path'].lower()]
        for n in model_nodes:
            print(f"  {n['path']}")
            print(f"    NodeId: {n['nodeid']}")
        
        print("\n" + "=" * 80)
        print("NODOS QUE CONTIENEN 'EgCom':")
        print("-" * 80)
        egcom_nodes = [n for n in all_nodes if 'egcom' in n['name'].lower()]
        for n in egcom_nodes:
            print(f"  {n['name']}")
            print(f"    Path: {n['path']}")
            print(f"    NodeId: {n['nodeid']}")
        
        print("\n" + "=" * 80)
        print("TODOS LOS NODOS EN ns=9 (primeros 100):")
        print("-" * 80)
        for i, n in enumerate(all_nodes[:100]):
            print(f"  {n['path']}")
            print(f"    {n['nodeid']}")
            
        if len(all_nodes) > 100:
            print(f"\n  ... y {len(all_nodes) - 100} nodos más")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
