from typing import List

from output_group import OutputGroup


def assemble_output_set(best_selection: List[bool],
                        utxo_pool: List[OutputGroup]) -> OutputGroup:
    selected_outputs = OutputGroup()
    for i, was_selected in enumerate(best_selection):
        if was_selected:
            output_group = utxo_pool[i]
            selected_outputs.insert_group(output_group)
    return selected_outputs
