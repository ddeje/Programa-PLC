"""
Explorar Program:EdgeGateway para encontrar los tags
"""
import asyncio
from asyncua import Client

async def explore_all(node, level=0):
    """Explorar todo recursivamente"""
    indent = "  " * level
    try:
        name = await node.read_browse_name()
        node_class = await node.read_node_class()
        
        # Si es variable, mostrar valor
        if node_class.value == 2:  # Variable
            try:
                val = await node.read_value()
                print(f"{indent}📊 {name.Name} = {val}")
                print(f"{indent}   NodeId: {node}")
            except Exception as e:
                print(f"{indent}📊 {name.Name} (error: {e})")
                print(f"{indent}   NodeId: {node}")
        else:
            print(f"{indent}📁 {name.Name}")
            print(f"{indent}   NodeId: {node}")
        
        # Explorar hijos
        children = await node.get_children()
        for child in children:
            await explore_all(child, level + 1)
            
    except Exception as e:
        print(f"{indent}Error: {e}")

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        # Ir directo a Tags
        tags_node = client.get_node("ns=9;g=8380cfae-cb36-f81b-c807-e1e07565fc20")
        print("Explorando Tags...")
        print("="*60)
        
        await explore_all(tags_node)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\n" + "="*60)
        print("Desconectado")

if __name__ == "__main__":
    asyncio.run(main())
