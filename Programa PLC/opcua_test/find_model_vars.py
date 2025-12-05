"""
Buscar variables del Model de Optix (no del PLC)
que podamos usar para probar comunicacion
"""
import asyncio
from asyncua import Client

async def explore_model(node, path="", results=None, depth=0):
    """Explorar buscando variables del Model"""
    if results is None:
        results = []
    if depth > 4:
        return results
    
    try:
        name = await node.read_browse_name()
        node_class = await node.read_node_class()
        current_path = f"{path}/{name.Name}" if path else name.Name
        
        # Si es variable, intentar leer
        if node_class.value == 2:  # Variable
            try:
                val = await node.read_value()
                results.append({
                    "path": current_path,
                    "node_id": str(node),
                    "value": val,
                    "readable": True
                })
            except:
                pass
        
        # Explorar hijos si es carpeta relevante
        if any(x in name.Name for x in ["Model", "Global", "Var", "UI", "Alias"]):
            children = await node.get_children()
            for child in children[:20]:
                await explore_model(child, current_path, results, depth + 1)
        elif depth < 2:
            children = await node.get_children()
            for child in children[:15]:
                await explore_model(child, current_path, results, depth + 1)
                
    except:
        pass
    
    return results

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        print("Buscando variables legibles (Model, GlobalVars, UI)...")
        print("="*60)
        
        objects = client.nodes.objects
        results = await explore_model(objects)
        
        print(f"\nEncontradas {len(results)} variables legibles:\n")
        
        for r in results[:20]:  # Mostrar primeras 20
            val_str = str(r['value'])[:40]
            print(f"📊 {r['path']}")
            print(f"   NodeId: {r['node_id']}")
            print(f"   Valor: {val_str}")
            print()
        
        if results:
            # Probar escribir en la primera variable que no sea de sistema
            print("="*60)
            print("Probando escritura...")
            
            for r in results:
                if "Server" not in r['path']:
                    try:
                        node = client.get_node(r['node_id'])
                        original = r['value']
                        
                        # Intentar escribir
                        if isinstance(original, bool):
                            await node.write_value(not original)
                            new_val = await node.read_value()
                            print(f"✅ ESCRITURA OK en: {r['path']}")
                            print(f"   Original: {original} -> Nuevo: {new_val}")
                            # Restaurar
                            await node.write_value(original)
                            break
                        elif isinstance(original, (int, float)):
                            await node.write_value(original + 1)
                            new_val = await node.read_value()
                            print(f"✅ ESCRITURA OK en: {r['path']}")
                            print(f"   Original: {original} -> Nuevo: {new_val}")
                            await node.write_value(original)
                            break
                        elif isinstance(original, str):
                            await node.write_value("TEST_PYTHON")
                            new_val = await node.read_value()
                            print(f"✅ ESCRITURA OK en: {r['path']}")
                            print(f"   Original: {original} -> Nuevo: {new_val}")
                            await node.write_value(original)
                            break
                    except Exception as e:
                        continue
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
