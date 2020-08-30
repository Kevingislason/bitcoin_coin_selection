from typing import List
from selection_types.input_coin import InputCoin

# See https://github.com/bitcoin/bitcoin/pull/12257
"""
Each output group corresponds to all outputs with the same destination
It is a privacy improvement, as each time you spend some output, any other
output that is publicly associated with the destination (address) will also be
spent at the same time, at the cost of fee increase for cases where coin
select without group restriction would find a more optimal set of coins
"""


class OutputGroup():
    outputs: List[InputCoin]
    value: int
    effective_value: int
    fee: int
    long_term_fee: int

    def __init__(self, outputs=None):
        self.effective_value = None
        self.fee = None
        self.long_term_fee = None
        self.value = 0
        self.outputs = []
        if outputs:
            for output in outputs:
                self.insert(output)

    def __gt__(self, output_group_2):
        return self.effective_value > output_group_2.effective_value

    def set_fee(self, short_term_fee_per_byte, long_term_fee_per_byte):
        self.effective_value = 0
        self.fee = 0
        self.long_term_fee = 0

        non_negative_ev_outputs = []
        for output in self.outputs:
            output.set_fee(short_term_fee_per_byte, long_term_fee_per_byte)
            # Filter outputs with negative effective values
            if output.effective_value > 0:
                self.fee += output.fee
                self.long_term_fee += output.long_term_fee
                self.effective_value += output.effective_value
                non_negative_ev_outputs.append(output)

    def insert(self, output: InputCoin):
        self.outputs.append(output)
        self.value += output.value
