"""
================================================================================
    EDGE GATEWAY CLIENT - Simulador de Edge Gateway
    
    Este programa Python actúa como el Edge Gateway, comunicándose con
    el Optix Edge de Rockwell vía OPC UA.
    
    Servidor: opc.tcp://192.168.101.100:59100 (FTOptixApplication)
================================================================================
"""

import asyncio
import logging
from datetime import datetime
from asyncua import Client, ua

# Silenciar logs de asyncua
logging.getLogger('asyncua').setLevel(logging.WARNING)

OPTIX_URL = "opc.tcp://192.168.101.100:59100/"


async def explore_and_find_tags():
    """Explora el servidor y encuentra los tags de comunicación."""
    
    print("=" * 70)
    print("🔍 EXPLORANDO OPTIX EDGE - FTOptixApplication")
    print("=" * 70)
    
    client = Client(url=OPTIX_URL, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        await client.load_data_type_definitions()
        
        # Ver namespaces
        print("=== NAMESPACES DISPONIBLES ===")
        ns_array = await client.get_namespace_array()
        for i, ns in enumerate(ns_array):
            print(f"  ns={i}: {ns}")
        
        # Explorar Objects
        print("\n=== ESTRUCTURA DEL SERVIDOR ===")
        objects = client.nodes.objects
        
        found_tags = []
        
        async def browse(node, path="", level=0):
            if level > 4:
                return
            try:
                children = await node.get_children()
                for child in children:
                    name = await child.read_browse_name()
                    node_id = child.nodeid.to_string()
                    current_path = f"{path}/{name.Name}" if path else name.Name
                    
                    # Buscar tags de comunicación
                    name_lower = name.Name.lower()
                    is_interesting = any(x in name_lower for x in 
                        ['egcom', 'global', 'heartbeat', 'barcode', 'uuid', 'write', 'comm'])
                    
                    if is_interesting or level < 2:
                        indent = "  " * level
                        
                        # Intentar leer valor
                        try:
                            value = await child.read_value()
                            dtype = await child.read_data_type_as_variant_type()
                            print(f"{indent}📌 {name.Name} = {value} [{dtype}]")
                            print(f"{indent}   NodeId: {node_id}")
                            
                            if 'egcom' in name_lower or 'heartbeat' in name_lower:
                                found_tags.append({
                                    'name': name.Name,
                                    'node_id': node_id,
                                    'value': value,
                                    'type': str(dtype)
                                })
                        except:
                            print(f"{indent}📁 {name.Name}")
                        
                        await browse(child, current_path, level + 1)
                        
            except Exception as e:
                pass
        
        await browse(objects)
        
        # Buscar tags específicos en diferentes formatos
        print("\n=== BUSCANDO TAGS ESPECÍFICOS ===")
        
        tag_patterns = [
            # Formato GlobalVars
            "GlobalVars.EgComIn_Heartbeat",
            "GlobalVars.EgComOut_BarcodeReq",
            # Formato directo
            "EgComIn_Heartbeat",
            "EgComOut_BarcodeReq",
            # Formato con Model
            "Model/GlobalVars/EgComIn_Heartbeat",
        ]
        
        for ns_idx in range(len(ns_array)):
            for pattern in tag_patterns:
                try:
                    node = client.get_node(f"ns={ns_idx};s={pattern}")
                    value = await node.read_value()
                    print(f"  ✅ ENCONTRADO: ns={ns_idx};s={pattern} = {value}")
                    found_tags.append({
                        'name': pattern,
                        'node_id': f"ns={ns_idx};s={pattern}",
                        'value': value
                    })
                except:
                    pass
        
        print("\n=== TAGS DE COMUNICACIÓN ENCONTRADOS ===")
        if found_tags:
            for tag in found_tags:
                print(f"  • {tag['name']}: {tag['node_id']}")
        else:
            print("  ⚠️ No se encontraron tags EgCom*")
            print("  Buscando cualquier variable...")
            
            # Buscar en todos los namespaces variables que podamos leer
            for ns_idx in [2, 3, 4, 5, 6]:
                try:
                    ns_node = client.get_node(ua.NodeId(85, ns_idx))  # Objects folder
                    children = await ns_node.get_children()
                    for child in children[:5]:
                        name = await child.read_browse_name()
                        print(f"    ns={ns_idx}: {name.Name}")
                except:
                    pass
        
        await client.disconnect()
        return found_tags
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


async def main():
    tags = await explore_and_find_tags()
    
    print("\n" + "=" * 70)
    print("📋 RESUMEN")
    print("=" * 70)
    print(f"Tags encontrados: {len(tags)}")
    for t in tags:
        print(f"  - {t['node_id']}")


if __name__ == "__main__":
    asyncio.run(main())
