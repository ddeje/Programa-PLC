"""
Buscar específicamente los tags EgComIn_Heartbeat y EgComIn_RecordNotFound
"""
import asyncio
from asyncua import Client

async def search_for_tag(node, search_names, results, path=""):
    """Buscar tags específicos"""
    try:
        name = await node.read_browse_name()
        current_path = f"{path}/{name.Name}" if path else name.Name
        
        # Verificar si es uno de los tags buscados
        for search in search_names:
            if search.lower() in name.Name.lower():
                node_class = await node.read_node_class()
                results.append({
                    "name": name.Name,
                    "path": current_path,
                    "node_id": str(node),
                    "is_variable": node_class.value == 2
                })
        
        # Explorar hijos
        children = await node.get_children()
        for child in children:
            await search_for_tag(child, search_names, results, current_path)
            
    except Exception as e:
        pass

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        # Buscar desde Objects
        objects = client.nodes.objects
        
        search_names = ["EgComIn_Heartbeat", "EgComIn_RecordNotFound", "Heartbeat", "RecordNotFound"]
        results = []
        
        print("Buscando tags... (esto puede tomar un momento)")
        await search_for_tag(objects, search_names, results)
        
        print("\n" + "="*60)
        print("RESULTADOS:")
        print("="*60)
        
        if results:
            for r in results:
                print(f"\n📊 {r['name']}")
                print(f"   Path: {r['path']}")
                print(f"   NodeId: {r['node_id']}")
                print(f"   Es Variable: {r['is_variable']}")
                
                # Intentar leer el valor
                if r['is_variable']:
                    try:
                        node = client.get_node(r['node_id'])
                        val = await node.read_value()
                        print(f"   ✅ Valor: {val}")
                    except Exception as e:
                        print(f"   ❌ Error leyendo: {e}")
        else:
            print("No se encontraron tags")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
