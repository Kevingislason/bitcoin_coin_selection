from typing import List, Tuple

import pytest

from bitcoin_coin_selection.selection_types.input_coin import InputCoin
from bitcoin_coin_selection.selection_types.output_group import OutputGroup


@pytest.fixture
def generate_utxo_pool():
    def _generate_utxo_pool(
        amounts: List[int],
        short_term_fee_per_byte: int = 0,
        long_term_fee_per_byte: int = 0
    ) -> List[OutputGroup]:
        utxo_pool: List[OutputGroup] = []
        for amount in amounts:
            input_coin = InputCoin(
                tx_hash="",
                vout=0,
                value=int(amount),
                input_bytes=100
            )
            fake_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
            output_group = OutputGroup(fake_address, [input_coin])
            output_group.set_fee(short_term_fee_per_byte,
                                 long_term_fee_per_byte)
            utxo_pool.append(output_group)
        return utxo_pool
    return _generate_utxo_pool


@pytest.fixture
def make_hard_case(generate_utxo_pool):
    def _make_hard_case(utxo_count: int) -> Tuple[int, List[OutputGroup]]:
        target_value = 0
        utxo_amounts: List[int] = []

        for i in range(utxo_count):
            target_value += 1 << (utxo_count + i)
            utxo_amount_1 = 1 << (utxo_count + i)
            utxo_amount_2 = (1 << (utxo_count + i)) + (1 << (utxo_count-1-i))
            utxo_amounts.append(utxo_amount_1)
            utxo_amounts.append(utxo_amount_2)

        utxo_pool = generate_utxo_pool(utxo_amounts)
        return (target_value, utxo_pool)

    return _make_hard_case


