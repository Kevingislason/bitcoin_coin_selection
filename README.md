# bitcoin_utxo_selection

Port of Bitcoin core UTXO selection algorithms (Branch and Bound, Knapsack) to Python <br>
See:<br>
https://github.com/bitcoin/bitcoin/blob/master/src/wallet/coinselection.cpp<br>
https://murch.one/wp-content/uploads/2016/11/erhardt2016coinselection.pdf

# Things I'm not implementing

-Coin eligibility filter<br>
-Any checks that the inputs to the UTXO selection algorithm are real or valid<br>
