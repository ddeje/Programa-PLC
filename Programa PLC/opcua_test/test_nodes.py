"""
Probar lectura/escritura directa con diferentes NodeIds
"""
import asyncio
from asyncua import Client

async def main():
    url = "opc.tcp://192.168.101.100:59100"
    
    print(f"Conectando a {url}...")
    client = Client(url, timeout=10)
    
    try:
        await client.connect()
        print("✅ Conectado!\n")
        
        # Lista de NodeIds a probar (encontrados en la exploracion)
        test_nodes = [
            # Tags del PLC
            ("ns=9;g=f1cd0d74-04dd-ea1e-77b3-54917c94cc70", "heartbeat"),
            ("ns=9;g=dd27f0d8-6631-6e08-8735-5776a29e234c", "EdCommIn/Heartbeat"),
            ("ns=9;g=280af14d-07e5-ee54-1646-8cf8ec49cd40", "RecordNotFound"),
            ("ns=9;g=fe00b1dc-bedd-1c3e-d261-c8282e7cf8e9", "EdCommIn/RecordNotFound"),
        ]
        
        print("Probando lectura de tags...")
        print("="*60)
        
        for node_id, name in test_nodes:
            try:
                node = client.get_node(node_id)
                
                # Intentar leer atributos
                browse_name = await node.read_browse_name()
                node_class = await node.read_node_class()
                
                print(f"\n📊 {name}")
                print(f"   NodeId: {node_id}")
                print(f"   BrowseName: {browse_name.Name}")
                print(f"   NodeClass: {node_class}")
                
                # Intentar leer valor
                try:
                    val = await node.read_value()
                    print(f"   ✅ Valor: {val}")
                    
                    # Intentar escribir
                    try:
                        if isinstance(val, bool):
                            await node.write_value(not val)
                            new_val = await node.read_value()
                            print(f"   ✅ Escritura OK! Nuevo valor: {new_val}")
                    except Exception as we:
                        print(f"   ⚠️ No se pudo escribir: {we}")
                        
                except Exception as re:
                    print(f"   ❌ Error lectura: {str(re)[:60]}")
                    
            except Exception as e:
                print(f"\n❌ {name}: {str(e)[:60]}")
        
        # Verificar si hay variables en Model namespace
        print("\n" + "="*60)
        print("Buscando en Model/GlobalVars...")
        
        # Probar formato alternativo
        alt_formats = [
            "ns=9;s=GlobalVars.EgComIn_Heartbeat",
            "ns=9;s=Model.GlobalVars.EgComIn_Heartbeat",
            "ns=1;s=GlobalVars.EgComIn_Heartbeat",
        ]
        
        for fmt in alt_formats:
            try:
                node = client.get_node(fmt)
                val = await node.read_value()
                print(f"✅ {fmt} = {val}")
            except:
                print(f"❌ {fmt}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    asyncio.run(main())
