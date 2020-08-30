from typing import List

from selection_algorithms.branch_and_bound import select_coins_branch_and_bound
from selection_algorithms.knapsack_solver import select_coins_knapsack_solver
from selection_algorithms.single_random_draw import select_coins_single_random_draw
from selection_types.change_constants import MAX_MONEY
from selection_types.output_group import OutputGroup
from selection_types.coin_selection import (
    CoinSelection
)


def select_coins(utxo_pool: List[OutputGroup],
                 target_value: int,
                 short_term_fee_per_byte: int,
                 long_term_fee_per_byte: int,
                 change_output_size_in_bytes: int,
                 change_spend_size_in_bytes: int,
                 not_input_size_in_bytes: int
                 ) -> CoinSelection:

    # Validate target value isn't something silly
    if target_value == 0 or target_value > MAX_MONEY:
        return CoinSelection.invalid_spend()

    # Check for insufficient funds
    total_value = int(sum(
        [output_group.value for output_group in utxo_pool]))
    if total_value < target_value:
        return CoinSelection.insufficient_funds()

    # Calculate fees spending any given utxo would incur
    for outut_group in utxo_pool:
        outut_group.set_fee(short_term_fee_per_byte, long_term_fee_per_byte)
    # Calculate fee for the "fixed" part of a transaction
    fixed_fee = short_term_fee_per_byte * not_input_size_in_bytes
    target_after_fixed_fees = target_value + fixed_fee

    # Check for insufficient funds after fees
    total_effective_value = int(sum(
        [output_group.effective_value for output_group in utxo_pool]))
    if total_effective_value < target_after_fixed_fees:
        return CoinSelection.insufficient_funds_after_fees()

    # Calculate cost of change (input to branch and bound)
    cost_of_creating_change = short_term_fee_per_byte * change_output_size_in_bytes
    cost_of_spending_change = long_term_fee_per_byte * change_spend_size_in_bytes
    cost_of_change = cost_of_creating_change + cost_of_spending_change

    # Return branch and bound selection (more optimized) if possible
    bnb_selection = select_coins_branch_and_bound(
        utxo_pool, target_after_fixed_fees, cost_of_change)
    if bnb_selection.outcome == CoinSelection.Outcome.SUCCESS:
        return bnb_selection
    # Otherwise return knapsack_selection (less optimized) if possible
    else:
        knapsack_selection = select_coins_knapsack_solver(
            utxo_pool, target_after_fixed_fees
        )
        if knapsack_selection.outcome == CoinSelection.Outcome.SUCCESS:
            return knapsack_selection
        else:
            # If all else fails, return single random draw selection (not optomized) as a fallback
            return select_coins_single_random_draw(utxo_pool, target_after_fixed_fees)
