"""Ver propiedades de Variable1"""
import asyncio
import uuid
from asyncua import Client, ua

async def main():
    client = Client("opc.tcp://192.168.101.100:55533")
    await client.connect()
    print("✓ Conectado\n")
    
    # GUID de Variable1
    guid = uuid.UUID("839c3529-1e4f-00f2-7c60-c4517c490413")
    node = client.get_node(ua.NodeId(guid, 9))
    
    # Leer todas las propiedades
    browse_name = await node.read_browse_name()
    display_name = await node.read_display_name()
    value = await node.read_value()
    node_id = node.nodeid
    
    print(f"NodeId:       {node_id}")
    print(f"BrowseName:   {browse_name}")
    print(f"DisplayName:  {display_name}")
    print(f"Valor:        {value}")
    
    await client.disconnect()

asyncio.run(main())
