import random

from typing import List, Optional

from selection_types.change_constants import MIN_CHANGE
from selection_types.coin_selection import (
    CoinSelection
)
from selection_types.output_group import OutputGroup
from utils.check_for_insufficient_funds import check_for_insufficient_funds


def approximate_best_subset(utxo_pool: List[OutputGroup], actual_target: int,
                            total_lower: int, iterations=1000) -> CoinSelection:
    best_selection = [True for output_group in utxo_pool]
    best_value = total_lower

    for iteration_number in range(iterations):
        if best_value == actual_target:
            break
        included = [False for output_group in utxo_pool]
        total_value = 0
        reached_target = False
        number_of_passes = 2
        for pass_number in range(number_of_passes):
            if reached_target:
                break
            for i in range(len(utxo_pool)):
                # The solver here uses a randomized algorithm,
                # the randomness serves no real security purpose but is just
                # needed to prevent degenerate behavior and it is important
                # that the rng is fast. We do not use a constant random sequence,
                # because there may be some privacy improvement by making
                # the selection random.
                if (random.choice([True, False]) if pass_number == 0 else not included[i]):
                    total_value += utxo_pool[i].effective_value
                    included[i] = True
                    if total_value >= actual_target:
                        reached_target = True
                        if total_value < best_value:
                            best_value = total_value
                            best_selection = included.copy()
                        total_value -= utxo_pool[i].effective_value
                        included[i] = False

    return CoinSelection.from_utxo_pool(best_selection, utxo_pool)


def select_coins_knapsack_solver(
        utxo_pool: List[OutputGroup], target_value: int, not_input_fees: int) -> CoinSelection:

    actual_target = target_value + not_input_fees

    insufficient_funds = check_for_insufficient_funds(
        utxo_pool, target_value, not_input_fees)
    if insufficient_funds:
        return insufficient_funds

    # lowest output larger than actual_target
    lowest_larger: Optional[OutputGroup] = None
    applicable_groups: List[OutputGroup] = []
    total_lower = 0

    random.shuffle(utxo_pool)

    for output_group in utxo_pool:
        if output_group.effective_value == actual_target:
            return CoinSelection([output_group])

        elif output_group.effective_value < actual_target + MIN_CHANGE:
            applicable_groups.append(output_group)
            total_lower += output_group.effective_value

        elif not lowest_larger or output_group.effective_value < lowest_larger.effective_value:
            lowest_larger = output_group

    if total_lower == actual_target:
        return CoinSelection(applicable_groups)

    if total_lower < actual_target:
        return CoinSelection([lowest_larger])

    # Solve subset sum by stochastic approximation
    utxo_pool.sort(reverse=True)
    best_selection = approximate_best_subset(
        applicable_groups, actual_target, total_lower
    )
    if best_selection.effective_value != actual_target and total_lower >= actual_target + MIN_CHANGE:
        best_selection = approximate_best_subset(
            applicable_groups, actual_target + MIN_CHANGE, total_lower
        )
    # If we have a bigger coin and (either the stochastic approximation didn't find
    # a good solution, or the next bigger coin is closer), return the bigger coin
    if lowest_larger and (
        (
            best_selection.effective_value != actual_target
            and best_selection.effective_value < actual_target + MIN_CHANGE
        )
        or
        (
            lowest_larger.effective_value <= best_selection.effective_value
        )
    ):
        best_selection = CoinSelection([lowest_larger])

    return best_selection
