# Value of a single Bitcoin in satoshis
COIN: int = 100000000
CENT: int = COIN / 100
# Target minimum change amount
MIN_CHANGE: int = COIN / 100
# Final minimum change amount after paying for fees
MIN_FINAL_CHANGE: int = MIN_CHANGE/2
# Mam possible value in bitcoin
MAX_MONEY: int = 21000000 * COIN
