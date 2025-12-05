"""
================================================================================
    OPC UA Test - Optix Edge (Rockwell)
    Configuración correcta después de explorar el servidor
    
    DESCUBRIMIENTO:
    - Los tags están en namespace 6 (ns=6)
    - Formato: ns=6;s=Program:EdgeGateway.TagName
    - El PLC es: 5069-L310ER/A, proyecto CPS_001
================================================================================
"""

import asyncio
from asyncua import Client

# ============================================================================
# CONFIGURACIÓN CORRECTA PARA OPTIX EDGE
# ============================================================================

SERVER_URL = "opc.tcp://192.168.101.100:59100"

# ¡NAMESPACE CORRECTO ES 6, NO 2!
NAMESPACE_INDEX = 6

# Tags descubiertos en la exploración
DISCOVERED_TAGS = [
    # Variable simple de sistema
    {
        "name": "YEAR",
        "node_id": "ns=6;s=YEAR",
        "description": "Variable de año del sistema"
    },
    # Tags del programa EdgeGateway - Entradas
    {
        "name": "Heartbeat (In)",
        "node_id": "ns=6;s=Program:EdgeGateway.EdCommIn.Heartbeat",
        "description": "Heartbeat de comunicación"
    },
    {
        "name": "RecordNotFound",
        "node_id": "ns=6;s=Program:EdgeGateway.EdCommIn.RecordNotFound",
        "description": "Flag de registro no encontrado"
    },
    {
        "name": "MaterialRecord_pull",
        "node_id": "ns=6;s=Program:EdgeGateway.EdCommIn.MaterialRecord_pull",
        "description": "Registro de material (pull)"
    },
    {
        "name": "WriteToDb_Confirmation",
        "node_id": "ns=6;s=Program:EdgeGateway.EdCommIn.WriteToDb_Confirmation",
        "description": "Confirmación de escritura a DB"
    },
    {
        "name": "UUID_pull",
        "node_id": "ns=6;s=Program:EdgeGateway.EdCommIn.UUID_pull",
        "description": "UUID de pull"
    },
    # Tags del programa EdgeGateway - Salidas
    {
        "name": "BarcodeValue",
        "node_id": "ns=6;s=Program:EdgeGateway.EgComOut.BarcodeValue",
        "description": "Valor del código de barras"
    },
    {
        "name": "BarcodeReq",
        "node_id": "ns=6;s=Program:EdgeGateway.EgComOut.BarcodeReq",
        "description": "Solicitud de código de barras"
    },
    {
        "name": "MaterialRecord_push",
        "node_id": "ns=6;s=Program:EdgeGateway.EgComOut.MaterialRecord_push",
        "description": "Registro de material (push)"
    },
    {
        "name": "WriteToDb",
        "node_id": "ns=6;s=Program:EdgeGateway.EgComOut.WriteToDb",
        "description": "Comando escribir a DB"
    },
    {
        "name": "UUIDReq",
        "node_id": "ns=6;s=Program:EdgeGateway.EgComOut.UUIDReq",
        "description": "Solicitud de UUID"
    },
]


async def test_read_tags():
    """Lee todos los tags descubiertos."""
    
    print("=" * 70)
    print("PRUEBA DE LECTURA - OPTIX EDGE")
    print("=" * 70)
    print(f"Servidor: {SERVER_URL}")
    print(f"Namespace: {NAMESPACE_INDEX}")
    print()
    
    client = Client(url=SERVER_URL)
    
    try:
        await client.connect()
        print("✓ Conectado al Optix Edge\n")
        
        print("=" * 70)
        print("LECTURA DE TAGS DESCUBIERTOS")
        print("=" * 70)
        
        success_count = 0
        error_count = 0
        
        for tag in DISCOVERED_TAGS:
            print(f"\n--- {tag['name']} ---")
            print(f"NodeId: {tag['node_id']}")
            
            try:
                node = client.get_node(tag['node_id'])
                value = await node.read_value()
                data_type = await node.read_data_type_as_variant_type()
                
                print(f"✓ Valor: {value}")
                print(f"  Tipo: {data_type}")
                success_count += 1
                
            except Exception as e:
                print(f"✗ Error: {e}")
                error_count += 1
        
        # Resumen
        print("\n" + "=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"Lecturas exitosas: {success_count}/{len(DISCOVERED_TAGS)}")
        print(f"Errores: {error_count}/{len(DISCOVERED_TAGS)}")
        
        if success_count > 0:
            print("\n✓ ¡LA COMUNICACIÓN OPC UA FUNCIONA!")
            print("\nINFORMACIÓN PARA JACOBO:")
            print("-" * 50)
            print(f"  Namespace correcto: ns={NAMESPACE_INDEX}")
            print(f"  URI del namespace: urn:RockwellAutomation:5069-L310ER%2FA")
            print(f"  Formato de NodeId: ns={NAMESPACE_INDEX};s=Program:EdgeGateway.Tag")
        
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        
    finally:
        await client.disconnect()
        print("\n✓ Desconectado")


async def test_write_tag():
    """Prueba de escritura (opcional)."""
    
    print("\n" + "=" * 70)
    print("PRUEBA DE ESCRITURA (opcional)")
    print("=" * 70)
    
    # Tag seguro para probar escritura
    # Usamos BarcodeReq que es un comando
    test_node_id = "ns=6;s=Program:EdgeGateway.EgComOut.BarcodeReq"
    
    client = Client(url=SERVER_URL)
    
    try:
        await client.connect()
        print("✓ Conectado")
        
        node = client.get_node(test_node_id)
        
        # Leer valor actual
        current = await node.read_value()
        print(f"Valor actual de BarcodeReq: {current}")
        
        # Intentar escribir
        # COMENTADO por seguridad - descomentar para probar
        # await node.write_value(True)
        # print("✓ Escritura enviada")
        
        print("\n(Escritura comentada por seguridad)")
        print("Descomentar línea en el código para probar")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await client.disconnect()


async def main():
    await test_read_tags()
    # await test_write_tag()  # Descomentar para probar escritura


if __name__ == "__main__":
    asyncio.run(main())
