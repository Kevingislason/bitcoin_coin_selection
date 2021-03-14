# bitcoin_coin_selection

Port of Bitcoin core coin selection logic to Python, prioritizing fidelity to the original and convenience. <br>
Classes / functions were named and organized per the original C++ code as far as was practicable.

# Installation

```pip install bitcoin_coin_selection```

# Usage
``select_coins`` is the main interface here. See the exmples folder for a step-by-step walkthrough. <br>

# Context

Bitcoin core coin selection logic:<br>
https://github.com/bitcoin/bitcoin/blob/master/src/wallet/coinselection.cpp<br>
https://github.com/bitcoin/bitcoin/blob/master/src/wallet/wallet.cpp<br><br>

Erhardt's thesis on coin selection<br>
https://murch.one/wp-content/uploads/2016/11/erhardt2016coinselection.pdf<br><br>

Explanation of the "OutputGroup" type (privacy enhancement)<br>
https://github.com/bitcoin/bitcoin/pull/12257<br>
