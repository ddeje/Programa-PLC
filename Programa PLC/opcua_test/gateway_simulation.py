"""
Simulación del Jetson Edge Gateway
Conecta a Optix y simula el ciclo de comunicación típico del Gateway
"""
import asyncio
import logging
from asyncua import Client

logging.disable(logging.WARNING)

# Configuración
OPTIX_URL = "opc.tcp://192.168.101.100:59100/"

# Tags conocidos con formato GUID de Optix (ns=9)
TAGS = {
    "EgComIn_Heartbeat": "ns=9;g=32dd019a-bfe0-a2ee-8825-85d7ac63864c",
    # Agregar más tags GUID aquí cuando los descubras
}

async def main():
    print("="*60)
    print("  SIMULACIÓN JETSON EDGE GATEWAY")
    print("="*60)
    print(f"\nConectando a Optix: {OPTIX_URL}")
    
    async with Client(url=OPTIX_URL, timeout=10) as client:
        await client.load_data_type_definitions()
        print("✅ CONECTADO a Optix\n")
        
        # Simular ciclo del Gateway
        cycle = 0
        while True:
            cycle += 1
            print(f"--- Ciclo {cycle} ---")
            
            try:
                # 1. Leer Heartbeat del PLC
                hb_node = client.get_node(TAGS["EgComIn_Heartbeat"])
                hb_value = await hb_node.read_value()
                print(f"  📖 Heartbeat PLC = {hb_value}")
                
                # 2. Escribir respuesta (toggle heartbeat de vuelta)
                new_value = not hb_value if isinstance(hb_value, bool) else True
                await hb_node.write_value(new_value)
                print(f"  ✍️  Escribí Heartbeat = {new_value}")
                
                # 3. Verificar que se escribió
                verify = await hb_node.read_value()
                print(f"  ✅ Verificado = {verify}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            print()
            await asyncio.sleep(2)  # Esperar 2 segundos entre ciclos

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Simulación detenida por usuario")
