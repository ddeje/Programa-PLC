"""
Explorar Program:EdgeGateway y listar TODOS los tags
"""
import asyncio
from asyncua import Client

async def list_all_children(node, path="", depth=0):
    """Listar todos los hijos"""
    if depth > 6:
        return
    
    try:
        name = await node.read_browse_name()
        node_class = await node.read_node_class()
        current_path = f"{path}.{name.Name}" if path else name.Name
        indent = "  " * depth
        
        if node_class.value == 2:  # Variable
            try:
                val = await node.read_value()
                print(f"{indent}✅ {name.Name} = {val}")
                print(f"{indent}   NodeId: {node}")
            except Exception as e:
                err = str(e)[:30]
                print(f"{indent}❌ {name.Name} (Error: {err})")
                print(f"{indent}   NodeId: {node}")
        else:
            print(f"{indent}📁 {name.Name}")
        
        children = await node.get_children()
        for child in children:
            await list_all_children(child, current_path, depth + 1)
            
    except Exception as e:
        pass

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=15)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        # Ir a Program:EdgeGateway
        edge_gateway = client.get_node("ns=9;g=69437ef4-a4c1-7ed2-6824-add4093b1757")
        
        print("Explorando Program:EdgeGateway...")
        print("="*60)
        
        await list_all_children(edge_gateway)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\n" + "="*60)
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
