"""Explorar OPC-UA Server To Edge Gateway"""
import asyncio
from asyncua import Client

async def explore(node, depth=0):
    if depth > 3: return
    try:
        nm = await node.read_browse_name()
        nc = await node.read_node_class()
        indent = "  " * depth
        
        if nc.value == 2:  # Variable
            try:
                v = await node.read_value()
                print(f"{indent}✅ {nm.Name} = {v}")
            except:
                print(f"{indent}❌ {nm.Name}")
        else:
            print(f"{indent}📁 {nm.Name}")
        
        for c in await node.get_children():
            await explore(c, depth+1)
    except: pass

async def main():
    c = Client("opc.tcp://192.168.101.100:59100", timeout=5)
    await c.connect()
    
    # OPC-UA Server To Edge Gateway
    folder = c.get_node("ns=9;g=1d5ca422-21c5-5985-f3b3-2f5557b4499d")
    print("OPC-UA Server To Edge Gateway:\n")
    await explore(folder)
    
    await c.disconnect()

asyncio.run(main())
