"""
Buscar EgComIn_Heartbeat en el servidor OPC UA de Optix
Servidor: 192.168.101.100:55533
"""

import asyncio
from asyncua import Client, ua

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def browse_deep(client, node, path="", target="EgComIn", max_level=8, level=0):
    """Buscar nodos que contengan el target"""
    if level > max_level:
        return
    
    try:
        children = await node.get_children()
        for child in children:
            try:
                name = await child.read_browse_name()
                node_id = child.nodeid
                current_path = f"{path}/{name.Name}" if path else name.Name
                
                # Si el nombre contiene lo que buscamos, mostrarlo
                if target.lower() in name.Name.lower() or "heartbeat" in name.Name.lower():
                    print(f"✓ ENCONTRADO: {current_path}")
                    print(f"  NodeId: {node_id}")
                    try:
                        value = await child.read_value()
                        print(f"  Valor: {value}")
                    except:
                        pass
                    print()
                
                # Continuar explorando
                await browse_deep(client, child, current_path, target, max_level, level + 1)
            except Exception as e:
                pass
    except Exception as e:
        pass

async def explore_tags_node(client):
    """Explorar el nodo Tags directamente"""
    tags_path = "ns=9;s=CPS001.CommDrivers.RAEtherNet_IPDriver1.RAEtherNet_IPStation1.Tags"
    print(f"\nExplorando: {tags_path}")
    print("-" * 70)
    
    try:
        tags_node = client.get_node(tags_path)
        children = await tags_node.get_children()
        
        print(f"Tags encontrados ({len(children)}):\n")
        for child in children[:50]:  # Limitar a 50
            try:
                name = await child.read_browse_name()
                node_id = child.nodeid
                print(f"  {name.Name}")
                print(f"    NodeId: {node_id}")
                
                # Intentar leer valor
                try:
                    value = await child.read_value()
                    print(f"    Valor: {value}")
                except Exception as e:
                    print(f"    (No se pudo leer valor)")
                print()
            except:
                pass
                
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print(f"Buscando EgComIn_Heartbeat en: {SERVER_URL}")
    print("=" * 70)
    
    client = Client(SERVER_URL)
    client.timeout = 30
    
    try:
        await client.connect()
        print("✓ Conectado\n")
        
        # Primero explorar el nodo Tags
        await explore_tags_node(client)
        
        # Luego buscar EgComIn en todo el árbol
        print("\n" + "=" * 70)
        print("Buscando 'EgComIn' en todo el árbol...")
        print("-" * 70)
        
        cps_node = client.get_node("ns=9;s=CPS001")
        await browse_deep(client, cps_node, "CPS001", "EgCom", 10)
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
