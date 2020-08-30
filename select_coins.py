from selection_algorithms.branch_and_bound import select_coins_branch_and_bound
from selection_algorithms.knapsack_solver import select_coins_knapsack_solver
from selection_types.output_group import OutputGroup
from selection_types.coin_selection import (
    CoinSelection
)


def select_coins(utxo_pool: List[OutputGroup],
                 target_value: int,
                 short_term_fee_per_byte: int,
                 long_term_fee_per_byte: int,
                 change_output_size_in_bytes: int,
                 change_input_size_in_bytes: int,
                 not_input_size_in_bytes: int
                 ) -> SelectionResult:

    # Calculate fees spending any given utxo would incur
    for outut_group in utxo_pool:
        outut_group.set_fees(short_term_fee_per_byte)
    # Calculate fee that the "fixed" part of a transaction incurs
    fixed_fee = short_term_fee_per_byte * not_input_size_in_bytes
    target_after_fixed_fees = target_value + fixed_fee

    # Check for insufficient funds
    total_value = sum(
        [output_group.value for output_group in utxo_pool])
    total_effective_value = sum(
        [output_group.value for output_group in utxo_pool])
    if total_value < target_value:
        return CoinSelection.insufficient_funds()
    elif total_effective_value < target_after_fixed_fees:
        return CoinSelection.insufficient_funds_after_fees()

    # Calculate cost of change
    cost_of_creating_change = short_term_fee_per_byte * change_output_size_in_bytes
    cost_of_spending_change = long_term_fee_per_byte * change_input_size_in_bytes
    cost_of_change = cost_of_creating_change + cost_of_spending_change

    # Return branch and bound selection if possible (more optimized)
    bnb_selection = select_coins_branch_and_bound(
        utxo_pool, target_after_fixed_fees, cost_of_change)
    if bnb_selection.outcome == CoinSelection.Outcomes.SUCCESS:
        return bnb_selection

    # Otherwise return knapsack_selection (less optimized)
    else:
        return select_coins_knapsack_solver(
            outut_group, target_after_fixed_fees
        )
