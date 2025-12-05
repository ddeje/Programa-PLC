"""
================================================================================
    CLIENTE OPC UA - GATEWAY COMMUNICATION
    
    Este programa se conecta al Gateway (real o simulador) y permite:
    - Leer todos los tags de comunicación
    - Escribir valores a los tags
    - Simular flujos de trabajo típicos
    
    Ejecutar con: python gateway_client.py
================================================================================
"""

import asyncio
import logging
from datetime import datetime
from asyncua import Client

# Configurar logging (silenciar asyncua para output más limpio)
logging.getLogger('asyncua').setLevel(logging.WARNING)
logger = logging.getLogger("GatewayClient")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Para el simulador local:
# SERVER_URL = "opc.tcp://localhost:4840"

# Para el Optix Edge de Rockwell (FTOptixApplication):
SERVER_URL = "opc.tcp://192.168.101.100:59100"

NAMESPACE_INDEX = 2  # Para el simulador

# ============================================================================
# DEFINICIÓN DE TAGS
# ============================================================================

TAGS = {
    # Tags de entrada (Gateway -> PLC)
    "Heartbeat": f"ns={NAMESPACE_INDEX};s=EgComIn_Heartbeat",
    "RecordNotFound": f"ns={NAMESPACE_INDEX};s=EgComIn_RecordNotFound",
    "WriteToDb_Confirmation": f"ns={NAMESPACE_INDEX};s=EgComIn_WriteToDb_Confirmation",
    "UUID_pull": f"ns={NAMESPACE_INDEX};s=EgComIn_UUID_pull",
    
    # Tags de salida (PLC -> Gateway)
    "BarcodeReq": f"ns={NAMESPACE_INDEX};s=EgComOut_BarcodeReq",
    "BarcodeValue": f"ns={NAMESPACE_INDEX};s=EgComOut_BarcodeValue",
    "UUIDReq": f"ns={NAMESPACE_INDEX};s=EgComOut_UUIDReq",
    "WriteToDb": f"ns={NAMESPACE_INDEX};s=EgComOut_WriteToDb",
    
    # Tags de simulación
    "SimulationCounter": f"ns={NAMESPACE_INDEX};s=SimulationCounter",
    "LastUpdate": f"ns={NAMESPACE_INDEX};s=LastUpdate",
}


class GatewayClient:
    """Cliente para comunicarse con el Gateway OPC UA."""
    
    def __init__(self, url=SERVER_URL):
        self.url = url
        self.client = None
        self.connected = False
        
    async def connect(self):
        """Conecta al servidor OPC UA."""
        
        self.client = Client(url=self.url)
        
        try:
            await self.client.connect()
            self.connected = True
            
            # Cargar definiciones de tipos (importante para estructuras)
            await self.client.load_data_type_definitions()
            
            logger.info(f"✅ Conectado a {self.url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
            
    async def disconnect(self):
        """Desconecta del servidor."""
        
        if self.client and self.connected:
            await self.client.disconnect()
            self.connected = False
            logger.info("🔌 Desconectado")
            
    async def read_tag(self, tag_name: str):
        """Lee un tag por su nombre."""
        
        if tag_name not in TAGS:
            logger.error(f"Tag desconocido: {tag_name}")
            return None
            
        try:
            node = self.client.get_node(TAGS[tag_name])
            value = await node.read_value()
            return value
            
        except Exception as e:
            logger.error(f"Error leyendo {tag_name}: {e}")
            return None
            
    async def write_tag(self, tag_name: str, value):
        """Escribe un valor a un tag."""
        
        if tag_name not in TAGS:
            logger.error(f"Tag desconocido: {tag_name}")
            return False
            
        try:
            node = self.client.get_node(TAGS[tag_name])
            await node.write_value(value)
            logger.info(f"✏️  {tag_name} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error escribiendo {tag_name}: {e}")
            return False
            
    async def read_all_tags(self):
        """Lee todos los tags y muestra sus valores."""
        
        print("\n" + "=" * 60)
        print("📊 ESTADO DE TODOS LOS TAGS")
        print("=" * 60)
        
        for name, node_id in TAGS.items():
            try:
                node = self.client.get_node(node_id)
                value = await node.read_value()
                data_type = await node.read_data_type_as_variant_type()
                print(f"  {name:30} = {str(value):20} [{data_type}]")
                
            except Exception as e:
                print(f"  {name:30} = ERROR: {e}")
                
        print("=" * 60 + "\n")


# ============================================================================
# FLUJOS DE TRABAJO TÍPICOS
# ============================================================================

async def workflow_barcode_lookup(client: GatewayClient, barcode: str):
    """
    Flujo de trabajo: Buscar información por código de barras.
    
    1. Escribir BarcodeValue con el código
    2. Activar BarcodeReq
    3. Esperar respuesta (RecordNotFound o UUID_pull)
    """
    
    print("\n" + "-" * 50)
    print(f"🔍 WORKFLOW: Búsqueda de Barcode '{barcode}'")
    print("-" * 50)
    
    # Paso 1: Escribir el barcode
    await client.write_tag("BarcodeValue", barcode)
    
    # Paso 2: Activar request
    await client.write_tag("BarcodeReq", True)
    
    # Paso 3: Esperar respuesta (timeout 5 segundos)
    print("⏳ Esperando respuesta...")
    
    for i in range(50):  # 5 segundos
        await asyncio.sleep(0.1)
        
        # Verificar si hay respuesta
        record_not_found = await client.read_tag("RecordNotFound")
        uuid_data = await client.read_tag("UUID_pull")
        
        if record_not_found:
            print("❌ Registro NO encontrado")
            break
            
        if uuid_data and uuid_data != '{"uuid": "", "timestamp": "", "data": {}}':
            print(f"✅ Registro encontrado: {uuid_data}")
            break
    else:
        print("⚠️  Timeout esperando respuesta")
        
    # Reset request
    await client.write_tag("BarcodeReq", False)
    
    print("-" * 50 + "\n")


async def workflow_request_uuid(client: GatewayClient):
    """
    Flujo de trabajo: Solicitar un nuevo UUID.
    
    1. Activar UUIDReq
    2. Esperar UUID_pull con datos
    """
    
    print("\n" + "-" * 50)
    print("🔑 WORKFLOW: Solicitar UUID")
    print("-" * 50)
    
    # Activar request
    await client.write_tag("UUIDReq", True)
    
    # Esperar respuesta
    print("⏳ Esperando UUID...")
    
    for i in range(30):  # 3 segundos
        await asyncio.sleep(0.1)
        
        uuid_data = await client.read_tag("UUID_pull")
        
        if uuid_data and '"uuid": ""' not in uuid_data:
            print(f"✅ UUID recibido: {uuid_data}")
            break
    else:
        print("⚠️  Timeout esperando UUID")
        
    # Reset request
    await client.write_tag("UUIDReq", False)
    
    print("-" * 50 + "\n")


async def workflow_write_to_db(client: GatewayClient):
    """
    Flujo de trabajo: Escribir a base de datos.
    
    1. Activar WriteToDb
    2. Esperar WriteToDb_Confirmation
    """
    
    print("\n" + "-" * 50)
    print("💾 WORKFLOW: Escribir a Base de Datos")
    print("-" * 50)
    
    # Activar write
    await client.write_tag("WriteToDb", True)
    
    # Esperar confirmación
    print("⏳ Esperando confirmación...")
    
    for i in range(30):  # 3 segundos
        await asyncio.sleep(0.1)
        
        confirmation = await client.read_tag("WriteToDb_Confirmation")
        
        if confirmation:
            print("✅ Escritura confirmada!")
            break
    else:
        print("⚠️  Timeout esperando confirmación")
        
    # Reset
    await client.write_tag("WriteToDb", False)
    
    print("-" * 50 + "\n")


async def monitor_heartbeat(client: GatewayClient, duration: int = 10):
    """Monitorea el heartbeat por un período de tiempo."""
    
    print("\n" + "-" * 50)
    print(f"💓 Monitoreando Heartbeat por {duration} segundos...")
    print("-" * 50)
    
    last_value = None
    toggles = 0
    
    for i in range(duration * 10):
        current = await client.read_tag("Heartbeat")
        counter = await client.read_tag("SimulationCounter")
        
        if current != last_value:
            toggles += 1
            status = "🟢" if current else "⚫"
            print(f"  {status} Heartbeat: {current}, Counter: {counter}")
            last_value = current
            
        await asyncio.sleep(0.1)
        
    print(f"\n📈 Total de toggles detectados: {toggles}")
    print("-" * 50 + "\n")


# ============================================================================
# MENÚ INTERACTIVO
# ============================================================================

async def interactive_menu(client: GatewayClient):
    """Menú interactivo para probar la comunicación."""
    
    while True:
        print("\n" + "=" * 60)
        print("📋 MENÚ DE OPCIONES")
        print("=" * 60)
        print("1. Leer todos los tags")
        print("2. Monitorear heartbeat (10 seg)")
        print("3. Workflow: Búsqueda de Barcode")
        print("4. Workflow: Solicitar UUID")
        print("5. Workflow: Escribir a DB")
        print("6. Escribir tag manualmente")
        print("7. Leer tag específico")
        print("0. Salir")
        print("-" * 60)
        
        try:
            option = input("Selecciona una opción: ").strip()
        except EOFError:
            break
            
        if option == "0":
            break
            
        elif option == "1":
            await client.read_all_tags()
            
        elif option == "2":
            await monitor_heartbeat(client)
            
        elif option == "3":
            barcode = input("Ingresa el código de barras: ").strip()
            if barcode:
                await workflow_barcode_lookup(client, barcode)
                
        elif option == "4":
            await workflow_request_uuid(client)
            
        elif option == "5":
            await workflow_write_to_db(client)
            
        elif option == "6":
            print("Tags disponibles:", list(TAGS.keys()))
            tag_name = input("Nombre del tag: ").strip()
            value = input("Valor (true/false para boolean, texto para string): ").strip()
            
            # Convertir valor
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
                
            await client.write_tag(tag_name, value)
            
        elif option == "7":
            print("Tags disponibles:", list(TAGS.keys()))
            tag_name = input("Nombre del tag: ").strip()
            value = await client.read_tag(tag_name)
            print(f"\n  {tag_name} = {value}\n")
            
        else:
            print("Opción no válida")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("\n" + "=" * 70)
    print("🔌 CLIENTE OPC UA - GATEWAY COMMUNICATION")
    print("=" * 70)
    print(f"\n📡 Conectando a: {SERVER_URL}")
    
    client = GatewayClient(SERVER_URL)
    
    if await client.connect():
        # Mostrar estado inicial
        await client.read_all_tags()
        
        # Modo de operación
        print("\n¿Qué modo deseas usar?")
        print("1. Menú interactivo")
        print("2. Demo automático")
        print("3. Solo monitorear")
        
        try:
            mode = input("Selecciona (1/2/3): ").strip()
        except EOFError:
            mode = "2"  # Default a demo
            
        if mode == "1":
            await interactive_menu(client)
            
        elif mode == "2":
            print("\n🎬 Ejecutando demo automático...\n")
            await asyncio.sleep(1)
            
            # Demo: Monitorear heartbeat
            await monitor_heartbeat(client, duration=5)
            
            # Demo: Búsqueda de barcode
            await workflow_barcode_lookup(client, "ABC123456")
            
            # Demo: Solicitar UUID
            await workflow_request_uuid(client)
            
            # Demo: Escribir a DB
            await workflow_write_to_db(client)
            
            # Estado final
            await client.read_all_tags()
            
        elif mode == "3":
            print("\n📺 Modo monitoreo - Presiona Ctrl+C para salir\n")
            while True:
                await client.read_all_tags()
                await asyncio.sleep(2)
                
        await client.disconnect()
        
    else:
        print("\n❌ No se pudo conectar al servidor.")
        print("   Verifica que el simulador esté corriendo:")
        print("   python gateway_simulator.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Cliente terminado por el usuario")
