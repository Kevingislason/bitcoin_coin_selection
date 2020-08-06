from typing import List

from input_coin import InputCoin


class OutputGroup():
    outputs: List[InputCoin]
    from_me: bool
    value: int
    depth: int
    ancestor_count: int
    descendant_count: int
    effective_value: int
    fee: int
    long_term_fee: int

    def __init__(
            self,
            outputs=[],
            from_me=True,
            value=0,
            depth=999,
            ancestor_count=0,
            descendant_count=0,
            effective_value=0,
            fee=0,
            long_term_fee=0
    ):
        self.outputs = outputs
        self.from_me = from_me
        self.value = value
        self.depth = depth
        self.ancestor_count = ancestor_count
        self.descendant_count = descendant_count
        self.effective_value = effective_value
        self.fee = fee
        self.long_term_fee = long_term_fee

    def __gt__(self, output_group_2):
        return self.effective_value > output_group_2.effective_value

    def insert(self, output: InputCoin, depth: int, from_me: bool, ancestor_count: int, descendant_count: int):
        self.outputs.append(output)
        self.from_me &= from_me
        self.value += output.effective_value
        self.depth = min(self.depth, depth)
        self.ancestor_count += ancestor_count
        self.descendant_count = max(self.descendant_count, descendant_count)
        self.effective_value = self.value
