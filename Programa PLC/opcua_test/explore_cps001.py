"""
Explorar CPS001 para encontrar los tags GlobalVars
"""
import asyncio
from asyncua import Client

async def explore_node(node, level=0, max_depth=4):
    """Explorar nodo recursivamente"""
    if level > max_depth:
        return
    
    indent = "  " * level
    try:
        name = await node.read_browse_name()
        node_class = await node.read_node_class()
        
        # Si es variable, mostrar valor
        if node_class.value == 2:  # Variable
            try:
                val = await node.read_value()
                print(f"{indent}📊 {name.Name} = {val} [{node}]")
            except:
                print(f"{indent}📊 {name.Name} [{node}]")
        else:
            print(f"{indent}📁 {name.Name} [{node}]")
        
        # Buscar si contiene "EgCom" o "GlobalVars"
        if "EgCom" in name.Name or "GlobalVars" in name.Name or "Heartbeat" in name.Name:
            print(f"{indent}   ⭐ ENCONTRADO!")
        
        # Explorar hijos
        children = await node.get_children()
        for child in children:
            await explore_node(child, level + 1, max_depth)
            
    except Exception as e:
        pass

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        # Ir directo a CPS001
        cps001 = client.get_node("ns=9;g=84691cbf-c66c-0b67-0321-8ef9dbb4a868")
        print("Explorando CPS001...")
        print("="*60)
        
        await explore_node(cps001, max_depth=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
