from typing import Optional, List
from selection_types.output_group import OutputGroup
from selection_types.coin_selection import (
    CoinSelection
)


def check_for_insufficient_funds(
        utxo_pool: List[OutputGroup],
        target_value: int,
        not_input_fees: int) -> Optional[CoinSelection]:

    total_value = sum(
        [output_group.value for output_group in utxo_pool])
    if total_value < target_value:
        return CoinSelection.insufficient_funds()
    else:
        total_effective_value = sum(
            [output_group.value for output_group in utxo_pool])
        if total_effective_value < target_value + not_input_fees:
            return CoinSelection.insufficient_funds_after_fees()
    return None
