from typing import List
import pytest
import json

from bitcoin_coin_selection.selection_algorithms.select_coins import (
  select_coins
)
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from bitcoin_coin_selection.selection_types.coin_selection_params import CoinSelectionParams
from bitcoin_coin_selection.selection_types.output_group import OutputGroup
from bitcoin_coin_selection.selection_types.input_coin import InputCoin
import requests


# 0. Gather Utxos you want to spend, and addresses you want to spend from
class YourUTXOClass():
    value: int
    tx_hash: str
    vout: int

    def __init__(self, value: int, tx_hash: str, vout: int):
        self.value = value
        self.tx_hash = tx_hash
        self.vout = vout

class YourAddressClass():
    _address: str
    utxos: List[YourUTXOClass]

    def __init__(self, address: str, utxos: List[YourUTXOClass] = None):
        self._address = address
        if not utxos:
          utxos = []
        else:
          self.utxos = utxos

    def __str__(self):
      return self._address

    # i.e. "virtual bytes" required to spend a utxo you own from this address
    # see https://bitcoin.stackexchange.com/questions/89385/is-there-a-difference-between-bytes-and-virtual-bytes-vbytes
    def get_spend_size_in_bytes(self):
        DUMMY_SPEND_SIZE = 100
        return DUMMY_SPEND_SIZE

    # i.e. "virtual bytes" required to output a new utxo to this address
    def get_output_size_in_bytes(self):
        DUMMY_OUTPUT_SIZE = 100
        return DUMMY_OUTPUT_SIZE

sender_utxos = [
  YourUTXOClass(
    100000,
    "340ad7bcf7dfc408fda32e2251fcb7fcbcf022b24daa6cbf11f202170f7748c2",
    0
  ),
  YourUTXOClass(
    200000,
    "abdfeabc232a5273545bef856f2edbafd1affbb22d1f8056c150f533426c0b7e",
    0
  ),
  YourUTXOClass(
    300000,
    "f25e6fca6236c34ea6eec7ead11e669255bd7a003a1d04463dd81a0eb2cd84df",
    1
  ),

]
sender_addresses = [
  YourAddressClass("n4VQ5YdHf7hLQ2gWQYYrcxoE5B7nWuDFNF", sender_utxos[:1]),
  YourAddressClass("2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm", sender_utxos[1:3]),
]


# 1. Depending on what your app-specific classes look like, you'll want to define something like:
def map_addresses_to_output_groups(addresses: List[YourAddressClass]) -> List[OutputGroup]:
    output_groups = []
    for address in sender_addresses:
        if address.utxos:
            input_coins = [
                InputCoin (
                    utxo.tx_hash,
                    utxo.vout,
                    utxo.value,
                    address.get_spend_size_in_bytes()
                )
                for utxo in address.utxos
            ]
            output_groups.append(OutputGroup(str(address), input_coins))
    return output_groups

utxo_pool = map_addresses_to_output_groups(sender_addresses)


# 2 Gather some peripheral data required for coin selection

# 2.1.1 Get base transaction size independent of inputs and outputs
# For most simple transactions this will always be 10 bytes
# i.e. Version (4b) + TxOut count (1b) + TxIn count (1b) + Lock time (4b)
tx_base_bytes = 10

# 2.1.2 Get the bytes required to spend to the given recipient's address(es)
# This will vary based on the recipient's address type(s) (P2PKH, native Segwit, etc.)
# See also: https://bitcoin.stackexchange.com/questions/1195/how-to-calculate-transaction-size-before-sending-legacy-non-segwit-p2pkh-p2sh
recipient_address = YourAddressClass("n4VQ5YdHf7hLQ2gWQYYrcxoE5B7nWuDFNF")
tx_output_bytes = recipient_address.get_output_size_in_bytes()

# 2.1.3 Sum the two to get total tx size not including inputs or change outputs (which we don't know yet in any case)
# i.e. "not_input_size_in_bytes"
not_input_size_in_bytes = tx_base_bytes + tx_output_bytes


# 2.2 Get the bytes required to make and spend change (similar to 2.1.2)
# This will vary based on the sender's change address type (P2PKH, native Segwit, etc.)
sender_change_address = YourAddressClass("mtXWDB6k5yC5v7TcwKZHB89SUp85yCKshy")
change_output_size_in_bytes = sender_change_address.get_output_size_in_bytes()
change_spend_size_in_bytes = sender_change_address.get_spend_size_in_bytes()

# 2.3 Get fee rate information

# 2.3.1 Get the current fee rate per byte
# There are a lot of public APIs for this, offering different levels of configurability
# See https://b10c.me/blog/003-a-list-of-public-bitcoin-feerate-estimation-apis/

def get_short_term_fee_rate(is_priority: bool):
    response = requests.get("https://api.blockchain.info/mempool/fees")
    if response.status_code != 200:
        raise Exception("Network error getting fee rate")
    if is_priority:
        return json.loads(response.text)["priority"]
    else:
        return json.loads(response.text)["regular"]

short_term_fee_per_byte = get_short_term_fee_rate(False)

# 2.3.2 Get long term fee rate per byte
# Sadly, I haven't found any public API's exposing this information
# If you find one or make one yourself, let me know! Would be a cool project.
# Otherwise, it's reasonable to come up with some heuristic method for your app
# Lacking better options, it's okay to use short_term_fee_per_byte,
# though this will cause inefficiencies when short_term_fees are anomalously low or high
long_term_fee_per_byte = short_term_fee_per_byte


# 3 At this point we are ready to select coins; suppose we want to spend 150000 satoshis
target_value = 150000
coin_selection = select_coins(
  CoinSelectionParams(
    utxo_pool,
    target_value,
    short_term_fee_per_byte,
    long_term_fee_per_byte,
    change_output_size_in_bytes,
    change_spend_size_in_bytes,
    not_input_size_in_bytes
  )
)


# 4 Based on the CoinSelection.Outcome, you can raise different exceptions
# or surface different error text to your UI or whatever
if coin_selection.outcome != CoinSelection.Outcome.SUCCESS:
  raise Exception("Coin selection failed")


# 5 Map the coin selection back to your app-specifc class, e.g.
def map_coin_selection_to_utxos(coin_selection: CoinSelection, utxo_pool: List[YourUTXOClass]) -> List[YourUTXOClass]:
    selected_utxos = []
    for selected_coin in coin_selection.outputs:
        selected_utxo = next(
          utxo for utxo in utxo_pool
          if utxo.tx_hash == selected_coin.tx_hash and utxo.vout == selected_coin.vout
        )
        selected_utxos.append(selected_utxo)
    return selected_utxos

selected_utxos = map_coin_selection_to_utxos(coin_selection, sender_utxos)


# 6 Assemble the transaction--your problem :)
change_value = coin_selection.change_value

def assemble_transaction(
  selected_utxos: List[YourUTXOClass],
  recipient_address: YourAddressClass,
  send_value: int,
  change_value: int # You will want to pass this in for its convenient
):
  if change_value > 0:
    # make 1 primary output and 1 change output
    # rest assured that the selection algorithm avoids creating dust
    return
  else:
    # make only 1 primary output, no change output
    return

transaction = assemble_transaction(
  selected_utxos,
  recipient_address,
  target_value,
  change_value
)
