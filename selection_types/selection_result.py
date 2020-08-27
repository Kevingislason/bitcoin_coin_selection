from typing import List

from selection_types.input_coin import InputCoin
from selection_types.output_group import OutputGroup


class SelectionResult():
    outputs: List[InputCoin]
    value: int
    effective_value: int
    fee: int

    def __init__(self, selected_output_groups: List[OutputGroup] = None):
        self.outputs = []
        self.value = 0
        self.effective_value = 0
        self.fee = 0
        if selected_output_groups:
            for output_group in selected_output_groups:
                for output in output_group.outputs:
                    self.insert(output_group)

    @classmethod
    def from_utxo_pool(cls, best_selection: List[bool], utxo_pool: List[OutputGroup]):
        selected_groups = []
        for i, was_selected in enumerate(best_selection):
            if was_selected:
                selected_group = utxo_pool[i]
                selected_groups.append(selected_group)

        return cls(selected_groups)

    def insert(self, output: InputCoin):
        self.outputs.append(output)
        self.value += output.value
        self.effective_value += output.effective_value
        self.fee += output.fee

    # def __init__(self, best_selection: List[bool], utxo_pool: List[OutputGroup]):
