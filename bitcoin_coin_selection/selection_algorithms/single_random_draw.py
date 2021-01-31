import random
from typing import List

from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from bitcoin_coin_selection.selection_types.coin_selection_params import CoinSelectionParams
from bitcoin_coin_selection.selection_types.output_group import OutputGroup


def select_coins_single_random_draw(params: CoinSelectionParams) -> CoinSelection:
    target_after_fixed_fee = params.target_value + params.fixed_fee
    random.shuffle(params.utxo_pool)
    selected_output_groups = []
    selected_value = 0
    for output_group in params.utxo_pool:
        selected_value += output_group.effective_value
        selected_output_groups.append(output_group)
        if selected_value >= target_after_fixed_fee:
            return CoinSelection(params, selected_output_groups)

    return CoinSelection.algorithm_failure(params)
