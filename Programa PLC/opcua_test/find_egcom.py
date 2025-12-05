"""Buscar EgComIn en todo el servidor"""
import asyncio
from asyncua import Client

async def find_egcom(node, depth=0):
    if depth > 6: return
    try:
        nm = await node.read_browse_name()
        
        if "EgCom" in nm.Name or "Heartbeat" in nm.Name or "RecordNotFound" in nm.Name or "UUID" in nm.Name:
            nc = await node.read_node_class()
            if nc.value == 2:
                try:
                    v = await node.read_value()
                    print(f"✅ {nm.Name} = {v} | {node}")
                except Exception as e:
                    print(f"❌ {nm.Name} | {node} | Error: {str(e)[:30]}")
            else:
                print(f"📁 {nm.Name} | {node}")
        
        for c in await node.get_children():
            await find_egcom(c, depth+1)
    except: pass

async def main():
    c = Client("opc.tcp://192.168.101.100:59100", timeout=10)
    await c.connect()
    print("Buscando EgComIn_Heartbeat, EgComIn_RecordNotFound, EgComIn_UUID_pull...\n")
    await find_egcom(c.nodes.objects)
    print("\nListo")
    await c.disconnect()

asyncio.run(main())
