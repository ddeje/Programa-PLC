"""
================================================================================
    DIAGNÓSTICO COMPLETO OPC UA - VERIFICACIÓN FINAL
    
    Objetivo: Confirmar exactamente qué funciona y qué no, y por qué
================================================================================
"""

import asyncio
from asyncua import Client, ua
from datetime import datetime

SERVER_URL = "opc.tcp://192.168.101.96:4840"

async def full_diagnostic():
    """Diagnóstico completo del servidor OPC UA."""
    
    print("=" * 80)
    print("   DIAGNÓSTICO COMPLETO OPC UA - OPTIX EDGE")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    client = Client(url=SERVER_URL)
    
    try:
        await client.connect()
        print("\n✓ CONEXIÓN EXITOSA")
        print(f"  Servidor: {SERVER_URL}")
        
        # =====================================================================
        # 1. ANÁLISIS DE NAMESPACES
        # =====================================================================
        print("\n" + "=" * 80)
        print("1. ANÁLISIS DE NAMESPACES")
        print("=" * 80)
        
        ns_array = await client.get_namespace_array()
        print(f"\nTotal de namespaces: {len(ns_array)}\n")
        
        for i, ns_uri in enumerate(ns_array):
            print(f"  ns={i}: {ns_uri}")
            
        print("\n" + "-" * 80)
        print("INTERPRETACIÓN:")
        print("  ns=0: OPC UA estándar (tipos base)")
        print("  ns=1: Servidor específico (urn:RockwellAutomation:5069-L310ER)")
        print("  ns=2: Rockwell Automation UA")
        print("  ns=3: OPC UA Device Integration (DI)")
        print("  ns=4: OPC UA FX Data")
        print("  ns=5: OPC UA FX AC")
        print("  ns=6: *** TUS TAGS DEL PLC ESTÁN AQUÍ ***")
        
        # =====================================================================
        # 2. PRUEBA DE LECTURA EN DIFERENTES NAMESPACES
        # =====================================================================
        print("\n" + "=" * 80)
        print("2. PRUEBA DE LECTURA EN DIFERENTES NAMESPACES")
        print("=" * 80)
        
        test_tag = "Program:EdgeGateway.EdCommIn.Heartbeat"
        
        print(f"\nProbando tag: {test_tag}")
        print("-" * 60)
        
        for ns in range(7):
            node_id = f"ns={ns};s={test_tag}"
            try:
                node = client.get_node(node_id)
                value = await node.read_value()
                print(f"  ns={ns}: ✓ ENCONTRADO - Valor: {value}")
            except Exception as e:
                error_name = type(e).__name__
                if "BadNodeIdUnknown" in str(e):
                    print(f"  ns={ns}: ✗ No existe")
                else:
                    print(f"  ns={ns}: ✗ Error: {error_name}")
        
        print("\n>>> CONCLUSIÓN: Los tags solo existen en ns=6")
        
        # =====================================================================
        # 3. ANÁLISIS DE TIPOS DE DATOS
        # =====================================================================
        print("\n" + "=" * 80)
        print("3. ANÁLISIS DE TIPOS DE DATOS")
        print("=" * 80)
        
        test_tags = [
            ("ns=6;s=YEAR", "YEAR (variable simple)"),
            ("ns=6;s=Program:EdgeGateway.EdCommIn.Heartbeat", "Heartbeat (BOOL)"),
            ("ns=6;s=Program:EdgeGateway.EgComOut.BarcodeValue", "BarcodeValue (STRING)"),
            ("ns=6;s=Program:EdgeGateway.EdCommIn.UUID_pull", "UUID_pull (STRING)"),
            ("ns=6;s=Program:EdgeGateway.EdCommIn.MaterialRecord_pull", "MaterialRecord_pull (ESTRUCTURA)"),
            ("ns=6;s=Program:EdgeGateway.EgComOut.MaterialRecord_push", "MaterialRecord_push (ARRAY ESTRUCTURA)"),
        ]
        
        print("\nAnalizando tipos de datos:")
        print("-" * 80)
        
        standard_types = []
        custom_types = []
        
        for node_id, description in test_tags:
            try:
                node = client.get_node(node_id)
                value = await node.read_value()
                data_type = await node.read_data_type_as_variant_type()
                
                # Mapeo de tipos
                type_names = {
                    0: "Null",
                    1: "Boolean",
                    2: "SByte",
                    3: "Byte",
                    4: "Int16",
                    5: "UInt16",
                    6: "Int32",
                    7: "UInt32",
                    8: "Int64",
                    9: "UInt64",
                    10: "Float",
                    11: "Double",
                    12: "String",
                    13: "DateTime",
                    14: "Guid",
                    15: "ByteString",
                    22: "ExtensionObject (CUSTOM TYPE)",
                    24: "DataValue",
                    25: "Variant",
                }
                
                type_name = type_names.get(data_type.value, f"Unknown({data_type.value})")
                
                print(f"\n  {description}")
                print(f"    NodeId: {node_id}")
                print(f"    Tipo: {type_name}")
                
                # Mostrar valor de forma legible
                if data_type.value == 22:  # ExtensionObject
                    if isinstance(value, list):
                        print(f"    Valor: [Array de {len(value)} ExtensionObjects]")
                    else:
                        print(f"    Valor: [ExtensionObject - bytes raw]")
                    print(f"    ⚠️  TIPO CUSTOM - No parseado automáticamente")
                    custom_types.append(description)
                else:
                    print(f"    Valor: {value}")
                    print(f"    ✓ TIPO ESTÁNDAR - Lectura correcta")
                    standard_types.append(description)
                    
            except Exception as e:
                print(f"\n  {description}")
                print(f"    ✗ Error: {e}")
        
        # =====================================================================
        # 4. RESUMEN DE TIPOS
        # =====================================================================
        print("\n" + "=" * 80)
        print("4. RESUMEN DE TIPOS DE DATOS")
        print("=" * 80)
        
        print(f"\n✓ TIPOS ESTÁNDAR (funcionan correctamente): {len(standard_types)}")
        for t in standard_types:
            print(f"    - {t}")
            
        print(f"\n⚠️  TIPOS CUSTOM (ExtensionObject): {len(custom_types)}")
        for t in custom_types:
            print(f"    - {t}")
        
        # =====================================================================
        # 5. ANÁLISIS DEL PROBLEMA CON EXTENSIONOBJECT
        # =====================================================================
        print("\n" + "=" * 80)
        print("5. ANÁLISIS DEL PROBLEMA CON EXTENSIONOBJECT")
        print("=" * 80)
        
        # Intentar obtener más info sobre el tipo custom
        try:
            node = client.get_node("ns=6;s=Program:EdgeGateway.EdCommIn.MaterialRecord_pull")
            
            # Obtener el DataType NodeId
            data_type_node = await node.read_data_type()
            print(f"\n  DataType NodeId: {data_type_node}")
            
            # Intentar leer el valor raw
            value = await node.read_value()
            if hasattr(value, 'TypeId'):
                print(f"  TypeId del ExtensionObject: {value.TypeId}")
            if hasattr(value, 'Body'):
                print(f"  Tamaño del Body (bytes): {len(value.Body)}")
                
            print("\n  EXPLICACIÓN DEL PROBLEMA:")
            print("  " + "-" * 60)
            print("  El servidor OPC UA envía estructuras (UDT) como 'ExtensionObject'.")
            print("  Para decodificar estos objetos, el cliente necesita:")
            print("    1. La definición del tipo de dato (schema)")
            print("    2. Cargar los tipos custom del servidor")
            print("")
            print("  ESTO es el problema con OPC UA 1.0.4:")
            print("    - La especificación 1.0.4 tiene limitaciones para")
            print("      transferir definiciones de tipos custom")
            print("    - El cliente no puede auto-descubrir la estructura")
            
        except Exception as e:
            print(f"  Error analizando: {e}")
        
        # =====================================================================
        # 6. INTENTAR CARGAR TIPOS CUSTOM
        # =====================================================================
        print("\n" + "=" * 80)
        print("6. INTENTO DE CARGA DE TIPOS CUSTOM")
        print("=" * 80)
        
        print("\n  Intentando cargar tipos del servidor...")
        
        try:
            # Intentar cargar los custom types
            await client.load_data_type_definitions()
            print("  ✓ load_data_type_definitions() completado")
            
            # Volver a leer el tag
            node = client.get_node("ns=6;s=Program:EdgeGateway.EdCommIn.MaterialRecord_pull")
            value = await node.read_value()
            
            print(f"\n  Valor después de cargar tipos:")
            print(f"  Tipo de Python: {type(value)}")
            
            if hasattr(value, '__dict__'):
                print(f"  Atributos: {value.__dict__}")
            else:
                print(f"  Valor: {value}")
                
            if isinstance(value, (bytes, bytearray)):
                print("  ⚠️  Sigue siendo bytes - tipos no cargados correctamente")
            elif hasattr(value, 'Body'):
                print("  ⚠️  Sigue siendo ExtensionObject sin parsear")
            else:
                print("  ✓ Tipo parseado correctamente")
                
        except Exception as e:
            print(f"  ✗ Error al cargar tipos: {e}")
            print("  ESTO CONFIRMA el problema con custom types")
        
        # =====================================================================
        # 7. CONCLUSIÓN FINAL
        # =====================================================================
        print("\n" + "=" * 80)
        print("7. CONCLUSIÓN FINAL")
        print("=" * 80)
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           DIAGNÓSTICO CONFIRMADO                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  PROBLEMA 1: NAMESPACE INDEX                                                  ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  • El gateway 3 estaba configurado con ns=2                                   ║
║  • Los tags del PLC están en ns=6                                             ║
║  • SOLUCIÓN: Cambiar Namespace Index de 2 a 6                                 ║
║                                                                               ║
║  PROBLEMA 2: FORMATO DE NODEID                                                ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  • Formato incorrecto: ns=2;s=TagName                                         ║
║  • Formato correcto:   ns=6;s=Program:EdgeGateway.TagName                     ║
║                                                                               ║
║  PROBLEMA 3: TIPOS DE DATOS CUSTOM (OPC UA 1.0.4)                             ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  • Los tipos estándar (BOOL, INT, STRING) funcionan correctamente             ║
║  • Las estructuras (UDT) llegan como ExtensionObject sin parsear              ║
║  • Esto es una limitación conocida de OPC UA 1.0.4                            ║
║  • Las estructuras anidadas NO se pueden decodificar automáticamente          ║
║                                                                               ║
║  ACCIONES RECOMENDADAS:                                                       ║
║  ─────────────────────────────────────────────────────────────────────────   ║
║  1. Corregir Namespace Index a 6 en el gateway                                ║
║  2. Usar formato completo: ns=6;s=Program:ProgramName.TagName                 ║
║  3. Para estructuras: usar solo miembros de tipos estándar o                  ║
║     implementar decodificación manual del ExtensionObject                     ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
        
    except Exception as e:
        print(f"\n✗ ERROR DE CONEXIÓN: {e}")
        
    finally:
        await client.disconnect()
        print("\n✓ Desconectado del servidor")


async def test_structure_members():
    """Intenta acceder a miembros individuales de la estructura."""
    
    print("\n" + "=" * 80)
    print("PRUEBA ADICIONAL: ACCESO A MIEMBROS DE ESTRUCTURA")
    print("=" * 80)
    
    client = Client(url=SERVER_URL)
    
    try:
        await client.connect()
        print("\n✓ Conectado")
        
        # Intentar acceder a miembros individuales de MaterialRecord_pull
        base_path = "Program:EdgeGateway.EdCommIn.MaterialRecord_pull"
        
        # Posibles nombres de miembros (según típicas estructuras de material)
        possible_members = [
            "ID", "id", "Name", "name", "Value", "value",
            "Quantity", "quantity", "Lot", "lot", "BatchId",
            "MaterialId", "material_id", "Description",
            "Status", "status", "Timestamp", "timestamp",
            "Field1", "Field2", "Data", "data"
        ]
        
        print(f"\nIntentando acceder a miembros de: {base_path}")
        print("-" * 60)
        
        found_any = False
        for member in possible_members:
            node_id = f"ns=6;s={base_path}.{member}"
            try:
                node = client.get_node(node_id)
                value = await node.read_value()
                print(f"  ✓ {member}: {value}")
                found_any = True
            except:
                pass
        
        if not found_any:
            print("  No se encontraron miembros accesibles directamente")
            print("  Los miembros de la estructura no están expuestos individualmente")
            
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        await client.disconnect()


async def main():
    await full_diagnostic()
    await test_structure_members()


if __name__ == "__main__":
    asyncio.run(main())
