from typing import List
import pytest

from bitcoin_coin_selection.selection_algorithms.single_random_draw import select_coins_single_random_draw
from bitcoin_coin_selection.tests.fixtures import generate_utxo_pool
from bitcoin_coin_selection.tests.coin_selection_params import TestParams
from bitcoin_coin_selection.selection_types.change_constants import CENT
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection


RUN_TESTS = 100


def test_single_random_draw_failure_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([i * CENT for i in range(100)])
    for i in range(RUN_TESTS):
        selection = select_coins_single_random_draw(
            TestParams(utxo_pool, 100000 * CENT)
        )
        assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
        assert selection.effective_value == 0
        assert selection.change_value == 0


def test_single_random_draw_failure_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([])
    selection = select_coins_single_random_draw(
        TestParams(utxo_pool, 1)
    )
    assert selection.outcome == CoinSelection.Outcome.ALGORITHM_FAILURE
    assert selection.effective_value == 0
    assert selection.change_value == 0


def test_single_random_draw_success_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([i * CENT for i in range(100)])
    for i in range(RUN_TESTS):
        selection = select_coins_single_random_draw(
            TestParams(utxo_pool, 150 * CENT)
        )

        assert selection.outcome == CoinSelection.Outcome.SUCCESS
        assert selection.effective_value >= 150 * CENT


def test_single_random_draw_success_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([1 * CENT])
    selection = select_coins_single_random_draw(
        TestParams(utxo_pool, 1 * CENT)
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert selection.effective_value == 1 * CENT
    assert selection.change_value == 0
