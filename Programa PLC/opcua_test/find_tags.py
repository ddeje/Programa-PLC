"""
Explorar namespaces y tags en Optix Edge
"""
import asyncio
from asyncua import Client

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        # Ver namespaces disponibles
        ns_array = await client.get_namespace_array()
        print("NAMESPACES:")
        for i, ns in enumerate(ns_array):
            print(f"  ns={i}: {ns}")
        
        print("\n" + "="*50)
        print("BUSCANDO TAGS...")
        
        # Probar diferentes formatos de NodeId
        formatos = [
            "ns=6;s=GlobalVars.EgComIn_Heartbeat",
            "ns=9;s=GlobalVars.EgComIn_Heartbeat",
            "ns=6;s=EgComIn_Heartbeat",
            "ns=9;s=EgComIn_Heartbeat",
            "ns=6;s=Controller Tags.EgComIn_Heartbeat",
            "ns=9;s=Controller Tags.EgComIn_Heartbeat",
        ]
        
        for fmt in formatos:
            try:
                node = client.get_node(fmt)
                val = await node.read_value()
                print(f"✅ ENCONTRADO: {fmt} = {val}")
            except:
                print(f"❌ No existe: {fmt}")
        
        print("\n" + "="*50)
        print("EXPLORANDO NODOS RAÍZ...")
        
        # Explorar Objects folder
        objects = client.nodes.objects
        children = await objects.get_children()
        print("\nHijos de Objects:")
        for child in children:
            name = await child.read_browse_name()
            print(f"  - {name.Name} ({child})")
            
            # Explorar un nivel más
            try:
                subchildren = await child.get_children()
                for sub in subchildren[:5]:  # Solo primeros 5
                    subname = await sub.read_browse_name()
                    print(f"      └─ {subname.Name} ({sub})")
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
