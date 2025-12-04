"""
================================================================================
    EXPLORACIÓN OPC UA - PLC VIEJO
    
    IP: 192.168.101.100
    Puerto: 55533
================================================================================
"""

import asyncio
from asyncua import Client, ua
from datetime import datetime

SERVER_URL = "opc.tcp://192.168.101.100:55533"

async def explore_plc():
    """Explorar el PLC viejo para encontrar tags."""
    
    print("=" * 80)
    print("   EXPLORACIÓN OPC UA - PLC VIEJO")
    print(f"   Servidor: {SERVER_URL}")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    client = Client(url=SERVER_URL)
    client.session_timeout = 60000  # 60 segundos
    
    try:
        print("\nIntentando conectar...")
        await client.connect()
        print("✓ CONEXIÓN EXITOSA\n")
        
        # =====================================================================
        # 1. INFORMACIÓN DEL SERVIDOR
        # =====================================================================
        print("=" * 80)
        print("1. INFORMACIÓN DEL SERVIDOR")
        print("=" * 80)
        
        try:
            server_node = client.get_node(ua.ObjectIds.Server)
            
            # Server Status
            status_node = client.get_node(ua.ObjectIds.Server_ServerStatus)
            try:
                status = await status_node.read_value()
                print(f"\n  Estado del servidor: {status}")
            except:
                pass
            
            # Build Info
            try:
                build_info = client.get_node(ua.ObjectIds.Server_ServerStatus_BuildInfo)
                product_name = await client.get_node(ua.ObjectIds.Server_ServerStatus_BuildInfo_ProductName).read_value()
                print(f"  Producto: {product_name}")
            except Exception as e:
                print(f"  No se pudo leer BuildInfo: {e}")
                
        except Exception as e:
            print(f"  Error obteniendo info del servidor: {e}")
        
        # =====================================================================
        # 2. NAMESPACES DISPONIBLES
        # =====================================================================
        print("\n" + "=" * 80)
        print("2. NAMESPACES DISPONIBLES")
        print("=" * 80)
        
        ns_array = await client.get_namespace_array()
        print(f"\nTotal de namespaces: {len(ns_array)}\n")
        
        for i, ns_uri in enumerate(ns_array):
            print(f"  ns={i}: {ns_uri}")
        
        # =====================================================================
        # 3. EXPLORAR ESTRUCTURA DEL SERVIDOR
        # =====================================================================
        print("\n" + "=" * 80)
        print("3. ESTRUCTURA DEL SERVIDOR (Nodos Raíz)")
        print("=" * 80)
        
        # Nodo raíz Objects
        objects_node = client.get_node(ua.ObjectIds.ObjectsFolder)
        
        async def browse_node(node, indent=0, max_depth=3):
            """Explorar nodo y sus hijos recursivamente."""
            if indent > max_depth:
                return
                
            prefix = "  " * indent
            
            try:
                browse_name = await node.read_browse_name()
                node_class = await node.read_node_class()
                
                class_str = str(node_class).split('.')[-1]
                print(f"{prefix}├─ {browse_name.Name} [{class_str}] - {node.nodeid}")
                
                # Si es Variable, intentar leer el valor
                if node_class == ua.NodeClass.Variable and indent <= max_depth:
                    try:
                        value = await node.read_value()
                        data_type = await node.read_data_type_as_variant_type()
                        if len(str(value)) < 100:
                            print(f"{prefix}   └─ Valor: {value} (Tipo: {data_type})")
                    except Exception as e:
                        print(f"{prefix}   └─ No se pudo leer valor")
                
                # Explorar hijos
                children = await node.get_children()
                for child in children[:20]:  # Limitar a 20 hijos por nivel
                    await browse_node(child, indent + 1, max_depth)
                    
                if len(children) > 20:
                    print(f"{prefix}  ... y {len(children) - 20} nodos más")
                    
            except Exception as e:
                print(f"{prefix}├─ Error: {e}")
        
        print("\nExplorando Objects Folder:")
        print("-" * 60)
        
        children = await objects_node.get_children()
        for child in children:
            await browse_node(child, indent=1, max_depth=2)
        
        # =====================================================================
        # 4. BUSCAR TAGS EN DIFERENTES NAMESPACES
        # =====================================================================
        print("\n" + "=" * 80)
        print("4. BÚSQUEDA DE TAGS EN NAMESPACES")
        print("=" * 80)
        
        # Intentar encontrar tags en diferentes formatos
        for ns in range(len(ns_array)):
            print(f"\n--- Explorando ns={ns} ---")
            try:
                # Buscar nodos en este namespace
                ns_node = client.get_node(f"ns={ns};i=85")  # ObjectsFolder
                children = await ns_node.get_children()
                print(f"  Encontrados {len(children)} nodos hijos")
                
                for child in children[:10]:
                    try:
                        name = await child.read_browse_name()
                        print(f"    - {name.Name}: {child.nodeid}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"  Error: {e}")
        
        # =====================================================================
        # 5. INTENTAR ALGUNOS TAGS COMUNES
        # =====================================================================
        print("\n" + "=" * 80)
        print("5. PRUEBA DE TAGS COMUNES")
        print("=" * 80)
        
        # Tags que podrían existir
        common_tags = [
            # Formatos típicos de Rockwell
            "ns=2;s=Local:1:I.Data",
            "ns=2;s=Controller Tags",
            "ns=1;s=Controller Tags",
            # Tags simples
            "ns=2;s=YEAR",
            "ns=1;s=YEAR",
            "ns=6;s=YEAR",
            # Otros formatos
            "ns=2;s=Program:MainProgram",
            "ns=1;s=Program:MainProgram",
        ]
        
        print("\nProbando tags comunes:")
        print("-" * 60)
        
        for tag in common_tags:
            try:
                node = client.get_node(tag)
                value = await node.read_value()
                print(f"  ✓ {tag}: {value}")
            except Exception as e:
                error_type = type(e).__name__
                if "BadNodeIdUnknown" in str(e):
                    print(f"  ✗ {tag}: No existe")
                else:
                    print(f"  ✗ {tag}: {error_type}")
        
        # =====================================================================
        # 6. LISTAR TODOS LOS PROGRAMAS/FOLDERS
        # =====================================================================
        print("\n" + "=" * 80)
        print("6. LISTADO DE PROGRAMAS Y FOLDERS")
        print("=" * 80)
        
        async def find_all_variables(node, path="", depth=0, max_depth=4):
            """Buscar todas las variables en el árbol."""
            if depth > max_depth:
                return []
                
            variables = []
            
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
                                variables.append((current_path, child.nodeid, value))
                            except:
                                variables.append((current_path, child.nodeid, "N/A"))
                        else:
                            # Recursivamente buscar en folders
                            sub_vars = await find_all_variables(child, current_path, depth + 1, max_depth)
                            variables.extend(sub_vars)
                            
                    except Exception as e:
                        pass
                        
            except Exception as e:
                pass
                
            return variables
        
        print("\nBuscando todas las variables disponibles...")
        print("-" * 60)
        
        all_vars = await find_all_variables(objects_node, "", 0, 4)
        
        print(f"\nEncontradas {len(all_vars)} variables:")
        for i, (path, nodeid, value) in enumerate(all_vars[:50]):
            val_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  {i+1}. {path}")
            print(f"      NodeId: {nodeid}")
            print(f"      Valor: {val_str}")
            
        if len(all_vars) > 50:
            print(f"\n  ... y {len(all_vars) - 50} variables más")
        
    except Exception as e:
        print(f"\n✗ ERROR DE CONEXIÓN: {e}")
        print("\nPosibles causas:")
        print("  1. El PLC no está encendido o conectado a la red")
        print("  2. La IP o puerto son incorrectos")
        print("  3. El servidor OPC UA no está habilitado")
        print("  4. Hay un firewall bloqueando la conexión")
        
    finally:
        try:
            await client.disconnect()
            print("\n✓ Desconectado del servidor")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(explore_plc())
