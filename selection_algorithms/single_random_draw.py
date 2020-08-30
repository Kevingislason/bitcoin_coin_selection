import random
from typing import List

from selection_types.coin_selection import CoinSelection

from selection_types.output_group import OutputGroup


def select_coins_single_random_draw(
        utxo_pool: List[OutputGroup], target_value: int) -> CoinSelection:

    random.shuffle(utxo_pool)
    selected_output_groups = []
    selected_value = 0
    for output_group in utxo_pool:
        selected_value += output_group.effective_value
        selected_output_groups.append(output_group)
        if selected_value >= target_value:
            return CoinSelection(selected_output_groups)

    return CoinSelection.algorithm_failure()
