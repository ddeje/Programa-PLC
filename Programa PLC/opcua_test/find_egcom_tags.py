"""
Buscar los tags EgComIn_Heartbeat, EgComIn_RecordNotFound, EgComIn_UUID_pull
"""
import asyncio
from asyncua import Client

async def search_deep(node, search_terms, results, depth=0, max_depth=8):
    """Buscar variables por nombre"""
    if depth > max_depth:
        return
    
    try:
        name = await node.read_browse_name()
        
        # Verificar si coincide
        for term in search_terms:
            if term.lower() in name.Name.lower():
                node_class = await node.read_node_class()
                try:
                    val = await node.read_value()
                    results.append({
                        "name": name.Name,
                        "node_id": str(node),
                        "value": val,
                        "readable": True
                    })
                except Exception as e:
                    results.append({
                        "name": name.Name,
                        "node_id": str(node),
                        "error": str(e)[:50],
                        "readable": False
                    })
        
        # Explorar hijos
        children = await node.get_children()
        for child in children:
            await search_deep(child, search_terms, results, depth + 1, max_depth)
                
    except:
        pass

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=15)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        print("Buscando tags EgComIn_Heartbeat, EgComIn_RecordNotFound, EgComIn_UUID_pull...")
        print("="*60)
        
        objects = client.nodes.objects
        results = []
        await search_deep(objects, ["EgComIn_Heartbeat", "EgComIn_RecordNotFound", "EgComIn_UUID", "GlobalVars"], results)
        
        if results:
            print(f"\n✅ Encontradas {len(results)} coincidencias:\n")
            for r in results:
                print(f"📊 {r['name']}")
                print(f"   NodeId: {r['node_id']}")
                if r['readable']:
                    print(f"   ✅ Valor: {r['value']}")
                    
                    # Probar escribir si es boolean
                    if isinstance(r['value'], bool):
                        try:
                            node = client.get_node(r['node_id'])
                            original = r['value']
                            await node.write_value(not original)
                            new_val = await node.read_value()
                            print(f"   ✅ ESCRITURA OK: {original} -> {new_val}")
                            await node.write_value(original)  # Restaurar
                        except Exception as e:
                            print(f"   ⚠️ Escritura: {str(e)[:40]}")
                else:
                    print(f"   ❌ Error: {r['error']}")
                print()
        else:
            print("\n❌ No se encontraron los tags.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
