from enum import Enum
from typing import List


from selection_types.input_coin import InputCoin
from selection_types.output_group import OutputGroup


class CoinSelection():

    class Outcome(Enum):
        SUCCESS = 0
        INSUFFICIENT_FUNDS = 1
        INSUFFICIENT_FUNDS_AFTER_FEES = 2
        ALGORITHM_FAILURE = 3
        INVALID_SPEND = 4

    outcome: Outcome
    target: int
    outputs: List[InputCoin]
    value: int
    effective_value: int
    fee: int

    def __init__(self, selected_output_groups: List[OutputGroup] = None, outcome=Outcome.SUCCESS):
        self.outputs = []
        self.value = 0
        self.effective_value = 0
        self.fee = 0
        self.outcome = outcome
        if selected_output_groups:
            for output_group in selected_output_groups:
                for output in output_group.outputs:
                    self.insert(output_group)

    @classmethod
    def insufficient_funds(cls):
        return cls(None, cls.Outcome.INSUFFICIENT_FUNDS)

    @classmethod
    def insufficient_funds_after_fees(cls):
        return cls(None, cls.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES)

    @classmethod
    def algorithm_failure(cls):
        return cls(None, cls.Outcome.ALGORITHM_FAILURE)

    @classmethod
    def invalid_spend(cls):
        return cls(None, cls.Outcome.INVALID_SPEND)

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
