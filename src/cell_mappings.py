from pyosys import libyosys as yosys

# Comprehensive dictionary mapping cell types and port names to functional circuit roles
GATE_ROLE_MAP = {

    # D-Flip-Flops (Sync Reset)
    **{c: {"C": "Clock_Trigger", "D": "Data_Input_Pipeline_Path", "R": "Synchronous Reset/Preset", "Q": "State_Data_Output"}
       for c in ["$_SDFF_PP0_", "$_SDFF_PP1_", "$_SDFF_PN0_", "$_SDFF_PN1_", "$_SDFF_NP0_", "$_SDFF_NP1_", "$_SDFF_NN0_", "$_SDFF_NN1_"]},

    # D-Flip-Flops (Async Reset)
    **{c: {"C": "Clock_Trigger", "D": "Data_Input", "Q": "State_Output", "E": "Clock_Enable", "R": "Hardware_Reset"}
       for c in ["$_DFF_P_", "$_DFF_N_", "$_DFFE_PP_", "$_DFFE_PN_", "$_DFFE_NP_", "$_DFFE_NN_", "$_DFF_PP0_", "$_DFF_PP1_", "$_DFF_NP0_", "$_DFF_NP1_"]},

    # Multiplexers
    **{c: {"A": "Input(Select=0)", "B": "Input(Select=1)", "S": "Mux_Selector_Bit", "Y": "Mux_Output"}
       for c in ["$_MUX_", "$_NMUX_"]},

    # Binary Logic Gates
    **{c: {"A": "Logic_Input_A", "B": "Logic_Input_B", "Y": "Gate_Output"}
       for c in ["$_AND_", "$_OR_", "$_XOR_", "$_XNOR_", "$_NAND_", "$_NOR_"]},

    # Unary Inverter
    "$_NOT_": {"A": "Inverter_Input", "Y": "Inverted_Output"},

    # Multi-port Block RAM
    **{c: {"RD_CLK": "Memory_Array_Read_Clock_Bus_Reference_Domain", "RD_EN": "Memory_Array_Read_Enable_Gating_Protocol_Mask",
           "RD_ADDR": "Memory_Matrix_Source_Read_Address_Offset_Locator_Bus", "RD_DATA": "Memory_Array_Data_Out_Register_Extraction_Bus",
           "RD_ARST": "Memory_Read_Port_Asynchronous_Output_Register_Reset", "RD_SRST": "Memory_Read_Port_Synchronous_Output_Register_Reset",
           "WR_CLK": "Memory_Array_Write_Clock_Bus_Reference_Domain", "WR_EN": "Memory_Array_Write_Bit/Byte_Gating_Lane_Allocation_Mask",
           "WR_ADDR": "Memory_Matrix_Destination_Write_Address_Offset_Pointer_Bus", "WR_DATA": "Memory_Array_Data_In_Injection_Configuration_Bus"}
       for c in ["$mem_v2"]},

    # Complex AOI/OAI Gate Logic Primitives
    **{c: {"A": "Gate_Input_A", "B": "Gate_Input_B", "C": "Gate_Input_C", "D": "Gate_Input_D", "Y": "AOI_Output"}
       for c in ["$_AOI3_", "$_OAI3_", "$_AOI4_", "$_OAI4_"]}
}

CUSTOM_MODULE_ROLE_MAP = {
    "clk": "Module_Level_Timing_Domain_Anchor",
    "rcon": "Cryptographic_Scheduling_Vector/Non_Secret_State_Modifier"
}

CONST_STATE_MAP = {
    yosys.State.S0: 'GND',
    yosys.State.S1: 'VCC',
    yosys.State.Sx: 'UNCONNECTED_X',
    yosys.State.Sz: 'UNCONNECTED_Z',
    yosys.State.Sa: 'DONT_CARE_MARKER',
    yosys.State.Sm: 'INTERNAL_PASS_MARKER'
}
