from enum import Enum
from typing import List


from bitcoin_coin_selection.selection_types.input_coin import InputCoin
from bitcoin_coin_selection.selection_types.output_group import OutputGroup
from bitcoin_coin_selection.selection_types.coin_selection_params import CoinSelectionParams



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
    fee: int
    change_value: int

    def __init__(self,
                 params: CoinSelectionParams,
                 selected_output_groups: List[OutputGroup] = None,
                 outcome=Outcome.SUCCESS
        ):
        self.target_value = params.target_value
        self.outputs = []
        self.effective_value = 0
        self.value = 0
        self.outcome = outcome
        if selected_output_groups:
            for output_group in selected_output_groups:
                for output in output_group.outputs:
                    self.insert(output)

        self.fee = self.calculate_fee(params.fixed_fee)
        self.change_value = self.calculate_change_value(params.cost_of_change)

    @classmethod
    def insufficient_funds(cls, target_value: int):
        return cls(target_value, outcome=cls.Outcome.INSUFFICIENT_FUNDS)

    @classmethod
    def insufficient_funds_after_fees(cls, target_value: int):
        return cls(target_value, outcome=cls.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES)

    @classmethod
    def algorithm_failure(cls, target_value: int):
        return cls(target_value, outcome=cls.Outcome.ALGORITHM_FAILURE)

    @classmethod
    def invalid_spend(cls, target_value: int):
        return cls(target_value, outcome=cls.Outcome.INVALID_SPEND)

    @classmethod
    def from_utxo_pool(
        cls,
        params: CoinSelectionParams,
        utxo_pool: List[OutputGroup],
        best_selection: List[bool],
    ):

        selected_groups = []
        for i, was_selected in enumerate(best_selection):
            if was_selected:
                selected_group = utxo_pool[i]
                selected_groups.append(selected_group)

        return cls(params, selected_groups)

    def insert(self, output: InputCoin):
        self.outputs.append(output)
        self.effective_value += output.effective_value
        self.value += output.value

    def calculate_change_value(self, cost_of_change: int):
        if self.outcome != self.Outcome.SUCCESS:
            return 0
        change_value = max(self.effective_value - self.target_value, 0)
        if change_value <= cost_of_change:
            change_value = 0
        return change_value

    def calculate_fee(self, fixed_fee: int):
        if self.outcome != self.Outcome.SUCCESS:
            return 0
        return fixed_fee + self.value - self.effective_value


