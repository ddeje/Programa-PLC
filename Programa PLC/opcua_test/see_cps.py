"""Ver hijos de CPS001"""
import asyncio
from asyncua import Client

async def main():
    c = Client("opc.tcp://192.168.101.100:59100", timeout=5)
    await c.connect()
    
    cps = c.get_node("ns=9;g=84691cbf-c66c-0b67-0321-8ef9dbb4a868")
    print("Hijos de CPS001:")
    for n in await cps.get_children():
        nm = await n.read_browse_name()
        print(f"  {nm.Name} | {n}")
        
        # Un nivel más
        for n2 in await n.get_children():
            nm2 = await n2.read_browse_name()
            print(f"    {nm2.Name} | {n2}")
    
    await c.disconnect()

asyncio.run(main())
