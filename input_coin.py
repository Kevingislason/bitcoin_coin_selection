class InputCoin():
    tx_hash: str
    vout: int
    effective_value: int
    # Pre-computed estimated size of this output as a fully-signed input in a transaction.
    # Can be -1 if it could not be calculated (???)
    input_bytes: int

    # todo: I think I need either txout or txout size to calculate input bytes

    def __init__(self, tx_hash, vout, effective_value, input_bytes=-1):
        self.tx_hash = tx_hash
        self.vout = vout
        self.effective_value = effective_value
        self.input_bytes = input_bytes
