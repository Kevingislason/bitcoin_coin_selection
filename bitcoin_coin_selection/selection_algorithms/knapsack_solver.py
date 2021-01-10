import random

from typing import List, Optional

from bitcoin_coin_selection.selection_types.change_constants import MIN_CHANGE
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection

from bitcoin_coin_selection.selection_types.output_group import OutputGroup


DEFAULT_ITERATIONS = 1000


def approximate_best_subset(utxo_pool: List[OutputGroup],
                            target_value: int,
                            total_lower: int,
                            iterations: int,
                            adjust_for_min_change: int = False
    ) -> CoinSelection:

    original_target_value = target_value
    if adjust_for_min_change:
        target_value += MIN_CHANGE

    best_selection = [True for output_group in utxo_pool]
    best_value = total_lower

    for iteration_number in range(iterations):
        if best_value == target_value:
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
                    if total_value >= target_value:
                        reached_target = True
                        if total_value < best_value:
                            best_value = total_value
                            best_selection = included.copy()
                        total_value -= utxo_pool[i].effective_value
                        included[i] = False

    if reached_target:
        return CoinSelection.from_utxo_pool(
            original_target_value, best_selection, utxo_pool
        )
    else:
        return CoinSelection.algorithm_failure(original_target_value)


def select_coins_knapsack_solver(
        utxo_pool: List[OutputGroup], target_value: int,
        iterations=DEFAULT_ITERATIONS) -> CoinSelection:

    # lowest output group larger than target_value
    lowest_larger: Optional[OutputGroup] = None
    applicable_groups: List[OutputGroup] = []
    total_lower = 0

    random.shuffle(utxo_pool)

    for output_group in utxo_pool:
        if output_group.effective_value == target_value:
            return CoinSelection(target_value, [output_group])

        elif output_group.effective_value < target_value + MIN_CHANGE:
            applicable_groups.append(output_group)
            total_lower += output_group.effective_value

        elif not lowest_larger or output_group.effective_value < lowest_larger.effective_value:
            lowest_larger = output_group

    if total_lower == target_value:
        return CoinSelection(target_value, applicable_groups)

    if total_lower < target_value and lowest_larger:
        return CoinSelection(target_value, [lowest_larger])

    # Solve subset sum by stochastic approximation
    utxo_pool.sort(reverse=True)
    best_selection = approximate_best_subset(
        applicable_groups, target_value, total_lower, iterations
    )
    if best_selection.effective_value != target_value and total_lower >= target_value + MIN_CHANGE:
        best_selection = approximate_best_subset(
            applicable_groups,
            target_value,
            total_lower,
            iterations,
            adjust_for_min_change=True
        )
    # If we have a bigger coin and (either the stochastic approximation didn't find
    # a good solution, or the next bigger coin is closer), return the bigger coin
    if lowest_larger and (
        (
            best_selection.effective_value != target_value
            and best_selection.effective_value < target_value + MIN_CHANGE
        )
        or
        (
            lowest_larger.effective_value <= best_selection.effective_value
        )
    ):
        best_selection = CoinSelection(target_value, [lowest_larger])

    return best_selection
