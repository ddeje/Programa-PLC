import asyncio
import logging
from asyncua import Client

logging.disable(logging.WARNING)

async def main():
    # Por ahora puerto 59100, cuando configure Optix sera 55533
    url = 'opc.tcp://192.168.101.100:59100/'
    print('Conectando a %s...' % url)
    
    async with Client(url=url) as client:
        print('Conectado!')
        structures = await client.load_data_type_definitions()
        print('Tipos cargados')
        
        # Por ahora ns=9 (Optix actual), cuando configure sera ns=4
        # Formato final sera: ns=4;s=GlobalVars.EgComIn_RecordNotFound
        node_id = 'ns=9;s=CPS001.CommDrivers.RAEtherNet_IPDriver1.RAEtherNet_IPStation1.Tags.Program:EdgeGateway.RecordNotFound'
        node = client.get_node(node_id)
        
        val_antes = await node.read_value()
        print('ANTES: RecordNotFound = %s' % val_antes)
        
        await node.write_value(True)
        print('ESCRIBI: True (1)')
        
        val_despues = await node.read_value()
        print('DESPUES: RecordNotFound = %s' % val_despues)

if __name__ == '__main__':
    asyncio.run(main())
