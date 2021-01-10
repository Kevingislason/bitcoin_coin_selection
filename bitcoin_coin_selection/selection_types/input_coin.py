class InputCoin():
    tx_hash: str
    vout: int
    value: int
    input_bytes: int
    effective_value: int
    fee: int
    long_term_fee: int
    address: str

    def __init__(self, tx_hash: str, vout: int, value: int, input_bytes: int):
        self.tx_hash = tx_hash
        self.vout = vout
        self.value = value
        self.input_bytes = input_bytes

    def set_fee(self, short_term_fee_per_byte: int, long_term_fee_per_byte: int):
        self.fee = self.input_bytes * short_term_fee_per_byte
        self.long_term_fee = self.input_bytes * long_term_fee_per_byte
        self.effective_value = self.value - self.fee
