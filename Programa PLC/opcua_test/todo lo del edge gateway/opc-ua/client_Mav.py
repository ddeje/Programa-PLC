#Simple Python OPC-UA Client
#code repository at https://github.com/techbeast-org/opc-ua
#LGPL-3.0 License

import asyncio
import logging
import time
import json

import asyncua
from asyncua import Client, Node, ua
logger = logging.getLogger('asyncua')
logging.disable(logging.WARNING)


async def dict_format(keys, values):
  return dict(zip(keys, values))


async def get_subnodes(client, nodes, level, max_level):
    if level < max_level:
        node_tree = {}
        node_tree_str = {}
        for kk in range(len(nodes)):
            aux_node = client.get_node(nodes[kk])
            aux_node_name = await aux_node.read_browse_name()
            aux_node_str = aux_node.nodeid.to_string()
            aux_subnodes = await aux_node.get_children()
            try:
                node_tree[aux_node_name.to_string()], node_tree_str[aux_node_str] = \
                    await get_subnodes(client, aux_subnodes, level+1, max_level)
            except:
                pass
        return node_tree, node_tree_str
    else:
        return {}


async def main():
    while True:
        url = "opc.tcp://192.168.101.100:59100/"
        #url = "opc.tcp://172.18.20.10:4840/"
        async with Client(url=url) as client:
            await client.load_data_type_definitions()
            data_list = []
            #idx = 2
            root = client.get_root_node()
            aux_nodes = await root.get_children()
            objects_node = aux_nodes[0]
            nodes = await objects_node.get_children()
            node_tree, node_tree_str = await get_subnodes(client, nodes, 1, 9)
            print(json.dumps(node_tree, indent=4))
            print(json.dumps(node_tree_str, indent=4))
            await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
