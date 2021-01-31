from bitcoin_coin_selection.selection_types.coin_selection_params import CoinSelectionParams


class TestParams(CoinSelectionParams):
    def __init__(self, utxo_pool, target_value, cost_of_change = None):
        super().__init__(
          utxo_pool,
          target_value,
          short_term_fee_per_byte=0,
          long_term_fee_per_byte=0,
          change_output_size_in_bytes=0,
          change_spend_size_in_bytes=0,
          not_input_size_in_bytes=0
        )
        self._cost_of_change = cost_of_change

    @property
    def cost_of_change(self):
      if self._cost_of_change:
        return self._cost_of_change
      return super().cost_of_change
