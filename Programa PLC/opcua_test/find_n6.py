"""Buscar n6 en el servidor"""
import asyncio
from asyncua import Client

async def search(node, path=""):
    try:
        bn = await node.read_browse_name()
        p = f"{path}/{bn.Name}" if path else bn.Name
        if "n6" in bn.Name.lower() or bn.Name == "n6":
            print(f"Encontrado: {bn.Name}")
            print(f"  Path: {p}")
            print(f"  NodeId: {node.nodeid}")
        for c in await node.get_children():
            await search(c, p)
    except: pass

async def main():
    client = Client("opc.tcp://192.168.101.100:55533")
    await client.connect()
    print("Buscando n6...")
    await search(client.get_root_node())
    await client.disconnect()
    print("Listo")

asyncio.run(main())
