"""
================================================================================
    Test de Formatos de NodeId para Allen-Bradley
    
    Este script prueba diferentes formatos de NodeId para encontrar
    el correcto para tu PLC. Esto es clave para resolver el problema
    de "identificadores no legibles" mencionado en la reunión.
================================================================================
"""

import sys

try:
    from opcua import Client
    OPCUA_AVAILABLE = True
except ImportError:
    try:
        import asyncio
        from asyncua import Client as AsyncClient
        OPCUA_AVAILABLE = True
        ASYNC_MODE = True
    except ImportError:
        OPCUA_AVAILABLE = False
        ASYNC_MODE = False

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SERVER_URL = "opc.tcp://192.168.101.96:4840"

# Tags de prueba de tu I/O List
TEST_TAG = "AEC_Sheller_ON"

# Rangos de namespace a probar
NAMESPACE_RANGE = range(0, 6)  # ns=0 hasta ns=5


def generate_nodeid_formats(tag_name, ns):
    """
    Genera todos los formatos posibles de NodeId para un tag.
    Allen-Bradley/Rockwell puede usar varios formatos.
    """
    formats = [
        # Formato 1: Tag directo
        f"ns={ns};s={tag_name}",
        
        # Formato 2: Con prefijo de Controller Tags
        f"ns={ns};s=Controller Tags.{tag_name}",
        
        # Formato 3: Con path de programa MainProgram
        f"ns={ns};s=Program:MainProgram.{tag_name}",
        
        # Formato 4: Solo programa sin prefijo
        f"ns={ns};s=MainProgram.{tag_name}",
        
        # Formato 5: Con DeviceSet (común en algunos servidores)
        f"ns={ns};s=DeviceSet.{tag_name}",
        
        # Formato 6: Path completo con Objects
        f"ns={ns};s=Objects.{tag_name}",
        
        # Formato 7: Usando punto como separador
        f"ns={ns};s=[]{tag_name}",
        
        # Formato 8: Tags globales
        f"ns={ns};s=GlobalTags.{tag_name}",
        
        # Formato 9: Formato Rockwell con corchetes (para arrays)
        f"ns={ns};s={tag_name}[0]",
        
        # Formato 10: Browse path estilo
        f"ns={ns};s=/{tag_name}",
    ]
    return formats


def test_with_opcua():
    """Versión síncrona con python-opcua."""
    from opcua import Client
    
    print("=" * 70)
    print("PRUEBA DE FORMATOS DE NODEID")
    print("=" * 70)
    print(f"Servidor: {SERVER_URL}")
    print(f"Tag de prueba: {TEST_TAG}")
    print()
    
    client = Client(SERVER_URL)
    
    try:
        client.connect()
        print("✓ Conectado al servidor\n")
        
        # Mostrar namespaces disponibles
        print("--- Namespaces Disponibles ---")
        ns_array = client.get_namespace_array()
        for i, ns in enumerate(ns_array):
            print(f"  ns={i}: {ns}")
        print()
        
        # Probar cada combinación
        print("--- Probando Formatos de NodeId ---")
        print("-" * 70)
        
        found_formats = []
        
        for ns in NAMESPACE_RANGE:
            if ns >= len(ns_array):
                break
                
            formats = generate_nodeid_formats(TEST_TAG, ns)
            
            for node_id in formats:
                try:
                    node = client.get_node(node_id)
                    value = node.get_value()
                    print(f"✓ ENCONTRADO!")
                    print(f"  NodeId: {node_id}")
                    print(f"  Valor: {value}")
                    print()
                    found_formats.append({
                        "node_id": node_id,
                        "value": value
                    })
                except Exception as e:
                    # Silencioso para no llenar la pantalla
                    pass
        
        # Resumen
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)
        
        if found_formats:
            print(f"✓ Se encontraron {len(found_formats)} formato(s) válido(s):\n")
            for f in found_formats:
                print(f"  {f['node_id']}")
                print(f"  Valor: {f['value']}\n")
                
            print("\nRECOMENDACIÓN:")
            print(f"  Usar el formato: {found_formats[0]['node_id']}")
            
            # Extraer el namespace correcto
            ns_found = found_formats[0]['node_id'].split(';')[0].split('=')[1]
            print(f"  Namespace correcto: ns={ns_found}")
        else:
            print("✗ No se encontró ningún formato válido para el tag.")
            print()
            print("Posibles causas:")
            print("  1. El tag no existe o tiene otro nombre")
            print("  2. El namespace está fuera del rango probado")
            print("  3. El servidor usa un formato diferente")
            print()
            print("Sugerencias:")
            print("  1. Usar UaExpert para navegar manualmente")
            print("  2. Ejecutar: python opcua_basic_test.py -i")
            print("  3. Verificar el nombre exacto del tag en el PLC")
        
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
    finally:
        client.disconnect()


async def test_with_asyncua():
    """Versión asíncrona con asyncua."""
    from asyncua import Client
    
    print("=" * 70)
    print("PRUEBA DE FORMATOS DE NODEID (asyncua)")
    print("=" * 70)
    print(f"Servidor: {SERVER_URL}")
    print(f"Tag de prueba: {TEST_TAG}")
    print()
    
    client = Client(url=SERVER_URL)
    
    try:
        await client.connect()
        print("✓ Conectado al servidor\n")
        
        # Mostrar namespaces disponibles
        print("--- Namespaces Disponibles ---")
        ns_array = await client.get_namespace_array()
        for i, ns in enumerate(ns_array):
            print(f"  ns={i}: {ns}")
        print()
        
        # Probar cada combinación
        print("--- Probando Formatos de NodeId ---")
        
        found_formats = []
        
        for ns in NAMESPACE_RANGE:
            if ns >= len(ns_array):
                break
                
            formats = generate_nodeid_formats(TEST_TAG, ns)
            
            for node_id in formats:
                try:
                    node = client.get_node(node_id)
                    value = await node.read_value()
                    print(f"✓ ENCONTRADO: {node_id}")
                    print(f"  Valor: {value}\n")
                    found_formats.append({
                        "node_id": node_id,
                        "value": value
                    })
                except:
                    pass
        
        # Resumen
        print("=" * 70)
        if found_formats:
            print(f"✓ Formatos válidos encontrados: {len(found_formats)}")
            print(f"  Recomendado: {found_formats[0]['node_id']}")
        else:
            print("✗ No se encontró ningún formato válido")
            print("  Usar UaExpert para explorar manualmente")
        print("=" * 70)
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()


def main():
    if not OPCUA_AVAILABLE:
        print("Instalar: pip install opcua  o  pip install asyncua")
        return
    
    # Intentar con opcua primero
    try:
        from opcua import Client
        test_with_opcua()
    except ImportError:
        import asyncio
        asyncio.run(test_with_asyncua())


if __name__ == "__main__":
    main()
