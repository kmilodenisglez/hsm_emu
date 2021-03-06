
# hsm_emu
`hsm_emu` is an example in Python3 that handles some Bitcoin functionalities in a simple way. Using libraries like (btcpy, bitcoinlib, ecdsa, cryptography and webpy).

**is a work in progress**

Table of Contents
=================

 * [hsm_emu](#hsm_emu)
 * [Requirements](#requirements)
 * [Structure](#structure)
 * [Libraries](#libraries)
 * [Start-the-server](start_server)
 * [Bitcoin-regtest-box](#bitcoin-regtest-box)
 * [TODO](#todo)

## Requirements
The strict requirements of this library are:

You must have bitcoind and bitcoin-cli installed on your system <a href="https://bitcoin.org/en/bitcoin-core/">bitcoin-core</a> v0.15.1 and Python 3.5.

    ```
	sudo apt-get install libssl-dev
	pip3 install cryptography
    ```	
		
all other dependencies are included in [`libraries`]:

## Structure

- **server/web.py**: [`server/web.py`](server/web.py)(app web utilizando <a href="http://webpy.org">webpy</a>)
- **Makefile**: [`Makefile`](Makefile)(Create your own private bitcoin regtest already preconfigured with 2 nodes, the 2nd node connected to the 1st; see more at #bitcoin-regtest-box).
- **libraries/authentication.py**: [`libraries/authentication.py`](libraries/authentication.py)(Challenge-response authentication [SLIP-0013: Authentication using deterministic hierarchy](https://github.com/satoshilabs/slips/blob/master/slip-0013.md).)
- **libraries/utils_wallets.py**: [`libraries/utils_wallets.py`](libraries/utils_wallets.py)(Several functionalities implemented [bip32KeyInfoFromKey, getXPubKey, derive, customPathDerivation, signMessage, verifyMessage, secret, cipherKeyValue, decipherKeyValue, generatePrivateMasterKey, raw_transaction, ...])
- **libraries/utils_transactions.py**: [`libraries/utils_transactions.py`](libraries/utils_wallets.py)(Several functionalities implemented [composeTx, createSignPushTransaction, validAmount])
- **libraries/request_payment.py**:[`libraries/request_payment.py`](libraries/request_payment.py)


## Libraries
- **libraries/utils_wallets.py**: [`libraries/utils_wallets.py`](libraries/utils_wallets.py):

```python
Derive a key, method which takes as input:

key: key
path: a string representing a path

example:
	derive('tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX', "m/0'/0'/276'")

def derive(key, path):
	try:
		extendedKey = ExtendedKey.decode(key, check_network=False)
		return extendedKey.derive(path)
	except Exception as e:
		raise e
```


## Start-the-server
If you go to your command line and type:

```
$ python3 web.py
```

http://0.0.0.0:8080/
You now have your web.py application running a real web server on your computer. Visit that URL (You can add an IP address/port after the "web.py" bit to control where web.py launches the server.

Note: You can specify the port number to use on the command line like this if you can't or don't want to use the default:

```
$ python3 web.py 9000
```

## Bitcoin-regtest-box
It is a fork of <a href="https://github.com/freewil/bitcoin-testnet-box">bitcoin-testnet-box</a> with some improvements and other commands included.

This will start up two nodes using the two datadirs `node_0` and `node_1`. They
will only connect to each other in order to remain an isolated private testnet.
Two nodes are provided, as one is used to generate blocks and it's balance
will be increased as this occurs (imitating a miner). You may want a second node
where this behavior is not observed.

Node `node_0` will listen on port `19000`, allowing node `node_1` to connect to it.

Node `node_0` will listen on port `19001` and node `node_1` will listen on port `19011`
for the JSON-RPC server.


```
$ cd hsm_emu/
$ make start
$ make generate-start
```

We start bitcore-core daemon in regtest mode and JSON-RPC in http://admin1:123@localhost:19001, with user (admin1) and password (123).

## TODO
Since this example is still a work in progress, the following roadmap lists the improvements that must be made:
* Add view for [Get account info]
* Add test for sendtransaction, signrawtransaction and other functionalities already implemented in the libraries.
