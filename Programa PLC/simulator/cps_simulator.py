"""
================================================================================
    CPS_001 - CORN PROCESSING SYSTEM SIMULATOR
    Version 2.0 - PULL SYSTEM Simulation
    
    Simula la lógica del PLC para probar antes de implementar
================================================================================
"""

import time
import os
import sys
import threading
import msvcrt  # Windows keyboard input

# ============================================================================
# CONFIGURACIÓN DE TIEMPOS (en segundos para simulación rápida)
# ============================================================================
TRANSFER_TIME = 2.0      # Tiempo para transferir material entre grupos
EMPTY_DETECT_TIME = 1.0  # Tiempo para detectar grupo vacío
SCAN_CYCLE = 0.1         # Velocidad del ciclo de escaneo

# ============================================================================
# ESTADO DEL SISTEMA (Tags del PLC simulados)
# ============================================================================
class PLCTags:
    def __init__(self):
        # --- INPUTS (Sensores) ---
        self.Compressed_Air = True
        self.Dust_Collector_ON = True
        self.AEC_Sheller_ON = True
        self.VMEK_Rdy = True
        self.R12_Ready = True
        self.R12_Envelope_Present = True
        
        # Sensores de material
        self.AEC_Material_Sensor = False
        self.Aspirator_Hopper_Sensor = False
        self.R12_Hopper_Sensor = False
        
        # Botones
        self.Barcode_Scanned = False
        self.BATCH_READY_Button = False
        self.START_Button = False
        self.E_Stop_Button = False
        self.E_Stop_Reset_Button = False
        
        # --- INTERNAL (Lógica interna) ---
        self.Batch_Ready_Latched = False
        self.CPS_RDY = False
        self.Cycle_Start_Enabled = False
        self.Cycle_Active = False
        self.Cycle_Complete = False
        self.Cycle_Step = 0
        
        # Group Status
        self.Group1_Empty = True
        self.Group2_Empty = True
        self.Group3_Empty = True
        self.Group4_Empty = True
        self.Group1_Has_Material = False
        self.Group2_Has_Material = False
        self.Group3_Has_Material = False
        self.Group4_Has_Material = False
        
        # Step Active flags
        self.Step1_Active = False
        self.Step2_Active = False
        self.Step3_Active = False
        self.Waiting_For_Group4_Empty = False
        
        # E-Stop
        self.E_Stop_Condition = False
        self.E_Stop_Active = False
        
        # --- OUTPUTS (Actuadores) ---
        self.R12_Hopper_Gate = False
        self.Aspirator_Hopper_Gate = False
        self.Material_Gate_Open = False
        self.Air_Conveyor = False
        self.Aspirator_Gate = False
        self.R12_Permit = False
        
        # Luces indicadoras
        self.Ready_To_Load_Light = False
        self.Cycle_In_Progress_Light = False
        self.Cycle_Complete_Light = False
        self.Material_Incoming_Light = False
        self.R12_Processing_Light = False
        
        # --- SIMULATION INTERNAL ---
        self._material_in_group1 = 0.0  # Cantidad de material (0-100%)
        self._material_in_group2 = 0.0
        self._material_in_group3 = 0.0
        self._material_in_group4 = 0.0
        self._transfer_progress = 0.0

# ============================================================================
# LÓGICA DEL PLC (Traducción del programa L5K)
# ============================================================================
class PLCLogic:
    def __init__(self, tags: PLCTags):
        self.tags = tags
        self.last_scan_time = time.time()
    
    def scan(self):
        """Ejecuta un ciclo de escaneo del PLC"""
        dt = time.time() - self.last_scan_time
        self.last_scan_time = time.time()
        
        t = self.tags
        
        # ============================================================
        # SECTION 0: OPERATOR WORKFLOW
        # ============================================================
        
        # RUNG 0.2: Batch Ready Latch
        if t.Barcode_Scanned and t.BATCH_READY_Button and not t.Cycle_Active:
            t.Batch_Ready_Latched = True
            t.BATCH_READY_Button = False  # Reset button
        
        # RUNG 0.3: Clear Batch Ready when cycle completes
        if t.Cycle_Complete:
            t.Batch_Ready_Latched = False
            t.Barcode_Scanned = False
        
        # ============================================================
        # SECTION 1: GROUP STATUS DETECTION
        # ============================================================
        
        # Update material sensors based on simulation
        t.Group1_Has_Material = t._material_in_group1 > 5
        t.Group2_Has_Material = t._material_in_group2 > 5
        t.Group3_Has_Material = t._material_in_group3 > 5
        t.Group4_Has_Material = t._material_in_group4 > 5
        
        t.Group1_Empty = not t.Batch_Ready_Latched and t._material_in_group1 < 5
        t.Group2_Empty = t._material_in_group2 < 5
        t.Group3_Empty = t._material_in_group3 < 5
        t.Group4_Empty = t._material_in_group4 < 5
        
        # Update physical sensors
        t.AEC_Material_Sensor = t._material_in_group2 > 5
        t.Aspirator_Hopper_Sensor = t._material_in_group3 > 5
        t.R12_Hopper_Sensor = t._material_in_group4 > 5
        
        # ============================================================
        # SECTION 2: SYSTEM READY CONDITIONS
        # ============================================================
        
        # RUNG 2.1: System Ready
        t.CPS_RDY = (t.Compressed_Air and t.Dust_Collector_ON and 
                    t.AEC_Sheller_ON and t.VMEK_Rdy)
        
        # RUNG 2.2: Cycle Start Enable
        t.Cycle_Start_Enabled = (t.CPS_RDY and t.Group4_Empty and 
                                  t.R12_Ready and t.R12_Envelope_Present and
                                  t.Batch_Ready_Latched and not t.E_Stop_Active)
        
        # ============================================================
        # SECTION 3: SEQUENTIAL PULL SEQUENCE
        # ============================================================
        
        # RUNG 3.1: Start Cycle
        if t.Cycle_Start_Enabled and t.START_Button and not t.Cycle_Active:
            t.Cycle_Active = True
            t.Cycle_Step = 1
            t.Cycle_Complete = False
            t.START_Button = False
            # Simular material en Group 1
            t._material_in_group1 = 100.0
        
        # RUNG 3.3: Step 1 - R12_Hopper_Gate
        t.Step1_Active = t.Cycle_Active and t.Cycle_Step == 1 and t.Group4_Empty
        if t.Step1_Active:
            t.R12_Hopper_Gate = True
        
        # RUNG 3.4: Step 1 Complete
        if t.Step1_Active and t.Group3_Empty and t._material_in_group3 < 5:
            t.Cycle_Step = 2
        
        # RUNG 3.5: Step 2 - Aspirator_Hopper_Gate
        t.Step2_Active = t.Cycle_Active and t.Cycle_Step == 2 and t.Group3_Empty
        if t.Step2_Active:
            t.Aspirator_Hopper_Gate = True
        
        # RUNG 3.6: Step 2 Complete
        if t.Step2_Active and t.Group2_Empty and t._material_in_group2 < 5:
            t.Cycle_Step = 3
        
        # RUNG 3.7: Step 3 - Material_Gate + Air_Conveyor + Aspirator_Gate
        t.Step3_Active = t.Cycle_Active and t.Cycle_Step == 3 and t.Group2_Empty
        if t.Step3_Active:
            t.Material_Gate_Open = True
            t.Air_Conveyor = True
            t.Aspirator_Gate = True
        
        # RUNG 3.8: Step 3 Complete
        if t.Step3_Active and t._material_in_group1 < 5:
            t.Cycle_Step = 4
            t.Batch_Ready_Latched = False  # Material salió de Group 1
        
        # RUNG 3.9-3.10: Step 4 - Waiting for all groups to empty
        t.Waiting_For_Group4_Empty = (t.Cycle_Active and t.Cycle_Step == 4 and
                                       t.Group1_Empty and t.Group2_Empty and t.Group3_Empty)
        
        if t.Waiting_For_Group4_Empty and t.Group4_Empty:
            t.Cycle_Complete = True
        
        # RUNG 3.11: Reset Cycle
        if t.Cycle_Complete:
            t.Cycle_Active = False
            t.Cycle_Step = 0
        
        # ============================================================
        # SECTION 4: GATE AUTO-CLOSE
        # ============================================================
        
        if not t.Step1_Active:
            t.R12_Hopper_Gate = False
        if not t.Step2_Active:
            t.Aspirator_Hopper_Gate = False
        if not t.Step3_Active:
            t.Material_Gate_Open = False
            t.Air_Conveyor = False
            t.Aspirator_Gate = False
        
        # ============================================================
        # SECTION 5: R12 PERMIT
        # ============================================================
        t.R12_Permit = t.R12_Hopper_Sensor and t.R12_Ready and t.CPS_RDY
        
        # ============================================================
        # SECTION 6: INDICATORS
        # ============================================================
        t.Ready_To_Load_Light = t.CPS_RDY and not t.Batch_Ready_Latched and not t.Cycle_Active
        t.Cycle_In_Progress_Light = t.Cycle_Active
        t.Cycle_Complete_Light = t.Cycle_Complete
        t.Material_Incoming_Light = t.Group3_Has_Material
        t.R12_Processing_Light = t.Group4_Has_Material
        
        # ============================================================
        # SECTION 7: E-STOP
        # ============================================================
        t.E_Stop_Condition = (not t.Compressed_Air or not t.Dust_Collector_ON or 
                              t.E_Stop_Button)
        
        if t.E_Stop_Condition:
            t.E_Stop_Active = True
        
        if t.E_Stop_Active and t.E_Stop_Reset_Button and not t.E_Stop_Condition:
            t.E_Stop_Active = False
            t.E_Stop_Reset_Button = False
        
        # ============================================================
        # SIMULATION: Material Transfer Physics
        # ============================================================
        self._simulate_material_transfer(dt)
    
    def _simulate_material_transfer(self, dt):
        """Simula el movimiento físico del material"""
        t = self.tags
        transfer_rate = 50.0 * dt  # % por segundo
        
        # Step 3: Group1 → Group2 (cuando Material_Gate_Open)
        if t.Material_Gate_Open and t._material_in_group1 > 0:
            transfer = min(transfer_rate, t._material_in_group1)
            t._material_in_group1 -= transfer
            t._material_in_group2 += transfer
        
        # Step 2: Group2 → Group3 (cuando Aspirator_Hopper_Gate)
        if t.Aspirator_Hopper_Gate and t._material_in_group2 > 0:
            transfer = min(transfer_rate, t._material_in_group2)
            t._material_in_group2 -= transfer
            t._material_in_group3 += transfer
        
        # Step 1: Group3 → Group4 (cuando R12_Hopper_Gate)
        if t.R12_Hopper_Gate and t._material_in_group3 > 0:
            transfer = min(transfer_rate, t._material_in_group3)
            t._material_in_group3 -= transfer
            t._material_in_group4 += transfer
        
        # R12 procesa material (cuando R12_Permit)
        if t.R12_Permit and t._material_in_group4 > 0:
            t._material_in_group4 -= transfer_rate * 0.5  # R12 procesa más lento
            if t._material_in_group4 < 0:
                t._material_in_group4 = 0

# ============================================================================
# INTERFAZ DE USUARIO (Consola)
# ============================================================================
class SimulatorUI:
    def __init__(self, tags: PLCTags):
        self.tags = tags
        self.running = True
        self.messages = []
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def add_message(self, msg):
        self.messages.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        if len(self.messages) > 5:
            self.messages.pop(0)
    
    def render(self):
        self.clear_screen()
        t = self.tags
        
        # Material bars
        def bar(value, width=20):
            filled = int(value / 100 * width)
            return '█' * filled + '░' * (width - filled)
        
        # Gate status
        def gate(is_open):
            return "\033[92mOPEN\033[0m" if is_open else "\033[91mCLOSED\033[0m"
        
        # Light status
        def light(is_on, color="92"):
            return f"\033[{color}m●\033[0m" if is_on else "○"
        
        # System status color
        sys_color = "\033[92m" if t.CPS_RDY else "\033[91m"
        estop_color = "\033[91m" if t.E_Stop_Active else "\033[92m"
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CPS-001 CORN PROCESSING SYSTEM SIMULATOR                  ║
║                           Version 2.0 - PULL SYSTEM                          ║
╠══════════════════════════════════════════════════════════════════════════════╣""")
        
        print(f"""║  SYSTEM STATUS: {sys_color}{'READY' if t.CPS_RDY else 'NOT READY'}\033[0m     E-STOP: {estop_color}{'ACTIVE!' if t.E_Stop_Active else 'OK'}\033[0m     CYCLE: Step {t.Cycle_Step}""")
        print("""╠══════════════════════════════════════════════════════════════════════════════╣""")
        
        print(f"""║                                                                              ║
║  ┌─────────────────┐                                                         ║
║  │ GROUP 1: FEEDER │  {bar(t._material_in_group1)} {t._material_in_group1:5.1f}%                  ║
║  │ (Manual Load)   │  Batch Ready: {'YES' if t.Batch_Ready_Latched else 'NO '}                               ║
║  └────────┬────────┘                                                         ║
║           │ Material Gate: {gate(t.Material_Gate_Open)}                                         ║
║           ▼                                                                  ║
║  ┌─────────────────┐                                                         ║
║  │ GROUP 2: SHELLER│  {bar(t._material_in_group2)} {t._material_in_group2:5.1f}%                  ║
║  │ + Air Conveyor  │  Air Conveyor: {'ON ' if t.Air_Conveyor else 'OFF'}  Aspirator: {'ON ' if t.Aspirator_Gate else 'OFF'}          ║
║  └────────┬────────┘                                                         ║
║           │ Aspirator Hopper Gate: {gate(t.Aspirator_Hopper_Gate)}                              ║
║           ▼                                                                  ║
║  ┌─────────────────┐                                                         ║
║  │ GROUP 3: ASP.   │  {bar(t._material_in_group3)} {t._material_in_group3:5.1f}%                  ║
║  │ HOPPER → VMEK   │                                                         ║
║  └────────┬────────┘                                                         ║
║           │ R12 Hopper Gate: {gate(t.R12_Hopper_Gate)}                                      ║
║           ▼                                                                  ║
║  ┌─────────────────┐                                                         ║
║  │ GROUP 4: R12    │  {bar(t._material_in_group4)} {t._material_in_group4:5.1f}%                  ║
║  │ SEED TREATER    │  R12 Permit: {'YES' if t.R12_Permit else 'NO '}                                  ║
║  └─────────────────┘                                                         ║""")
        
        print("""╠══════════════════════════════════════════════════════════════════════════════╣""")
        print(f"""║  INDICATORS:  {light(t.Ready_To_Load_Light, "92")} Ready to Load   {light(t.Cycle_In_Progress_Light, "93")} In Progress   {light(t.Cycle_Complete_Light, "94")} Complete     ║""")
        print(f"""║               {light(t.Material_Incoming_Light, "93")} Material Incoming   {light(t.R12_Processing_Light, "95")} R12 Processing                   ║""")
        print("""╠══════════════════════════════════════════════════════════════════════════════╣""")
        print("""║  CONTROLS:                                                                   ║""")
        print(f"""║  [1] Scan Barcode {'✓' if t.Barcode_Scanned else ' '}   [2] Batch Ready   [3] START   [E] E-Stop   [R] Reset  ║""")
        print("""║  [Q] Quit                                                                    ║""")
        print("""╠══════════════════════════════════════════════════════════════════════════════╣""")
        print("""║  LOG:                                                                        ║""")
        for msg in self.messages[-4:]:
            print(f"║  {msg:<74} ║")
        for _ in range(4 - len(self.messages[-4:])):
            print(f"║  {'':<74} ║")
        print("""╚══════════════════════════════════════════════════════════════════════════════╝""")
    
    def handle_input(self):
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            t = self.tags
            
            if key == '1':
                t.Barcode_Scanned = True
                self.add_message("Barcode scanned - Product: CORN_LOT_001")
            elif key == '2':
                if t.Barcode_Scanned:
                    t.BATCH_READY_Button = True
                    self.add_message("Batch Ready button pressed")
                else:
                    self.add_message("ERROR: Scan barcode first!")
            elif key == '3':
                if t.Cycle_Start_Enabled:
                    t.START_Button = True
                    self.add_message("START pressed - Beginning cycle...")
                else:
                    self.add_message("ERROR: System not ready to start!")
            elif key == 'e':
                t.E_Stop_Button = True
                self.add_message("!!! E-STOP ACTIVATED !!!")
            elif key == 'r':
                t.E_Stop_Button = False
                t.E_Stop_Reset_Button = True
                self.add_message("E-Stop Reset pressed")
            elif key == 'q':
                self.running = False
                self.add_message("Shutting down...")
            
            return True
        return False

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("Iniciando CPS-001 Simulator...")
    print("Presiona cualquier tecla para continuar...")
    msvcrt.getch()
    
    tags = PLCTags()
    plc = PLCLogic(tags)
    ui = SimulatorUI(tags)
    
    ui.add_message("Sistema iniciado - Listo para operar")
    ui.add_message("Presiona [1] para escanear código de barras")
    
    last_render = 0
    render_interval = 0.1  # Actualizar pantalla cada 100ms
    
    while ui.running:
        # PLC Scan
        plc.scan()
        
        # Handle keyboard input
        ui.handle_input()
        
        # Render UI (throttled)
        if time.time() - last_render > render_interval:
            ui.render()
            last_render = time.time()
        
        time.sleep(SCAN_CYCLE)
    
    print("\n\nSimulador terminado.")

if __name__ == "__main__":
    main()
