"""Buscar GlobalVars rapido"""
import asyncio
from asyncua import Client

async def scan(node, depth=0):
    if depth > 4: return
    try:
        name = await node.read_browse_name()
        if "Global" in name.Name or "EgCom" in name.Name or "Heartbeat" in name.Name:
            nc = await node.read_node_class()
            if nc.value == 2:
                try:
                    v = await node.read_value()
                    print(f"✅ {name.Name} = {v} | {node}")
                except:
                    print(f"⚠️ {name.Name} | {node}")
            else:
                print(f"📁 {name.Name} | {node}")
        for c in await node.get_children():
            await scan(c, depth+1)
    except: pass

async def main():
    client = Client("opc.tcp://192.168.101.100:59100", timeout=10)
    await client.connect()
    print("Buscando GlobalVars, EgCom, Heartbeat...\n")
    await scan(client.nodes.objects)
    await client.disconnect()

asyncio.run(main())
