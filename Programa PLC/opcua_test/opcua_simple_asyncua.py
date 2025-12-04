"""
================================================================================
    OPC UA Simple Test - Versión Asyncua (moderna)
    Prueba mínima de comunicación OPC UA
    
    Esta versión usa asyncua que es más moderna y mejor mantenida
================================================================================
"""

import asyncio
import sys

# Intentar importar asyncua
try:
    from asyncua import Client
    ASYNCUA_AVAILABLE = True
except ImportError:
    ASYNCUA_AVAILABLE = False


# ============================================================================
# CONFIGURACIÓN - MODIFICAR ESTOS VALORES
# ============================================================================

# Servidor OPC UA del PLC Allen-Bradley
SERVER_URL = "opc.tcp://192.168.101.96:4840"

# Namespace Index (el problema principal identificado en la reunión)
# Probar con 2, 3, 4... hasta encontrar el correcto
NAMESPACE_INDEX = 2

# Tags de prueba SIMPLES (solo tipos estándar, sin estructuras)
SIMPLE_TAGS = [
    "AEC_Sheller_ON",           # Boolean
    "Compressed_Air",           # Boolean  
    "Material_Gate_Open_Pos",   # Boolean
]


async def simple_test():
    """Prueba simple de conexión y lectura."""
    
    print("=" * 60)
    print("PRUEBA SIMPLE OPC UA")
    print("=" * 60)
    print(f"Servidor: {SERVER_URL}")
    print(f"Namespace: {NAMESPACE_INDEX}")
    print()
    
    client = Client(url=SERVER_URL)
    
    try:
        # Conectar
        print("Conectando...")
        await client.connect()
        print("✓ Conectado exitosamente!")
        print()
        
        # Mostrar namespaces
        print("--- Namespaces Disponibles ---")
        ns_array = await client.get_namespace_array()
        for i, ns in enumerate(ns_array):
            marker = " <-- ACTUAL" if i == NAMESPACE_INDEX else ""
            print(f"  ns={i}: {ns}{marker}")
        print()
        
        # Probar lectura de tags
        print("--- Prueba de Lectura de Tags ---")
        for tag_name in SIMPLE_TAGS:
            # Construir NodeId
            node_id = f"ns={NAMESPACE_INDEX};s={tag_name}"
            print(f"\nTag: {tag_name}")
            print(f"NodeId: {node_id}")
            
            try:
                node = client.get_node(node_id)
                value = await node.read_value()
                print(f"✓ Valor: {value}")
            except Exception as e:
                print(f"✗ Error: {e}")
                
                # Intentar formatos alternativos
                alt_formats = [
                    f"ns={NAMESPACE_INDEX};s=Program:MainProgram.{tag_name}",
                    f"ns={NAMESPACE_INDEX};s=Controller Tags.{tag_name}",
                ]
                print("  Probando formatos alternativos...")
                for alt in alt_formats:
                    try:
                        node = client.get_node(alt)
                        value = await node.read_value()
                        print(f"  ✓ Encontrado con: {alt}")
                        print(f"    Valor: {value}")
                        break
                    except:
                        pass
        
        print()
        print("=" * 60)
        print("PRUEBA COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR DE CONEXIÓN: {e}")
        print("\nVerificar:")
        print("  1. IP del PLC es correcta")
        print("  2. Puerto OPC UA (probar 4840, 4843)")
        print("  3. OPC UA está habilitado en el módulo")
        
    finally:
        await client.disconnect()


async def explore_server():
    """Explorar la estructura del servidor."""
    
    print("=" * 60)
    print("EXPLORACIÓN DEL SERVIDOR OPC UA")
    print("=" * 60)
    
    client = Client(url=SERVER_URL)
    
    try:
        await client.connect()
        print("✓ Conectado\n")
        
        # Obtener nodo Objects
        objects = client.nodes.objects
        print("Explorando Objects node...")
        print("-" * 40)
        
        async def browse(node, depth=0, max_depth=3):
            if depth > max_depth:
                return
                
            children = await node.get_children()
            for child in children[:15]:  # Limitar
                try:
                    name = await child.read_browse_name()
                    node_id = child.nodeid
                    indent = "  " * depth
                    print(f"{indent}├─ {name.Name}")
                    print(f"{indent}│  {node_id}")
                    await browse(child, depth + 1, max_depth)
                except Exception as e:
                    pass
        
        await browse(objects)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


def main():
    if not ASYNCUA_AVAILABLE:
        print("=" * 60)
        print("La librería 'asyncua' no está instalada.")
        print()
        print("Instalar con:")
        print("  pip install asyncua")
        print("=" * 60)
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "explore":
        asyncio.run(explore_server())
    else:
        asyncio.run(simple_test())


if __name__ == "__main__":
    main()
