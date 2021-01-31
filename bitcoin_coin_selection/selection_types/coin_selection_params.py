from typing import List

from bitcoin_coin_selection.selection_types.output_group import OutputGroup

class CoinSelectionParams:
    def __init__(
      self,
      utxo_pool: List[OutputGroup],
      target_value: int,
      short_term_fee_per_byte : int,
      long_term_fee_per_byte: int,
      change_output_size_in_bytes: int,
      change_spend_size_in_bytes: int,
      not_input_size_in_bytes: int
    ):
        for outut_group in utxo_pool:
            outut_group.set_fee(short_term_fee_per_byte, long_term_fee_per_byte)
        self.utxo_pool = utxo_pool
        self.target_value = target_value
        self.short_term_fee_per_byte = short_term_fee_per_byte
        self.long_term_fee_per_byte = long_term_fee_per_byte
        self.change_output_size_in_bytes = change_output_size_in_bytes
        self.change_spend_size_in_bytes = change_spend_size_in_bytes
        self.not_input_size_in_bytes = not_input_size_in_bytes

    @property
    def total_value(self):
        return int(sum(output_group.value for output_group in self.utxo_pool))

    @property
    def total_effective_value(self):
        return int(
          sum(output_group.effective_value for output_group in self.utxo_pool)
        )

    @property
    def fixed_fee(self):
        return self.short_term_fee_per_byte * self.not_input_size_in_bytes

    @property
    def cost_of_creating_change(self):
        return self.short_term_fee_per_byte * self.change_output_size_in_bytes

    @property
    def cost_of_spending_change(self):
        return self.long_term_fee_per_byte * self.change_spend_size_in_bytes

    @property
    def cost_of_change(self):
        return self.cost_of_spending_change + self.cost_of_creating_change







