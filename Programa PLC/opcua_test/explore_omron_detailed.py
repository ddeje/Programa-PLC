"""
================================================================================
    EXPLORACIÓN DETALLADA - PLC OMRON VIEJO
    
    Enfocado en GlobalVars y tags del namespace 4
================================================================================
"""

import asyncio
from asyncua import Client, ua
from datetime import datetime

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def explore_global_vars():
    """Explorar GlobalVars del PLC OMRON."""
    
    print("=" * 80)
    print("   EXPLORACIÓN DETALLADA - PLC OMRON")
    print(f"   Servidor: {SERVER_URL}")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    client = Client(url=SERVER_URL)
    client.session_timeout = 60000
    
    try:
        print("\nConectando...")
        await client.connect()
        print("✓ Conectado\n")
        
        # =====================================================================
        # EXPLORAR GLOBALVARS
        # =====================================================================
        print("=" * 80)
        print("EXPLORANDO GlobalVars (ns=4)")
        print("=" * 80)
        
        # El nodo GlobalVars que vimos
        global_vars_node = client.get_node("ns=4;s=NxController.GlobalVars")
        
        print("\nListando todas las variables globales:")
        print("-" * 80)
        
        all_tags = []
        
        async def explore_node(node, path="", depth=0):
            """Explorar nodo recursivamente."""
            if depth > 6:
                return
            
            try:
                children = await node.get_children()
                
                for child in children:
                    try:
                        browse_name = await child.read_browse_name()
                        node_class = await child.read_node_class()
                        
                        current_path = f"{path}.{browse_name.Name}" if path else browse_name.Name
                        
                        if node_class == ua.NodeClass.Variable:
                            try:
                                value = await child.read_value()
                                data_type = await child.read_data_type_as_variant_type()
                                
                                tag_info = {
                                    'name': current_path,
                                    'nodeid': str(child.nodeid),
                                    'value': value,
                                    'type': str(data_type)
                                }
                                all_tags.append(tag_info)
                                
                                # Mostrar
                                val_str = str(value)
                                if len(val_str) > 60:
                                    val_str = val_str[:60] + "..."
                                    
                                print(f"  {current_path}")
                                print(f"      NodeId: {child.nodeid}")
                                print(f"      Tipo: {data_type}, Valor: {val_str}")
                                print()
                                
                            except Exception as e:
                                print(f"  {current_path}")
                                print(f"      NodeId: {child.nodeid}")
                                print(f"      Error leyendo: {e}")
                                print()
                        
                        # Explorar hijos (si es Object o Variable con hijos)
                        await explore_node(child, current_path, depth + 1)
                        
                    except Exception as e:
                        pass
                        
            except Exception as e:
                pass
        
        await explore_node(global_vars_node, "GlobalVars", 0)
        
        # =====================================================================
        # EXPLORAR Master_CPU / NxController
        # =====================================================================
        print("\n" + "=" * 80)
        print("EXPLORANDO Master_CPU (NxController)")
        print("=" * 80)
        
        master_cpu_node = client.get_node("ns=4;s=NxController")
        
        print("\nEstructura de Master_CPU:")
        print("-" * 80)
        
        children = await master_cpu_node.get_children()
        for child in children:
            try:
                browse_name = await child.read_browse_name()
                node_class = await child.read_node_class()
                class_str = str(node_class).split('.')[-1]
                print(f"  {browse_name.Name} [{class_str}] - {child.nodeid}")
                
                # Contar hijos
                sub_children = await child.get_children()
                if sub_children:
                    print(f"      ({len(sub_children)} hijos)")
            except Exception as e:
                print(f"  Error: {e}")
        
        # =====================================================================
        # EXPLORAR DeviceStatus
        # =====================================================================
        print("\n" + "=" * 80)
        print("EXPLORANDO DeviceStatus")
        print("=" * 80)
        
        device_status_node = client.get_node("ns=4;s=PLC.DeviceStatus")
        
        print("\nEstado del dispositivo:")
        print("-" * 80)
        
        await explore_node(device_status_node, "DeviceStatus", 0)
        
        # =====================================================================
        # RESUMEN
        # =====================================================================
        print("\n" + "=" * 80)
        print("RESUMEN DE TAGS ENCONTRADOS")
        print("=" * 80)
        
        print(f"\nTotal de tags encontrados: {len(all_tags)}")
        print("\n" + "-" * 80)
        
        # Agrupar por tipo
        types_count = {}
        for tag in all_tags:
            t = tag['type']
            types_count[t] = types_count.get(t, 0) + 1
        
        print("Por tipo de dato:")
        for t, count in sorted(types_count.items()):
            print(f"  {t}: {count} tags")
        
        # =====================================================================
        # EXPORTAR A CSV
        # =====================================================================
        print("\n" + "=" * 80)
        print("EXPORTANDO A CSV")
        print("=" * 80)
        
        import csv
        
        csv_file = "omron_plc_tags.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Tag Name', 'NodeId', 'Data Type', 'Current Value'])
            
            for tag in all_tags:
                val_str = str(tag['value'])
                if len(val_str) > 200:
                    val_str = val_str[:200] + "..."
                writer.writerow([tag['name'], tag['nodeid'], tag['type'], val_str])
        
        print(f"\n✓ Exportado a {csv_file}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            await client.disconnect()
            print("\n✓ Desconectado")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(explore_global_vars())
