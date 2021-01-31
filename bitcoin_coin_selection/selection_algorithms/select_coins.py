from typing import List

from bitcoin_coin_selection.selection_algorithms.branch_and_bound import select_coins_branch_and_bound
from bitcoin_coin_selection.selection_algorithms.knapsack_solver import select_coins_knapsack_solver
from bitcoin_coin_selection.selection_algorithms.single_random_draw import select_coins_single_random_draw
from bitcoin_coin_selection.selection_types.change_constants import MAX_MONEY
from bitcoin_coin_selection.selection_types.coin_selection import (
    CoinSelection
)
from bitcoin_coin_selection.selection_types.coin_selection_params import (
    CoinSelectionParams
)


def select_coins(params: CoinSelectionParams) -> CoinSelection:

    # Validate target value isn't something silly
    if params.target_value == 0 or params.target_value > MAX_MONEY:
        return CoinSelection.invalid_spend(params)

    # Check for insufficient funds
    if params.total_value < params.target_value:
        return CoinSelection.insufficient_funds(params)

    if params.total_effective_value < params.target_value + params.fixed_fee:
        return CoinSelection.insufficient_funds_after_fees(params)

    # Return branch and bound selection (more optimized) if possible
    bnb_selection = select_coins_branch_and_bound(params)
    if bnb_selection.outcome == CoinSelection.Outcome.SUCCESS:
        return bnb_selection
    # Otherwise return knapsack_selection (less optimized) if possible
    else:
        knapsack_selection = select_coins_knapsack_solver(params)
        if knapsack_selection.outcome == CoinSelection.Outcome.SUCCESS:
            return knapsack_selection
        else:
            # If all else fails, return single random draw selection (not optomized) as a fallback
            return select_coins_single_random_draw(params)
