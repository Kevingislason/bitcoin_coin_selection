from typing import List, Tuple
import math
import pytest

from bitcoin_coin_selection.selection_algorithms.knapsack_solver import select_coins_knapsack_solver
from bitcoin_coin_selection.tests.fixtures import generate_utxo_pool
from bitcoin_coin_selection.tests.coin_selection_params import TestParams
from bitcoin_coin_selection.selection_types.change_constants import CENT, COIN, MIN_CHANGE
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection


RUN_TESTS = 100


def test_knapsack_solver_single_coin_exact_match(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([1 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 1 * CENT)
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 1 * CENT
    assert selection.change_value == 0


def test_knapsack_solver_two_coins_exact_match(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([1 * CENT, 2 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 3 * CENT)
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 2
    assert selection.effective_value == 3 * CENT
    assert selection.change_value == 0


def test_knapsack_solver_large_pool_exact_match_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [6 * CENT, 7 * CENT, 8 * CENT, 20 * CENT, 30 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 71 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 5
    assert selection.effective_value == 71 * CENT
    assert selection.change_value == 0


def test_knapsack_solver_large_pool_insufficient_funds(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [6 * CENT, 7 * CENT, 8 * CENT, 20 * CENT, 30 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 72 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0
    assert selection.change_value == 0


def test_knapsack_solver_large_pool_single_large_coin_approx_match(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [6 * CENT, 7 * CENT, 8 * CENT, 20 * CENT, 30 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 16 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 20 * CENT
    assert selection.change_value == 4 * CENT


def test_knapsack_solver_large_pool_many_coins_approx_match(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [5 * CENT, 6 * CENT, 7 * CENT, 8 * CENT, 20 * CENT, 30 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 16 * CENT)
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 3
    assert selection.effective_value == 18 * CENT
    assert selection.change_value == 2 * CENT


def test_knapsack_solver_large_pool_single_large_coin_vs_many_coins_tie(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [5 * CENT, 6 * CENT, 7 * CENT, 8 * CENT, 18 * CENT, 20 * CENT, 30 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 16 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 18 * CENT
    assert selection.change_value == 2 * CENT


def test_knapsack_solver_large_pool_exact_match_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [5 * CENT, 6 * CENT, 7 * CENT, 8 * CENT, 18 * CENT, 20 * CENT, 30 * CENT])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 11 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 2
    assert selection.effective_value == 11 * CENT
    assert selection.change_value == 0


def test_knapsack_solver_smallest_larger_coin_used(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        5 * CENT,
        6 * CENT,
        7 * CENT,
        8 * CENT,
        18 * CENT,
        20 * CENT,
        30 * CENT,
        1 * COIN,
        2 * COIN,
        3 * COIN
    ])
    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 95 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 1 * COIN
    assert selection.change_value == 5 * CENT

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 195 * CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 2 * COIN
    assert selection.change_value == 5 * CENT


def test_knapsack_solver_avoids_small_change_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        CENT * 1 / 10,
        CENT * 2 / 10,
        CENT * 3 / 10,
        CENT * 4 / 10,
        CENT * 5 / 10
    ])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert selection.effective_value == CENT
    assert selection.change_value >= MIN_CHANGE or selection.change_value == 0


def test_knapsack_solver_avoids_small_change_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        CENT * 1 / 10,
        CENT * 2 / 10,
        CENT * 3 / 10,
        CENT * 4 / 10,
        CENT * 5 / 10,
        1111 * CENT
    ])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert selection.effective_value == CENT
    assert selection.change_value >= MIN_CHANGE or selection.change_value == 0


def test_knapsack_solver_avoids_small_change_3(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        CENT * 1 / 10,
        CENT * 2 / 10,
        CENT * 3 / 10,
        CENT * 4 / 10,
        CENT * 5 / 10,
        CENT * 6 / 10,
        CENT * 7 / 10,
        1111 * CENT
    ])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert selection.effective_value == CENT
    assert selection.change_value >= MIN_CHANGE or selection.change_value == 0


def test_knapsack_solver_avoids_small_change_4(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        CENT * 5 / 10,
        CENT * 6 / 10,
        CENT * 7 / 10,
        1111 * CENT
    ])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 1
    assert selection.effective_value == 1111 * CENT
    assert selection.change_value >= MIN_CHANGE or selection.change_value == 0


def test_knapsack_solver_avoids_small_change_5(generate_utxo_pool):

    utxo_pool = generate_utxo_pool([
        CENT * 4 / 10,
        CENT * 6 / 10,
        CENT * 8 / 10,
        1111 * CENT
    ])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, CENT)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 2
    assert selection.effective_value == MIN_CHANGE
    assert selection.change_value >= MIN_CHANGE or selection.change_value == 0



def test_knapsack_solver_avoids_small_change_6(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        CENT * 5 / 100,
        CENT,
        CENT * 100
    ])

    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, CENT * 9990 / 100)
    )
    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 2
    assert selection.effective_value == 101 * CENT
    assert selection.change_value >= MIN_CHANGE or selection.change_value == 0


# run the 'mtgox' test (see http://blockexplorer.com/tx/29a3efd3ef04f9153d47a990bd7b048a4b2d213daaa5fb8ed670fb85f13bdbcf)
# they tried to consolidate 10 50k coins into one 500k coin, and ended up with 50k in change


def test_knapsack_solver_mt_gox(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([50000 * COIN for i in range(20)])
    selection = select_coins_knapsack_solver(
        TestParams(utxo_pool, 500000 * COIN)
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) == 10
    assert selection.effective_value == 500000 * COIN
    assert selection.change_value == 0


def test_knapsack_solver_many_inputs(generate_utxo_pool):
    current_amount = 1500

    while current_amount < COIN:
        # Create 676 inputs (=  (old MAX_STANDARD_TX_SIZE == 100000)  / 148 bytes per input)
        MAX_INPUTS = 676
        utxo_pool = generate_utxo_pool(
            [current_amount for i in range(MAX_INPUTS)]
        )

        for i in range(100):
            selection = select_coins_knapsack_solver(
                TestParams(utxo_pool, 2000)
            )
            assert selection.outcome == CoinSelection.Outcome.SUCCESS
            if current_amount - 2000 < MIN_CHANGE:
                # needs more than one input
                return_size = math.ceil((2000.0 + MIN_CHANGE) / current_amount)
                return_value = current_amount * return_size
                assert len(selection.outputs) == return_size
                assert selection.effective_value == return_value
            else:
                # one input is sufficient
                assert selection.effective_value == current_amount
                assert len(selection.outputs) == 1

        current_amount *= 10


def test_knapsack_solver_randomness_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [COIN for i in range(100)])

    for i in range(RUN_TESTS):

        selection_1 = select_coins_knapsack_solver(
            TestParams(utxo_pool, 50 * COIN)
        )
        selection_2 = select_coins_knapsack_solver(
            TestParams(utxo_pool, 50 * COIN)
        )
        assert selection_1.outcome == selection_2.outcome == CoinSelection.Outcome.SUCCESS
        assert selection_1.effective_value == selection_1.effective_value == 50 * COIN
        assert set(selection_1.outputs) != set(selection_2.outputs)


def test_knapsack_solver_randomness_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool(
        [5 * CENT, 10 * CENT, 15 * CENT, 20 * CENT, 25 * CENT]
        + [COIN for i in range(1000)]
    )

    for i in range(RUN_TESTS):

        selection_1 = select_coins_knapsack_solver(
            TestParams(utxo_pool, 90 * CENT)
        )
        selection_2 = select_coins_knapsack_solver(
            TestParams(utxo_pool, 90 * CENT)
        )
        assert selection_1.outcome == selection_2.outcome == CoinSelection.Outcome.SUCCESS
        assert selection_1.effective_value == selection_1.effective_value == COIN
        assert set(selection_1.outputs) != set(selection_2.outputs)
