from enum import Enum
from typing import List


from bitcoin_coin_selection.selection_types.input_coin import InputCoin
from bitcoin_coin_selection.selection_types.output_group import OutputGroup


class CoinSelection():

    class Outcome(Enum):
        SUCCESS = 0
        INSUFFICIENT_FUNDS = 1
        INSUFFICIENT_FUNDS_AFTER_FEES = 2
        ALGORITHM_FAILURE = 3
        INVALID_SPEND = 4

    outcome: Outcome
    outputs: List[InputCoin]
    target_value: int
    effective_value: int
    value: int
    change_value: int
    fee: int

    def __init__(self,
                 target_value: int,
                 selected_output_groups: List[OutputGroup] = None,
                 outcome=Outcome.SUCCESS):
        self.target_value = target_value
        self.outputs = []
        self.effective_value = 0
        self.value = 0
        self.fee = 0
        self.outcome = outcome
        if selected_output_groups:
            for output_group in selected_output_groups:
                for output in output_group.outputs:
                    self.insert(output)
        self.change_value = self.value - self.target_value - self.fee

    @classmethod
    def insufficient_funds(cls, target_value: int):
        return cls(target_value, None, cls.Outcome.INSUFFICIENT_FUNDS)

    @classmethod
    def insufficient_funds_after_fees(cls, target_value: int):
        return cls(target_value, None, cls.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES)

    @classmethod
    def algorithm_failure(cls, target_value: int):
        return cls(target_value, None, cls.Outcome.ALGORITHM_FAILURE)

    @classmethod
    def invalid_spend(cls, target_value: int):
        return cls(target_value, None, cls.Outcome.INVALID_SPEND)

    @classmethod
    def from_utxo_pool(cls,
                       target_value: int,
                       best_selection: List[bool],
                       utxo_pool: List[OutputGroup]):

        selected_groups = []
        for i, was_selected in enumerate(best_selection):
            if was_selected:
                selected_group = utxo_pool[i]
                selected_groups.append(selected_group)

        return cls(target_value, selected_groups)

    def insert(self, output: InputCoin):
        self.outputs.append(output)
        self.effective_value += output.effective_value
        self.value += output.value
        self.fee += output.fee
