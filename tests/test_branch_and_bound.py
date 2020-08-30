from typing import List

import pytest

from selection_algorithms.branch_and_bound import select_coins_branch_and_bound
from selection_types.change_constants import CENT
from selection_types.coin_selection import CoinSelection
from selection_types.input_coin import InputCoin
from selection_types.output_group import OutputGroup
from tests.fixtures import generate_utxo_pool, make_hard_case

# todo: run tests with retries and repeats
# todo: test cases for non-zero npon-input fees

# How many times to run all the tests to have a chance to catch errors
# that only show up with particular random shuffles
RUN_TESTS = 100
# Some tests fail 1% of the time due to bad luck.
# We repeat those tests this many times and only complain if all iterations of the test fail
RANDOM_REPEATS = 5

DEFAULT_NOT_INPUT_FEES = 0


@pytest.mark.parametrize("target_amount", [1 * CENT, 2 * CENT, 3 * CENT, 4 * CENT])
def test_branch_and_bound_exact_match_single_coin(generate_utxo_pool, target_amount):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])

    selection = select_coins_branch_and_bound(
        utxo_pool, target_amount, 0.5 * CENT)

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == target_amount


def test_branch_and_bound_insufficient_funds(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])

    selection = select_coins_branch_and_bound(
        utxo_pool, 11 * CENT, 0.5 * CENT)

    assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


# Cost of change is greater than the difference between target value and utxo sum
def test_branch_and_bound_expensive_change(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])

    selection = select_coins_branch_and_bound(
        utxo_pool, 0.9 * CENT, 0.5 * CENT)

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 1 * CENT


# Cost of change is less than the difference between target value and utxo sum
def test_branch_and_bound_cheap_change_failure(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])

    selection = select_coins_branch_and_bound(
        utxo_pool, 0.9 * CENT, 0)
    assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


def test_branch_and_bound_exact_match_multiple_coins(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
        5 * CENT
    ])

    selection = select_coins_branch_and_bound(
        utxo_pool, 10 * CENT, 0.5 * CENT)
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 3
    assert selection.effective_value == 10 * CENT

    selected_amounts = [
        output.effective_value for output in selection.outputs]
    selected_amounts.sort()

    assert selected_amounts[0] == 1 * CENT
    assert selected_amounts[1] == 4 * CENT
    assert selected_amounts[2] == 5 * CENT


def test_branch_and_bound_failure_no_match(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
        5 * CENT
    ])

    selection = select_coins_branch_and_bound(
        utxo_pool, 0.25 * CENT, 0.5 * CENT)
    assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


def test_branch_and_bound_iteration_exhaustion(make_hard_case):
    target_value, utxo_pool = make_hard_case(17)
    selection = select_coins_branch_and_bound(
        utxo_pool, target_value, 0)
    assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
    assert len(selection.outputs) == 0

    target_value, utxo_pool = make_hard_case(14)
    selection = select_coins_branch_and_bound(
        utxo_pool, target_value, 0)
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) > 0


def test_branch_and_bound_early_bailout_optimization(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [2 * CENT,
         7 * CENT,
         7 * CENT,
         7 * CENT,
         7 * CENT] +
        [5 * CENT for i in range(50000)]
    )
    selection = select_coins_branch_and_bound(
        utxo_pool, 30 * CENT, 5000)
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 5
    assert selection.effective_value == 30 * CENT


def test_branch_and_bound_consistently_fails_impossible_case(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [i * CENT for i in range(5, 21)]
    )
    for i in range(100):
        selection = select_coins_branch_and_bound(
            utxo_pool, 1 * CENT, 2 * CENT)
        assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
        assert len(selection.outputs) == 0
        assert selection.effective_value == 0
