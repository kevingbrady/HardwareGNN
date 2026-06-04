from pyosys import libyosys as yosys


def get_module_hierarchy(design):
    visited = set()
    ordered_list = []

    def traverse(module):
        if module is None or module.name.str() in visited:
            return

        visited.add(module.name.str())
        ordered_list.append(module)

        # Recurse through all instantiated sub-modules
        for cell_id, cell in module.cells_.items():
            cell_type = cell.type.str()
            # Ensure the cell is not a standard primitive but a defined module
            if design.has(cell_type):
                sub_module = design.module(cell_type)
                traverse(sub_module)

    # 1. Start traversal at the top module
    top_mod = design.top_module()
    if top_mod:
        traverse(top_mod)

    return ordered_list

def compact_dir(obj):
    return set(dir(obj)) - set(dir(object))



def get_bit_key(sig_bit):
    """
    Extracts a unique, hashable C++ tuple from a SigBit object.
    This bypasses Python instance reference mismatches.
    """
    if sig_bit.wire:
        # returns (wire_name_str, bit_index) e.g., ('\\my_net', 2)
        return sig_bit.wire.name.c_str().replace('\\', ''), sig_bit.offset
    else:
        # Handles constant values (0, 1, x, z) by using their enum data value
        return "const", sig_bit.data
