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
            outputs=None,
            from_me=True,
            value=0,
            depth=999,
            ancestor_count=0,
            descendant_count=0,
            effective_value=0,
            fee=0,
            long_term_fee=0
    ):
        if outputs:
            self.outputs = outputs
        else:
            self.outputs = []
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
        # ancestors here express the number of ancestors the new coin will end up having, which is
        # the sum, rather than the max; this will overestimate in the cases where multiple inputs
        # have common ancestors
        self.ancestor_count += ancestor_count
        # descendants is the count as seen from the top ancestor, not the descendants as seen from the
        # coin itself; thus, this value is counted as the max, not the sum
        self.descendant_count = max(self.descendant_count, descendant_count)
        self.effective_value = self.value

    # Insert all the input coins in the given group into this group
    def insert_group(self, output_group: "OutputGroup"):
        for output in output_group.outputs:
            self.insert(output,
                        output_group.depth,
                        output_group.from_me,
                        output_group.ancestor_count,
                        output_group.descendant_count
                        )
