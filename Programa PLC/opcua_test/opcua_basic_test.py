"""
================================================================================
    OPC UA Basic Communication Test
    Prueba básica de comunicación OPC UA para diagnóstico
    
    Propósito: Verificar conectividad y lectura de variables usando
               SOLO tipos de datos estándar (sin estructuras customizadas)
    
    Fecha: December 4, 2025
================================================================================
"""

import sys
import time
from datetime import datetime

# Intentar importar opcua - si no está instalado, dar instrucciones
try:
    from opcua import Client, ua
    OPCUA_AVAILABLE = True
except ImportError:
    OPCUA_AVAILABLE = False
    print("=" * 60)
    print("ERROR: La librería 'opcua' no está instalada.")
    print("Instalar con: pip install opcua")
    print("O para la versión asyncio: pip install asyncua")
    print("=" * 60)

# ============================================================================
# CONFIGURACIÓN - MODIFICAR SEGÚN TU ENTORNO
# ============================================================================

# Dirección del servidor OPC UA del PLC
# Formato típico Allen-Bradley: opc.tcp://IP:PORT
OPC_SERVER_URL = "opc.tcp://192.168.101.96:4840"  # Puerto estándar OPC UA

# Alternativa: Si usas el servidor VMEK
# OPC_SERVER_URL = "opc.tcp://192.168.101.105:55532"

# Timeout de conexión en segundos
CONNECTION_TIMEOUT = 5000  # milisegundos

# Namespace Index - CRÍTICO: Este fue uno de los problemas identificados
# Por defecto, las variables de usuario suelen estar en ns=2 o ns=3
# ns=0 es el namespace estándar de OPC UA
# ns=1 suele ser del servidor
# ns=2, ns=3... son los definidos por el usuario/dispositivo
NAMESPACE_INDEX = 2  # Ajustar según lo que vean en UaExpert

# ============================================================================
# VARIABLES DE PRUEBA - TIPOS ESTÁNDAR ÚNICAMENTE
# ============================================================================

# Definir tags de prueba con diferentes formatos de identificador
# Esto ayudará a diagnosticar el problema de formato de identificadores

TEST_TAGS = [
    # Formato 1: NodeId como string (browsable name)
    # Ejemplo para Allen-Bradley
    {
        "name": "Test Bool (DI)",
        "node_id": f"ns={NAMESPACE_INDEX};s=AEC_Sheller_ON",
        "expected_type": "Boolean"
    },
    {
        "name": "Compressed Air Status",
        "node_id": f"ns={NAMESPACE_INDEX};s=Compressed_Air",
        "expected_type": "Boolean"
    },
    # Formato 2: Path completo del tag
    {
        "name": "Material Gate Open",
        "node_id": f"ns={NAMESPACE_INDEX};s=Program:MainProgram.Material_Gate_Open_Pos",
        "expected_type": "Boolean"
    },
    # Formato 3: Acceso directo a I/O
    {
        "name": "Local Input Slot 1",
        "node_id": f"ns={NAMESPACE_INDEX};s=Local:1:I.Data.0",
        "expected_type": "Boolean"
    },
]


def print_separator(char="=", length=70):
    """Imprime una línea separadora."""
    print(char * length)


def print_header(title):
    """Imprime un encabezado formateado."""
    print_separator()
    print(f"  {title}")
    print_separator()


def test_connection(url):
    """
    Prueba 1: Verificar conexión básica al servidor OPC UA
    """
    print_header("PRUEBA 1: Conexión al Servidor OPC UA")
    print(f"URL del servidor: {url}")
    print(f"Timeout: {CONNECTION_TIMEOUT}ms")
    print()
    
    client = Client(url)
    client.connect_timeout = CONNECTION_TIMEOUT
    
    try:
        print("Intentando conectar...")
        client.connect()
        print("✓ CONEXIÓN EXITOSA")
        
        # Obtener información del servidor
        print("\n--- Información del Servidor ---")
        try:
            root = client.get_root_node()
            print(f"Root Node: {root}")
            
            # Obtener endpoints
            endpoints = client.get_endpoints()
            print(f"Endpoints disponibles: {len(endpoints)}")
            for i, ep in enumerate(endpoints):
                print(f"  [{i}] {ep.EndpointUrl}")
                print(f"      Security: {ep.SecurityMode}")
        except Exception as e:
            print(f"  (No se pudo obtener info detallada: {e})")
        
        return client, True
        
    except Exception as e:
        print(f"✗ ERROR DE CONEXIÓN: {e}")
        print("\nPosibles causas:")
        print("  - IP incorrecta o PLC no accesible en la red")
        print("  - Puerto incorrecto (probar 4840, 4843, 55532)")
        print("  - Firewall bloqueando la conexión")
        print("  - Servidor OPC UA no habilitado en el PLC")
        return None, False


def explore_namespaces(client):
    """
    Prueba 2: Explorar los Namespaces disponibles
    CRÍTICO: Identificar el namespace correcto fue un problema en la reunión
    """
    print_header("PRUEBA 2: Exploración de Namespaces")
    
    try:
        # Obtener la tabla de namespaces
        ns_array = client.get_namespace_array()
        
        print("Namespaces disponibles:")
        print("-" * 50)
        for i, ns in enumerate(ns_array):
            marker = " <-- ACTUAL" if i == NAMESPACE_INDEX else ""
            print(f"  ns={i}: {ns}{marker}")
        print("-" * 50)
        
        print(f"\nNamespace configurado para pruebas: ns={NAMESPACE_INDEX}")
        if NAMESPACE_INDEX < len(ns_array):
            print(f"URI del namespace: {ns_array[NAMESPACE_INDEX]}")
        else:
            print("⚠ ADVERTENCIA: El namespace configurado no existe!")
            
        return ns_array
        
    except Exception as e:
        print(f"✗ Error al explorar namespaces: {e}")
        return []


def browse_nodes(client, max_depth=2):
    """
    Prueba 3: Navegar la estructura de nodos
    Esto ayuda a encontrar los identificadores correctos
    """
    print_header("PRUEBA 3: Navegación de Estructura de Nodos")
    
    try:
        root = client.get_root_node()
        objects = client.get_objects_node()
        
        print(f"Root Node: {root}")
        print(f"Objects Node: {objects}")
        print("\nEstructura de nodos (primeros 2 niveles):")
        print("-" * 50)
        
        def browse_recursive(node, depth=0, max_d=2):
            if depth > max_d:
                return
            
            try:
                children = node.get_children()
                for child in children[:10]:  # Limitar a 10 hijos por nivel
                    indent = "  " * depth
                    try:
                        browse_name = child.get_browse_name()
                        node_class = child.get_node_class()
                        node_id = child.nodeid
                        
                        print(f"{indent}├─ {browse_name.Name}")
                        print(f"{indent}│  NodeId: {node_id}")
                        print(f"{indent}│  Class: {node_class}")
                        
                        browse_recursive(child, depth + 1, max_d)
                    except Exception as e:
                        print(f"{indent}├─ (Error: {e})")
                        
                if len(children) > 10:
                    indent = "  " * depth
                    print(f"{indent}└─ ... y {len(children) - 10} nodos más")
                    
            except Exception as e:
                print(f"  Error browsing: {e}")
        
        browse_recursive(objects, 0, max_depth)
        return True
        
    except Exception as e:
        print(f"✗ Error al navegar nodos: {e}")
        return False


def test_read_variables(client):
    """
    Prueba 4: Lectura de variables con diferentes formatos de NodeId
    """
    print_header("PRUEBA 4: Lectura de Variables de Prueba")
    
    results = []
    
    for tag in TEST_TAGS:
        print(f"\n--- {tag['name']} ---")
        print(f"NodeId: {tag['node_id']}")
        print(f"Tipo esperado: {tag['expected_type']}")
        
        try:
            node = client.get_node(tag['node_id'])
            value = node.get_value()
            data_type = node.get_data_type_as_variant_type()
            
            print(f"✓ LECTURA EXITOSA")
            print(f"  Valor: {value}")
            print(f"  Tipo: {data_type}")
            
            results.append({
                "tag": tag['name'],
                "status": "OK",
                "value": value,
                "type": str(data_type)
            })
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({
                "tag": tag['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    return results


def test_write_variable(client, node_id, value):
    """
    Prueba 5: Escritura de variable (opcional)
    """
    print_header("PRUEBA 5: Escritura de Variable (Opcional)")
    print(f"NodeId: {node_id}")
    print(f"Valor a escribir: {value}")
    
    try:
        node = client.get_node(node_id)
        
        # Leer valor actual
        current_value = node.get_value()
        print(f"Valor actual: {current_value}")
        
        # Escribir nuevo valor
        node.set_value(value)
        print(f"✓ Escritura enviada")
        
        # Verificar
        time.sleep(0.5)
        new_value = node.get_value()
        print(f"Valor después de escribir: {new_value}")
        
        if new_value == value:
            print("✓ ESCRITURA VERIFICADA CORRECTAMENTE")
            return True
        else:
            print("⚠ El valor no coincide (puede haber lógica en el PLC)")
            return True
            
    except Exception as e:
        print(f"✗ ERROR DE ESCRITURA: {e}")
        return False


def find_allen_bradley_tags(client):
    """
    Prueba 6: Buscar tags específicos de Allen-Bradley
    Los PLCs Rockwell tienen una estructura específica
    """
    print_header("PRUEBA 6: Búsqueda de Tags Allen-Bradley")
    
    # Patrones comunes en PLCs Allen-Bradley/Rockwell
    ab_patterns = [
        f"ns={NAMESPACE_INDEX};s=Program:MainProgram",
        f"ns={NAMESPACE_INDEX};s=Controller Tags",
        f"ns={NAMESPACE_INDEX};s=Program Tags",
        f"ns={NAMESPACE_INDEX};s=Local:1:I",
        f"ns={NAMESPACE_INDEX};s=Local:2:I", 
        f"ns={NAMESPACE_INDEX};s=Local:3:O",
    ]
    
    print("Buscando estructuras típicas de Allen-Bradley...")
    print("-" * 50)
    
    found_any = False
    for pattern in ab_patterns:
        try:
            node = client.get_node(pattern)
            browse_name = node.get_browse_name()
            print(f"✓ Encontrado: {pattern}")
            print(f"  Browse Name: {browse_name}")
            
            # Intentar listar hijos
            try:
                children = node.get_children()
                print(f"  Hijos: {len(children)}")
                for child in children[:5]:
                    child_name = child.get_browse_name()
                    print(f"    - {child_name.Name}")
                if len(children) > 5:
                    print(f"    ... y {len(children) - 5} más")
            except:
                pass
                
            found_any = True
        except Exception as e:
            print(f"✗ No encontrado: {pattern}")
    
    if not found_any:
        print("\n⚠ No se encontraron estructuras típicas de Allen-Bradley")
        print("  Posibles causas:")
        print("  - Namespace Index incorrecto")
        print("  - El servidor OPC UA tiene una estructura diferente")
        print("  - Los tags no están expuestos vía OPC UA")
    
    return found_any


def generate_report(results):
    """Genera un reporte de las pruebas realizadas."""
    print_header("REPORTE FINAL DE PRUEBAS")
    
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Servidor: {OPC_SERVER_URL}")
    print(f"Namespace Index usado: {NAMESPACE_INDEX}")
    print()
    
    success_count = sum(1 for r in results if r.get('status') == 'OK')
    total_count = len(results)
    
    print(f"Resultados de lectura de variables: {success_count}/{total_count} exitosas")
    print("-" * 50)
    
    for r in results:
        status_icon = "✓" if r.get('status') == 'OK' else "✗"
        print(f"  {status_icon} {r['tag']}: {r.get('status', 'N/A')}")
        if r.get('value') is not None:
            print(f"      Valor: {r['value']}")
        if r.get('error'):
            print(f"      Error: {r['error']}")
    
    print()
    print_separator()


def main():
    """Función principal que ejecuta todas las pruebas."""
    
    if not OPCUA_AVAILABLE:
        print("\nNo se puede continuar sin la librería OPC UA.")
        print("Ejecutar: pip install opcua")
        return
    
    print()
    print_header("INICIANDO PRUEBAS DE COMUNICACIÓN OPC UA")
    print(f"Servidor objetivo: {OPC_SERVER_URL}")
    print(f"Namespace Index configurado: {NAMESPACE_INDEX}")
    print()
    
    # Prueba 1: Conexión
    client, connected = test_connection(OPC_SERVER_URL)
    
    if not connected:
        print("\n" + "=" * 70)
        print("No se puede continuar sin conexión al servidor.")
        print("Verificar:")
        print(f"  1. La IP {OPC_SERVER_URL.split('//')[1].split(':')[0]} es accesible")
        print("  2. El puerto está correcto")
        print("  3. El servidor OPC UA está habilitado en el PLC")
        print("=" * 70)
        return
    
    try:
        # Prueba 2: Namespaces
        namespaces = explore_namespaces(client)
        
        # Prueba 3: Navegación
        browse_nodes(client)
        
        # Prueba 4: Lectura de variables
        read_results = test_read_variables(client)
        
        # Prueba 6: Búsqueda Allen-Bradley
        find_allen_bradley_tags(client)
        
        # Generar reporte
        generate_report(read_results)
        
    finally:
        # Siempre desconectar
        print("\nDesconectando del servidor...")
        client.disconnect()
        print("✓ Desconectado")


def interactive_mode():
    """
    Modo interactivo para explorar el servidor OPC UA
    """
    print_header("MODO INTERACTIVO")
    print("Este modo te permite explorar el servidor manualmente.")
    print()
    
    url = input(f"URL del servidor [{OPC_SERVER_URL}]: ").strip()
    if not url:
        url = OPC_SERVER_URL
    
    ns = input(f"Namespace Index [{NAMESPACE_INDEX}]: ").strip()
    if ns:
        try:
            ns = int(ns)
        except:
            ns = NAMESPACE_INDEX
    else:
        ns = NAMESPACE_INDEX
    
    client = Client(url)
    
    try:
        client.connect()
        print("✓ Conectado")
        
        while True:
            print("\nOpciones:")
            print("  1. Ver namespaces")
            print("  2. Navegar nodos")
            print("  3. Leer variable (ingresar NodeId)")
            print("  4. Buscar por nombre")
            print("  5. Salir")
            
            choice = input("\nSelección: ").strip()
            
            if choice == "1":
                explore_namespaces(client)
            elif choice == "2":
                browse_nodes(client, max_depth=3)
            elif choice == "3":
                node_id = input("NodeId (ej: ns=2;s=TagName): ").strip()
                if node_id:
                    try:
                        node = client.get_node(node_id)
                        print(f"Valor: {node.get_value()}")
                        print(f"Tipo: {node.get_data_type_as_variant_type()}")
                    except Exception as e:
                        print(f"Error: {e}")
            elif choice == "4":
                name = input("Nombre a buscar: ").strip()
                print(f"Buscando '{name}'...")
                # Búsqueda básica
                test_ids = [
                    f"ns={ns};s={name}",
                    f"ns={ns};s=Program:MainProgram.{name}",
                    f"ns={ns};s=Controller Tags.{name}",
                ]
                for tid in test_ids:
                    try:
                        node = client.get_node(tid)
                        val = node.get_value()
                        print(f"✓ Encontrado: {tid}")
                        print(f"  Valor: {val}")
                    except:
                        pass
            elif choice == "5":
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("Desconectado")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("   OPC UA BASIC COMMUNICATION TEST")
    print("   Para diagnóstico de problemas de comunicación")
    print("=" * 70)
    
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        interactive_mode()
    else:
        main()
        print("\nTip: Ejecutar con '-i' para modo interactivo")
        print("     python opcua_basic_test.py -i")
