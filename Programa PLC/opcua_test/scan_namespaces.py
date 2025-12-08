import asyncio
import logging
from asyncua import Client

# Configuración
OPTIX_URL = "opc.tcp://192.168.101.100:55533"  # Ajustar IP/Puerto si es necesario

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('NamespaceScanner')

async def scan_namespaces():
    print(f"🔌 Conectando a {OPTIX_URL}...")
    try:
        async with Client(url=OPTIX_URL) as client:
            print("✅ Conexión establecida!")
            
            # Leer el array de namespaces
            idx = await client.get_namespace_array()
            
            print("\n📊 TABLA DE NAMESPACES ACTUAL:")
            print("-" * 60)
            print(f"{'INDEX (ns)':<10} | {'URI'}")
            print("-" * 60)
            
            for i, uri in enumerate(idx):
                print(f"{i:<10} | {uri}")
                
            print("-" * 60)
            
            # Buscar dónde está nuestro proyecto (generalmente urn:...)
            print("\n🕵️  ANÁLISIS:")
            if len(idx) > 9:
                print(f"⚠️  Tu proyecto está actualmente por el índice 9 o superior.")
                print(f"👉  Objetivo: Eliminar {(len(idx)-1) - 4} namespaces anteriores para llegar a ns=4.")
            else:
                print(f"ℹ️  Tienes {len(idx)} namespaces en total.")

    except Exception as e:
        print(f"🔥 Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(scan_namespaces())
