from typing import List, Tuple
import pytest

from bitcoin_coin_selection.selection_algorithms.select_coins import select_coins
from bitcoin_coin_selection.tests.fixtures import generate_utxo_pool
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from bitcoin_coin_selection.selection_types.coin_selection_params import CoinSelectionParams
from bitcoin_coin_selection.selection_types.change_constants import CENT, COIN, MIN_CHANGE


def test_insufficient_funds_1(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])
    selection = select_coins(CoinSelectionParams(utxo_pool, 11 * CENT, 0, 0, 0, 0, 0))
    assert selection.outcome == CoinSelection.Outcome.INSUFFICIENT_FUNDS
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0
    assert selection.change_value == 0


def test_insufficient_funds_2(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([])
    selection = select_coins(CoinSelectionParams(utxo_pool, 1,  0, 0, 0, 0, 0))
    assert selection.outcome == CoinSelection.Outcome.INSUFFICIENT_FUNDS
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0
    assert selection.change_value == 0


def test_insufficient_funds_after_fees(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        10 * CENT
    ])
    selection = select_coins(
        CoinSelectionParams(
            utxo_pool=utxo_pool,
            target_value=10 * CENT,
            short_term_fee_per_byte=100,
            long_term_fee_per_byte=100,
            change_spend_size_in_bytes=100,
            change_output_size_in_bytes=100,
            not_input_size_in_bytes=100,
        )
    )
    assert selection.outcome == CoinSelection.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0
    assert selection.change_value == 0


def test_invalid_spend(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])
    selection = select_coins(CoinSelectionParams(utxo_pool, 0,  0, 0, 0, 0, 0))

    assert selection.outcome == CoinSelection.Outcome.INVALID_SPEND
    assert len(selection.outputs) == 0
    assert selection.effective_value == 0
    assert selection.change_value == 0


def test_success(generate_utxo_pool):
    utxo_pool = generate_utxo_pool([
        1 * CENT,
        2 * CENT,
        3 * CENT,
        4 * CENT,
    ])
    selection = select_coins(
        CoinSelectionParams(
            utxo_pool=utxo_pool,
            target_value=5 * CENT,
            short_term_fee_per_byte=100,
            long_term_fee_per_byte=100,
            change_spend_size_in_bytes=100,
            change_output_size_in_bytes=100,
            not_input_size_in_bytes=100
        )
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert len(selection.outputs) > 0
    assert selection.effective_value >= 5 * CENT
    assert selection.change_value > 0


def test_does_not_make_dust_change(generate_utxo_pool):
    short_term_fee_per_byte = 100
    long_term_fee_per_byte = 100
    utxo_pool = generate_utxo_pool(
        [1 * CENT],
        short_term_fee_per_byte,
        long_term_fee_per_byte
    )
    not_input_size_in_bytes = 100
    fixed_fee = short_term_fee_per_byte * not_input_size_in_bytes
    total_effective_value = sum(output_group.effective_value for output_group in utxo_pool)

    selection = select_coins(
        CoinSelectionParams(
            utxo_pool=utxo_pool,
            target_value=total_effective_value - fixed_fee - 1,
            short_term_fee_per_byte=short_term_fee_per_byte,
            long_term_fee_per_byte=long_term_fee_per_byte,
            change_spend_size_in_bytes=100,
            change_output_size_in_bytes=100,
            not_input_size_in_bytes=not_input_size_in_bytes
        )
    )

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert selection.change_value == 0


def test_makes_slightly_larger_than_dust_change(generate_utxo_pool):
    short_term_fee_per_byte = 100
    long_term_fee_per_byte = 100
    change_output_size_in_bytes = 100
    change_spend_size_in_bytes = 100

    utxo_pool = generate_utxo_pool(
        [1 * CENT],
        short_term_fee_per_byte,
        long_term_fee_per_byte
    )

    not_input_size_in_bytes = 100
    fixed_fee = short_term_fee_per_byte * not_input_size_in_bytes
    cost_of_creating_change = short_term_fee_per_byte * change_output_size_in_bytes
    cost_of_spending_change = long_term_fee_per_byte * change_spend_size_in_bytes
    cost_of_change = cost_of_creating_change + cost_of_spending_change


    total_effective_value = sum(output_group.effective_value for output_group in utxo_pool)
    params = CoinSelectionParams(
        utxo_pool=utxo_pool,
        target_value=total_effective_value - fixed_fee - cost_of_change - 1,
        short_term_fee_per_byte=short_term_fee_per_byte,
        long_term_fee_per_byte=long_term_fee_per_byte,
        change_spend_size_in_bytes=100,
        change_output_size_in_bytes=100,
        not_input_size_in_bytes=not_input_size_in_bytes
    )

    selection = select_coins(params)

    assert selection.outcome == CoinSelection.Outcome.SUCCESS
    assert selection.change_value == params.cost_of_change + params.fixed_fee + 1

