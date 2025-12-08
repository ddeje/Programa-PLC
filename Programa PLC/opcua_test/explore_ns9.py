import asyncio
from asyncua import Client

OPTIX_URL = "opc.tcp://192.168.101.100:55533"

async def explore():
    async with Client(url=OPTIX_URL) as client:
        print("✅ Conectado!\n")
        
        # Buscar en root/Objects
        root = client.get_root_node()
        objects = await root.get_child(["0:Objects"])
        
        print("📂 Explorando Objects...")
        children = await objects.get_children()
        
        for child in children:
            name = await child.read_browse_name()
            print(f"\n  {name.Name} -> {child.nodeid}")
            
            # Explorar hijos
            try:
                sub_children = await child.get_children()
                for sub in sub_children:
                    sub_name = await sub.read_browse_name()
                    print(f"    {sub_name.Name} -> {sub.nodeid}")
                    
                    # Buscar más profundo
                    try:
                        deep = await sub.get_children()
                        for d in deep:
                            d_name = await d.read_browse_name()
                            print(f"      {d_name.Name} -> {d.nodeid}")
                    except:
                        pass
            except:
                pass

if __name__ == "__main__":
    asyncio.run(explore())
