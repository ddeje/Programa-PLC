"""
Test simple - buscar CUALQUIER variable que funcione
para confirmar que OPC UA basico esta OK
"""
import asyncio
from asyncua import Client

async def find_readable_var(node, depth=0, max_depth=3, found=None):
    """Buscar primera variable legible"""
    if found is None:
        found = {"node": None}
    if found["node"] or depth > max_depth:
        return
    
    try:
        node_class = await node.read_node_class()
        
        # Si es variable, intentar leer
        if node_class.value == 2:
            try:
                val = await node.read_value()
                name = await node.read_browse_name()
                found["node"] = node
                found["name"] = name.Name
                found["value"] = val
                return
            except:
                pass
        
        # Explorar hijos
        children = await node.get_children()
        for child in children[:10]:  # Limitar
            await find_readable_var(child, depth + 1, max_depth, found)
            if found["node"]:
                return
                
    except:
        pass

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"="*60)
    print("TEST SIMPLE DE COMUNICACION OPC UA")
    print(f"="*60)
    print(f"\nServidor: {url}")
    print("Conectando...")
    
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ CONEXION EXITOSA!\n")
        
        # Leer informacion del servidor
        print("Informacion del servidor:")
        server_node = client.get_node("i=2253")  # Server node
        
        # Estado del servidor
        server_status = client.get_node("i=2256")
        status = await server_status.read_value()
        print(f"  - Estado: {status.State}")
        print(f"  - Tiempo inicio: {status.StartTime}")
        print(f"  - Tiempo actual: {status.CurrentTime}")
        
        # Namespaces
        ns_array = await client.get_namespace_array()
        print(f"  - Namespaces: {len(ns_array)}")
        
        # Buscar una variable legible
        print("\nBuscando variable legible...")
        objects = client.nodes.objects
        found = {"node": None}
        await find_readable_var(objects, found=found)
        
        if found["node"]:
            print(f"  ✅ Variable encontrada: {found['name']}")
            print(f"     Valor: {found['value']}")
            print(f"     NodeId: {found['node']}")
        else:
            print("  ⚠️ No se encontraron variables legibles en primeros niveles")
        
        print("\n" + "="*60)
        print("RESULTADO: ✅ COMUNICACION OPC UA FUNCIONA")
        print("="*60)
        print("\n⚠️ NOTA: Los tags del PLC (EgComIn_*) dan error BadInternalError")
        print("   Esto puede significar:")
        print("   1. El PLC no esta comunicando con Optix Edge")
        print("   2. La conexion EtherNet/IP no esta establecida")
        print("   3. Verificar en Optix que la estacion este 'Online'")
        
    except Exception as e:
        print(f"❌ ERROR DE CONEXION: {e}")
        print("\nVerificar:")
        print("  - IP correcta (192.168.101.100)")
        print("  - Puerto correcto (59100)")
        print("  - Optix Edge ejecutandose")
        print("  - Firewall permitiendo conexion")
        
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
