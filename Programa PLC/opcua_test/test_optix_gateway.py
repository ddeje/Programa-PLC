"""
Test de Conexión OPC UA - FactoryTalk Optix Gateway
====================================================
Script para probar conectividad con Optix y verificar tags del Edge Gateway.

Servidor: opc.tcp://192.168.101.100:59100
Namespace: 9

Tags a verificar:
- GlobalVars.EgComIn_Heartbeat           [Boolean]
- GlobalVars.EgComIn_RecordNotFound      [Boolean]
- GlobalVars.EgComIn_UUID_pull           [ExtensionObject]
- GlobalVars.EgComIn_WriteToDb_Confirmation [Boolean]
- GlobalVars.EgComOut_BarcodeReq         [Boolean]
- GlobalVars.EgComOut_BarcodeValue       [String]
- GlobalVars.EgComOut_UUIDReq            [Boolean]
- GlobalVars.EgComOut_WriteToDb          [Boolean]
"""

import asyncio
import sys
from datetime import datetime
from asyncua import Client, ua

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
OPTIX_URL = "opc.tcp://192.168.101.100:59100"
NAMESPACE = 9

# Tags del Edge Gateway
GATEWAY_TAGS = {
    # Inputs TO PLC (Gateway escribe estos)
    "EgComIn_Heartbeat": "Boolean",
    "EgComIn_RecordNotFound": "Boolean", 
    "EgComIn_UUID_pull": "ExtensionObject",
    "EgComIn_WriteToDb_Confirmation": "Boolean",
    # Outputs FROM PLC (Gateway lee estos)
    "EgComOut_BarcodeReq": "Boolean",
    "EgComOut_BarcodeValue": "String",
    "EgComOut_UUIDReq": "Boolean",
    "EgComOut_WriteToDb": "Boolean",
}

# ============================================================================
# UTILIDADES DE IMPRESIÓN
# ============================================================================
def print_header(text: str):
    """Imprime encabezado con formato"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text: str):
    """Imprime sección con formato"""
    print(f"\n--- {text} ---")

def print_ok(text: str):
    """Imprime mensaje de éxito"""
    print(f"  ✓ {text}")

def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"  ✗ {text}")

def print_info(text: str):
    """Imprime información"""
    print(f"  ► {text}")

def print_tag(name: str, value, datatype: str = ""):
    """Imprime valor de tag con formato"""
    type_str = f" [{datatype}]" if datatype else ""
    print(f"    {name:40} = {value}{type_str}")

def timestamp():
    """Retorna timestamp actual"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

# ============================================================================
# FUNCIONES DE PRUEBA
# ============================================================================
async def test_connection(client: Client) -> bool:
    """Prueba conexión básica al servidor OPC UA"""
    print_section("TEST 1: Conexión al servidor")
    print_info(f"Conectando a: {OPTIX_URL}")
    
    try:
        await client.connect()
        print_ok("Conexión establecida!")
        
        # Obtener información del servidor
        server_node = client.get_node(ua.ObjectIds.Server)
        server_status = await client.get_node(ua.ObjectIds.Server_ServerStatus).read_value()
        print_ok(f"Estado del servidor: {server_status.State}")
        print_ok(f"Tiempo del servidor: {server_status.CurrentTime}")
        
        return True
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        return False

async def explore_namespaces(client: Client):
    """Explora los namespaces disponibles"""
    print_section("TEST 2: Explorar Namespaces")
    
    try:
        ns_array = await client.get_namespace_array()
        print_info(f"Namespaces disponibles ({len(ns_array)}):")
        for i, ns in enumerate(ns_array):
            marker = " ◄── OBJETIVO" if i == NAMESPACE else ""
            print(f"      ns={i}: {ns}{marker}")
        
        if NAMESPACE < len(ns_array):
            print_ok(f"Namespace {NAMESPACE} existe: {ns_array[NAMESPACE]}")
        else:
            print_error(f"Namespace {NAMESPACE} NO existe! Máximo: {len(ns_array)-1}")
            
    except Exception as e:
        print_error(f"Error explorando namespaces: {e}")

async def explore_namespace_nodes(client: Client):
    """Explora nodos en el namespace objetivo"""
    print_section("TEST 3: Explorar Nodos en Namespace 9")
    
    try:
        # Intentar encontrar el nodo Objects
        objects_node = client.get_node(ua.ObjectIds.ObjectsFolder)
        print_info("Explorando ObjectsFolder...")
        
        children = await objects_node.get_children()
        print_info(f"Hijos de ObjectsFolder ({len(children)}):")
        
        for child in children[:15]:  # Limitar a 15
            try:
                browse_name = await child.read_browse_name()
                node_class = await child.read_node_class()
                print(f"      {child.nodeid} - {browse_name.Name} [{node_class}]")
            except:
                print(f"      {child.nodeid} - (error leyendo)")
                
        if len(children) > 15:
            print(f"      ... y {len(children) - 15} más")
            
    except Exception as e:
        print_error(f"Error explorando nodos: {e}")

async def find_globalvars_node(client: Client):
    """Intenta encontrar el nodo GlobalVars de diferentes formas"""
    print_section("TEST 4: Buscar GlobalVars")
    
    # Diferentes formatos de NodeID a probar
    node_formats = [
        f"ns={NAMESPACE};s=GlobalVars",
        f"ns={NAMESPACE};s=GlobalVars.EgComIn_Heartbeat",
        f"ns={NAMESPACE};s=Root.GlobalVars",
        f"ns={NAMESPACE};s=Root.GlobalVars.EgComIn_Heartbeat",
        f"ns={NAMESPACE};s=/GlobalVars",
        f"ns={NAMESPACE};s=/GlobalVars/EgComIn_Heartbeat",
        f"ns={NAMESPACE};s=Objects.GlobalVars",
        f"ns={NAMESPACE};s=EgComIn_Heartbeat",
    ]
    
    print_info("Probando diferentes formatos de NodeID:")
    
    found_format = None
    for node_format in node_formats:
        try:
            node = client.get_node(node_format)
            value = await node.read_value()
            print_ok(f"ENCONTRADO: {node_format} = {value}")
            found_format = node_format
        except Exception as e:
            error_short = str(e).split('\n')[0][:50]
            print(f"      ✗ {node_format}")
            # print(f"        Error: {error_short}...")
    
    return found_format

async def read_all_tags(client: Client, base_format: str = None):
    """Lee todos los tags del gateway"""
    print_section("TEST 5: Leer Tags del Gateway")
    
    # Si encontramos un formato válido, usarlo
    if base_format:
        # Extraer el patrón base
        if "EgCom" in base_format:
            base = base_format.rsplit(".", 1)[0] if "." in base_format else f"ns={NAMESPACE};s=GlobalVars"
        else:
            base = base_format
    else:
        base = f"ns={NAMESPACE};s=GlobalVars"
    
    print_info(f"Usando base: {base}")
    print_info("Leyendo tags:")
    
    results = {}
    for tag_name, expected_type in GATEWAY_TAGS.items():
        node_id = f"{base}.{tag_name}" if not base.endswith(tag_name) else base
        # Si el base ya tiene el prefijo ns=X;s=, construir correctamente
        if not node_id.startswith("ns="):
            node_id = f"ns={NAMESPACE};s=GlobalVars.{tag_name}"
        else:
            node_id = f"ns={NAMESPACE};s=GlobalVars.{tag_name}"
            
        try:
            node = client.get_node(node_id)
            value = await node.read_value()
            data_type = await node.read_data_type_as_variant_type()
            results[tag_name] = {"value": value, "type": str(data_type), "status": "OK"}
            print_ok(f"{tag_name:40} = {value} [{data_type}]")
        except Exception as e:
            results[tag_name] = {"value": None, "type": expected_type, "status": "ERROR", "error": str(e)}
            print_error(f"{tag_name:40} - Error: {str(e)[:40]}")
    
    return results

async def test_heartbeat_write(client: Client):
    """Prueba escribir al tag Heartbeat"""
    print_section("TEST 6: Prueba de Escritura (Heartbeat)")
    
    node_id = f"ns={NAMESPACE};s=GlobalVars.EgComIn_Heartbeat"
    
    try:
        node = client.get_node(node_id)
        
        # Leer valor actual
        current = await node.read_value()
        print_info(f"Valor actual: {current}")
        
        # Escribir valor opuesto
        new_value = not current
        print_info(f"Escribiendo: {new_value}")
        
        await node.write_value(ua.DataValue(ua.Variant(new_value, ua.VariantType.Boolean)))
        
        # Verificar escritura
        verify = await node.read_value()
        if verify == new_value:
            print_ok(f"Escritura exitosa! Nuevo valor: {verify}")
        else:
            print_error(f"Escritura falló. Esperado: {new_value}, Actual: {verify}")
            
        # Restaurar valor original
        await node.write_value(ua.DataValue(ua.Variant(current, ua.VariantType.Boolean)))
        print_info(f"Valor restaurado a: {current}")
        
        return True
    except Exception as e:
        print_error(f"Error en escritura: {e}")
        return False

async def monitor_tags_live(client: Client, duration: int = 30):
    """Monitorea tags en tiempo real"""
    print_section(f"TEST 7: Monitoreo en Vivo ({duration} segundos)")
    print_info("Presiona Ctrl+C para detener")
    print()
    
    tag_names = list(GATEWAY_TAGS.keys())
    
    # Obtener nodos
    nodes = {}
    for tag in tag_names:
        node_id = f"ns={NAMESPACE};s=GlobalVars.{tag}"
        nodes[tag] = client.get_node(node_id)
    
    # Cabecera
    print(f"  {'TIMESTAMP':<12} | ", end="")
    for tag in tag_names:
        short_name = tag.replace("EgCom", "").replace("In_", "I:").replace("Out_", "O:")
        print(f"{short_name:<12} | ", end="")
    print()
    print("  " + "-" * 120)
    
    start_time = asyncio.get_event_loop().time()
    last_values = {}
    
    try:
        while asyncio.get_event_loop().time() - start_time < duration:
            values = {}
            changed = False
            
            for tag, node in nodes.items():
                try:
                    value = await node.read_value()
                    values[tag] = value
                    if tag in last_values and last_values[tag] != value:
                        changed = True
                except:
                    values[tag] = "ERR"
            
            # Imprimir línea
            print(f"  {timestamp():<12} | ", end="")
            for tag in tag_names:
                val = values.get(tag, "?")
                # Formatear valor
                if isinstance(val, bool):
                    val_str = "TRUE" if val else "FALSE"
                elif isinstance(val, str):
                    val_str = val[:10] if len(str(val)) > 10 else val
                else:
                    val_str = str(val)[:10]
                
                # Marcar si cambió
                if tag in last_values and last_values[tag] != val:
                    val_str = f"*{val_str}*"
                    
                print(f"{val_str:<12} | ", end="")
            print()
            
            last_values = values.copy()
            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n  [Monitoreo detenido por usuario]")

async def interactive_menu(client: Client):
    """Menú interactivo para pruebas"""
    print_header("MENÚ INTERACTIVO")
    
    while True:
        print("\n  Opciones:")
        print("    1. Leer todos los tags")
        print("    2. Toggle Heartbeat")
        print("    3. Monitoreo en vivo (30s)")
        print("    4. Escribir valor a tag específico")
        print("    5. Explorar nodos")
        print("    0. Salir")
        
        try:
            choice = input("\n  Selección: ").strip()
        except EOFError:
            break
            
        if choice == "0":
            break
        elif choice == "1":
            await read_all_tags(client)
        elif choice == "2":
            await test_heartbeat_write(client)
        elif choice == "3":
            await monitor_tags_live(client)
        elif choice == "4":
            await write_specific_tag(client)
        elif choice == "5":
            await explore_namespace_nodes(client)
        else:
            print("  Opción no válida")

async def write_specific_tag(client: Client):
    """Escribe un valor a un tag específico"""
    print_section("Escribir a Tag Específico")
    
    print("  Tags disponibles:")
    for i, tag in enumerate(GATEWAY_TAGS.keys(), 1):
        print(f"    {i}. {tag}")
    
    try:
        tag_num = int(input("  Número de tag: ")) - 1
        tag_name = list(GATEWAY_TAGS.keys())[tag_num]
        tag_type = GATEWAY_TAGS[tag_name]
        
        print(f"  Tag seleccionado: {tag_name} [{tag_type}]")
        
        if tag_type == "Boolean":
            val_str = input("  Nuevo valor (true/false): ").strip().lower()
            new_value = val_str in ["true", "1", "yes", "t"]
            variant_type = ua.VariantType.Boolean
        elif tag_type == "String":
            new_value = input("  Nuevo valor (string): ").strip()
            variant_type = ua.VariantType.String
        else:
            print_error(f"Tipo {tag_type} no soportado para escritura manual")
            return
        
        node_id = f"ns={NAMESPACE};s=GlobalVars.{tag_name}"
        node = client.get_node(node_id)
        
        await node.write_value(ua.DataValue(ua.Variant(new_value, variant_type)))
        
        # Verificar
        verify = await node.read_value()
        print_ok(f"Escrito! Valor verificado: {verify}")
        
    except Exception as e:
        print_error(f"Error: {e}")

# ============================================================================
# MAIN
# ============================================================================
async def main():
    print_header("TEST DE CONEXIÓN OPC UA - FACTORYTALK OPTIX")
    print(f"  Servidor: {OPTIX_URL}")
    print(f"  Namespace objetivo: {NAMESPACE}")
    print(f"  Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("  [INICIANDO - Si se congela aquí, el servidor no responde]")
    sys.stdout.flush()
    
    client = Client(url=OPTIX_URL, timeout=10)  # 10 segundos timeout
    client.session_timeout = 10000  # 10 segundos session timeout
    
    try:
        # Test 1: Conexión
        print("  [Paso 1/7: Intentando conectar...]")
        sys.stdout.flush()
        connected = await asyncio.wait_for(test_connection(client), timeout=15.0)
        if not connected:
            print_error("No se pudo conectar. Verifica que Optix esté corriendo.")
            return
        
        # Test 2: Namespaces
        await explore_namespaces(client)
        
        # Test 3: Explorar nodos
        await explore_namespace_nodes(client)
        
        # Test 4: Buscar GlobalVars
        found_format = await find_globalvars_node(client)
        
        # Test 5: Leer tags
        await read_all_tags(client, found_format)
        
        # Test 6: Escribir heartbeat
        await test_heartbeat_write(client)
        
        # Preguntar si quiere modo interactivo
        print_section("¿Continuar con modo interactivo?")
        try:
            response = input("  Entrar a menú interactivo? (s/n): ").strip().lower()
            if response in ["s", "si", "y", "yes"]:
                await interactive_menu(client)
        except EOFError:
            pass
        
    except KeyboardInterrupt:
        print("\n\n  [Programa interrumpido por usuario]")
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_section("Cerrando conexión")
        try:
            await client.disconnect()
            print_ok("Desconectado correctamente")
        except:
            pass

if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("█  GATEWAY SIMULATOR - OPC UA TEST TOOL")
    print("█" * 70)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nPrograma terminado.")
    
    print("\n" + "=" * 70)
    print("  FIN DEL TEST")
    print("=" * 70 + "\n")
