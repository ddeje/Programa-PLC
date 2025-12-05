"""
================================================================================
    SIMULADOR DE GATEWAY OPC UA
    
    Este programa crea un servidor OPC UA que simula los tags del Edge Gateway
    del PLC Rockwell para desarrollo y pruebas.
    
    Tags simulados:
    - EgComIn_Heartbeat, EgComIn_RecordNotFound, EgComIn_UUID_pull, etc.
    - EgComOut_BarcodeReq, EgComOut_BarcodeValue, EgComOut_WriteToDb, etc.
    
    Ejecutar con: python gateway_simulator.py
================================================================================
"""

import asyncio
import logging
from datetime import datetime
from asyncua import Server, ua
from asyncua.common.methods import uamethod

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GatewaySimulator")

# ============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================================

SERVER_URL = "opc.tcp://0.0.0.0:4840"  # Escucha en todas las interfaces
SERVER_NAME = "EdgeGateway Simulator"
NAMESPACE_URI = "urn:RockwellAutomation:EdgeGateway:Simulator"


class GatewaySimulator:
    """Simulador del Edge Gateway con tags OPC UA."""
    
    def __init__(self):
        self.server = None
        self.namespace_idx = None
        
        # Referencias a los nodos de tags para manipulación
        self.tags = {}
        
        # Estado interno del simulador
        self.heartbeat_counter = 0
        self.simulation_running = True
        
    async def init_server(self):
        """Inicializa el servidor OPC UA."""
        
        self.server = Server()
        await self.server.init()
        
        self.server.set_endpoint(SERVER_URL)
        self.server.set_server_name(SERVER_NAME)
        
        # Registrar namespace
        self.namespace_idx = await self.server.register_namespace(NAMESPACE_URI)
        logger.info(f"Namespace registrado: ns={self.namespace_idx}")
        
        # Crear estructura de objetos
        await self._create_tag_structure()
        
        logger.info(f"Servidor configurado en {SERVER_URL}")
        
    async def _create_tag_structure(self):
        """Crea la estructura de tags que simula el Gateway."""
        
        objects = self.server.nodes.objects
        
        # Crear carpeta GlobalVars (como en el PLC real)
        global_vars = await objects.add_folder(
            self.namespace_idx, 
            "GlobalVars"
        )
        
        # ====================================================================
        # TAGS DE ENTRADA (Gateway -> PLC) - EgComIn
        # ====================================================================
        
        # Heartbeat - Boolean
        self.tags["Heartbeat"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComIn_Heartbeat",
            False,
            ua.VariantType.Boolean
        )
        await self.tags["Heartbeat"].set_writable()
        
        # RecordNotFound - Boolean
        self.tags["RecordNotFound"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComIn_RecordNotFound",
            False,
            ua.VariantType.Boolean
        )
        await self.tags["RecordNotFound"].set_writable()
        
        # WriteToDb_Confirmation - Boolean
        self.tags["WriteToDb_Confirmation"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComIn_WriteToDb_Confirmation",
            False,
            ua.VariantType.Boolean
        )
        await self.tags["WriteToDb_Confirmation"].set_writable()
        
        # UUID_pull - String (simulamos la estructura como string JSON)
        self.tags["UUID_pull"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComIn_UUID_pull",
            '{"uuid": "", "timestamp": "", "data": {}}',
            ua.VariantType.String
        )
        await self.tags["UUID_pull"].set_writable()
        
        # ====================================================================
        # TAGS DE SALIDA (PLC -> Gateway) - EgComOut
        # ====================================================================
        
        # BarcodeReq - Boolean
        self.tags["BarcodeReq"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComOut_BarcodeReq",
            False,
            ua.VariantType.Boolean
        )
        await self.tags["BarcodeReq"].set_writable()
        
        # BarcodeValue - String
        self.tags["BarcodeValue"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComOut_BarcodeValue",
            "",
            ua.VariantType.String
        )
        await self.tags["BarcodeValue"].set_writable()
        
        # UUIDReq - Boolean
        self.tags["UUIDReq"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComOut_UUIDReq",
            False,
            ua.VariantType.Boolean
        )
        await self.tags["UUIDReq"].set_writable()
        
        # WriteToDb - Boolean
        self.tags["WriteToDb"] = await global_vars.add_variable(
            self.namespace_idx,
            "EgComOut_WriteToDb",
            False,
            ua.VariantType.Boolean
        )
        await self.tags["WriteToDb"].set_writable()
        
        # ====================================================================
        # TAGS ADICIONALES PARA SIMULACIÓN
        # ====================================================================
        
        # Contador de simulación
        self.tags["SimulationCounter"] = await global_vars.add_variable(
            self.namespace_idx,
            "SimulationCounter",
            0,
            ua.VariantType.Int32
        )
        
        # Timestamp
        self.tags["LastUpdate"] = await global_vars.add_variable(
            self.namespace_idx,
            "LastUpdate",
            datetime.now().isoformat(),
            ua.VariantType.String
        )
        
        logger.info("Tags creados:")
        for name, node in self.tags.items():
            node_id = node.nodeid.to_string()
            logger.info(f"  - {name}: {node_id}")
            
    async def run_heartbeat(self):
        """Ejecuta el heartbeat toggle automático."""
        
        while self.simulation_running:
            try:
                # Toggle heartbeat
                current = await self.tags["Heartbeat"].read_value()
                await self.tags["Heartbeat"].write_value(not current)
                
                # Incrementar contador
                self.heartbeat_counter += 1
                await self.tags["SimulationCounter"].write_value(self.heartbeat_counter)
                
                # Actualizar timestamp
                await self.tags["LastUpdate"].write_value(datetime.now().isoformat())
                
                await asyncio.sleep(1)  # Heartbeat cada segundo
                
            except Exception as e:
                logger.error(f"Error en heartbeat: {e}")
                await asyncio.sleep(1)
                
    async def run_simulation_logic(self):
        """Simula la lógica del Gateway respondiendo a requests."""
        
        while self.simulation_running:
            try:
                # Verificar si hay solicitud de barcode
                barcode_req = await self.tags["BarcodeReq"].read_value()
                if barcode_req:
                    # Simular lectura de barcode
                    barcode = await self.tags["BarcodeValue"].read_value()
                    if barcode:
                        logger.info(f"📦 Barcode recibido: {barcode}")
                        # Aquí iría la lógica de buscar en base de datos
                        
                        # Simular respuesta después de 500ms
                        await asyncio.sleep(0.5)
                        
                        # Resetear el request (simula que PLC lo hace)
                        # await self.tags["BarcodeReq"].write_value(False)
                        
                # Verificar si hay solicitud de UUID
                uuid_req = await self.tags["UUIDReq"].read_value()
                if uuid_req:
                    logger.info("🔑 Solicitud de UUID recibida")
                    
                    # Simular respuesta con UUID
                    import uuid
                    new_uuid = str(uuid.uuid4())
                    uuid_data = f'{{"uuid": "{new_uuid}", "timestamp": "{datetime.now().isoformat()}", "data": {{}}}}'
                    await self.tags["UUID_pull"].write_value(uuid_data)
                    
                    logger.info(f"🔑 UUID generado: {new_uuid}")
                    
                # Verificar WriteToDb
                write_db = await self.tags["WriteToDb"].read_value()
                if write_db:
                    logger.info("💾 Solicitud de escritura a DB recibida")
                    
                    # Simular escritura exitosa
                    await asyncio.sleep(0.3)
                    await self.tags["WriteToDb_Confirmation"].write_value(True)
                    
                    # Reset después de un momento
                    await asyncio.sleep(0.5)
                    await self.tags["WriteToDb_Confirmation"].write_value(False)
                    
                await asyncio.sleep(0.1)  # Check cada 100ms
                
            except Exception as e:
                logger.error(f"Error en simulación: {e}")
                await asyncio.sleep(1)
                
    async def start(self):
        """Inicia el servidor y las tareas de simulación."""
        
        await self.init_server()
        
        print("\n" + "=" * 70)
        print("🚀 GATEWAY SIMULATOR INICIADO")
        print("=" * 70)
        print(f"\n📡 Servidor OPC UA corriendo en: {SERVER_URL}")
        print(f"📂 Namespace Index: {self.namespace_idx}")
        print(f"🏷️  Namespace URI: {NAMESPACE_URI}")
        print("\n📋 Tags disponibles:")
        print("-" * 50)
        for name, node in self.tags.items():
            print(f"   {node.nodeid.to_string()}")
        print("-" * 50)
        print("\n⏳ Presiona Ctrl+C para detener el servidor\n")
        
        async with self.server:
            # Iniciar tareas de simulación
            heartbeat_task = asyncio.create_task(self.run_heartbeat())
            simulation_task = asyncio.create_task(self.run_simulation_logic())
            
            try:
                # Mantener corriendo
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                self.simulation_running = False
                heartbeat_task.cancel()
                simulation_task.cancel()
                
        print("\n✅ Servidor detenido correctamente")


async def main():
    simulator = GatewaySimulator()
    await simulator.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
