"""Monitor Heartbeat en tiempo real"""
import asyncio
from asyncua import Client
from datetime import datetime

async def main():
    c = Client('opc.tcp://192.168.101.100:59100', timeout=10)
    await c.connect()
    print("Conectado! Monitoreando Heartbeat... (Ctrl+C para salir)\n")
    
    hb = c.get_node('ns=9;g=32dd019a-bfe0-a2ee-8825-85d7ac63864c')
    
    last_val = None
    try:
        while True:
            val = await hb.read_value()
            now = datetime.now().strftime("%H:%M:%S")
            
            if val != last_val:
                print(f"[{now}] Heartbeat = {val} {'🟢' if val else '⚫'}")
                last_val = val
            
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDetenido")
    finally:
        await c.disconnect()

asyncio.run(main())
