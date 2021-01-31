from typing import List

from bitcoin_coin_selection.selection_types.change_constants import MAX_MONEY
from bitcoin_coin_selection.selection_types.output_group import OutputGroup
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from bitcoin_coin_selection.selection_types.coin_selection_params import CoinSelectionParams


TOTAL_TRIES = 100000


def select_coins_branch_and_bound(
    params: CoinSelectionParams
) -> CoinSelection:
    utxo_pool = params.utxo_pool
    target_after_fixed_fees = params.target_value + params.fixed_fee
    current_value = 0
    current_selection: List[bool] = []
    current_available_value = params.total_effective_value
    current_waste = 0
    best_waste = MAX_MONEY
    best_selection: List[bool] = []
    utxo_pool.sort(reverse=True)

    for i in range(TOTAL_TRIES):
        should_backtrack = False

        if (
            # Cannot possibly reach target with the amount remaining in the curr_available_value
            (current_value + current_available_value < target_after_fixed_fees)
            # Selected value is out of range, go back and try other branch
            or (current_value > target_after_fixed_fees + params.cost_of_change)
            # Don't select things which we know will be more wasteful if the waste is increasing
            or (current_waste > best_waste and utxo_pool[0].fee - utxo_pool[0].long_term_fee > 0)
        ):
            should_backtrack = True
        # Selected value is within range
        elif current_value >= target_after_fixed_fees:
            # This^^ is the excess value which is added to the waste for the below comparison
            # Adding another UTXO after this check could bring the waste down if the long term fee is higher than the current fee.
            # However we are not going to explore that because this optimization for the waste is only done when we have hit our target
            # value. Adding any more UTXOs will be just burning the UTXO; it will go entirely to fees. Thus we aren't going to
            # explore any more UTXOs to avoid burning money like that.

            current_waste += (current_value - target_after_fixed_fees)
            if current_waste <= best_waste:
                best_selection = current_selection.copy()
                best_waste = current_waste
                if (best_waste == 0):
                    return CoinSelection.from_utxo_pool(params, params.utxo_pool, best_selection)
            # Remove the excess value as we will be selecting different coins now
            current_waste -= (current_value - target_after_fixed_fees)
            should_backtrack = True
        # Backtracking, moving backwards
        if should_backtrack:
            # Walk backwards to find the last included UTXO
            # that still needs to have its omission branch traversed
            while len(current_selection) > 0 and current_selection[-1] == False:
                current_selection.pop()
                current_available_value += utxo_pool[len(
                    current_selection)].effective_value
            if len(current_selection) == 0:
                # We have walked back to the first utxo and no branch is untraversed.
                # All solutions searched
                break

            # Output was included on previous iterations, try excluding now
            current_selection[-1] = False
            utxo: OutputGroup = utxo_pool[len(current_selection)-1]
            current_value -= utxo.effective_value
            current_waste -= (utxo.fee - utxo.long_term_fee)
        # Moving forwards, continuing down this branch
        else:
            utxo = utxo_pool[len(current_selection)]
            current_available_value -= utxo.effective_value
            # Avoid searching a branch if the previous UTXO has the same value and
            # same waste and was excluded. Since the ratio of fee to long term fee
            # is the same, we only need to check if one of those values match in
            # order to know that the waste is the same
            if (
                len(current_selection) > 0
                and current_selection[-1] == False
                and utxo.effective_value == utxo_pool[len(current_selection) - 1].effective_value
                and utxo.fee == utxo_pool[len(current_selection) - 1].fee
            ):
                current_selection.append(False)
            else:
                # Inclusion branch first (Largest First Exploration)
                current_selection.append(True)
                current_value += utxo.effective_value
                current_waste += (utxo.fee - utxo.long_term_fee)

    # Check for solution
    if len(best_selection) == 0:
        return CoinSelection.algorithm_failure(params)

    # Set output set
    return CoinSelection.from_utxo_pool(params, params.utxo_pool, best_selection)
