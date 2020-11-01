from typing import List, Tuple
import pytest

from selection_algorithms.select_coins import select_coins
from tests.fixtures import generate_utxo_pool
from selection_types.coin_selection import CoinSelection
from selection_types.change_constants import CENT, COIN, MIN_CHANGE


def test_insufficient_funds_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])
    selection = select_coins(utxo_pool, 11 * CENT, 0, 0, 0, 0, 0)
    assert selection.outcome == CoinSelection.Outcome.INSUFFICIENT_FUNDS
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


def test_insufficient_funds_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([])
    selection = select_coins(utxo_pool, 1,  0, 0, 0, 0, 0)
    assert selection.outcome == CoinSelection.Outcome.INSUFFICIENT_FUNDS
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


def test_insufficient_funds_after_fees(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        10 * CENT
    ])
    selection = select_coins(
        utxo_pool=utxo_pool,
        target_value=10 * CENT,
        short_term_fee_per_byte=100,
        long_term_fee_per_byte=100,
        change_spend_size_in_bytes=100,
        change_output_size_in_bytes=100,
        not_input_size_in_bytes=100,
    )
    assert selection.outcome == CoinSelection.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


def test_invalid_spend(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])
    selection = select_coins(utxo_pool, 0,  0, 0, 0, 0, 0)

    assert selection.outcome == CoinSelection.Outcome.INVALID_SPEND
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0


def test_success(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])
    selection = select_coins(
        utxo_pool=utxo_pool,
        target_value=5 * CENT,
        short_term_fee_per_byte=100,
        long_term_fee_per_byte=100,
        change_spend_size_in_bytes=100,
        change_output_size_in_bytes=100,
        not_input_size_in_bytes=100,
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) > 0
    assert selection.effective_value >= 5 * CENT
