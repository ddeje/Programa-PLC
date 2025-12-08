import asyncio
import logging
from asyncua import Client

# Configuración
OPTIX_URL = "opc.tcp://192.168.101.100:55533"  # Ajustar IP/Puerto si es necesario
NAMESPACE_INDEX = 9  # CPS001
REQUIRED_NODES = [
    f"ns={NAMESPACE_INDEX};s=EgComIn_Heartbeat",
    f"ns={NAMESPACE_INDEX};s=EgComIn_RecordNotFound",
    # Agregar más si es necesario
]

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('Verification')

async def verify_optix():
    print(f"🔌 Conectando a {OPTIX_URL}...")
    try:
        async with Client(url=OPTIX_URL) as client:
            print("✅ Conexión establecida!")
            
            # 1. Verificar Namespace
            idx = await client.get_namespace_index("CPS001")  # Namespace del proyecto
            print(f"ℹ️  Info: El namespace URI buscado está en índice: {idx}")
            
            # 2. Verificar Nodos Críticos
            print("\n🔍 Verificando Tags requeridos...")
            all_good = True
            
            for nodeid in REQUIRED_NODES:
                try:
                    node = client.get_node(nodeid)
                    val = await node.read_value()
                    print(f"✅ ENCONTRADO: {nodeid} | Valor: {val}")
                except Exception as e:
                    print(f"❌ FALLO: {nodeid} | Error: {e}")
                    all_good = False
            
            print("-" * 30)
            if all_good:
                print("🚀 ¡ÉXITO! Todos los tags críticos se leyeron correctamente.")
                print("El Gateway Jetson debería funcionar ahora.")
            else:
                print("⚠️  ATENCIÓN: Algunos tags no se encontraron.")
                print("Revise que el Namespace sea 4 y el NodeId sea String exacto.")
                
    except Exception as e:
        print(f"🔥 Error fatal de conexión: {e}")
        print("Asegúrese de que el servidor Optix esté corriendo y la IP sea correcta.")

if __name__ == "__main__":
    asyncio.run(verify_optix())
