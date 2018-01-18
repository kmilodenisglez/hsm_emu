#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from btcpy.setup import setup
from btcpy.structs.transaction import Transaction
from bitcoin import SelectParams
from bitcoin.core import COIN
from bitcoin.wallet import CBitcoinAddress
from bitcoin.base58 import Base58ChecksumError

from transactions import Transactions
from transactions.services.myownregtestservice import RegtestDaemonService

from storage import getData


net = 'regtest'
actived_mainnet = (True and (net == 'mainnet'))

setup(net)  # set net of btcpy
SelectParams(net)  # set net of bitcoin


try:
	masterkey = getData()['masterprivkey'] # we get the masterkey of a storage.
except Exception as e:
	raise e

"""
	Requests a payment from a address wallet to a given recipients
	return (fromAddress, rawTx)
"""


def composeTx(transactions, rpcconn, addressTo, amount):		
	if not isinstance(transactions, Transactions):
		raise ValueError('Expected objects of type `Transactions`, got {} instead'.format(type(transactions)))
	if not isinstance(rpcconn, RegtestDaemonService):
		raise ValueError('Expected objects of type `RegtestDaemonService`, got {} instead'.format(type(rpcconn)))	
	if isinstance(amount, float):
		amount = int(amount)
	if not isinstance(amount, int):
		raise ValueError('Expected objects of type `int`, got {} instead'.format(type(amount)))		
	try:
		CBitcoinAddress(addressTo)
	except Base58ChecksumError:
		raise ValueError("address recipient invalid")

	try:
		transactions.import_address(addressTo)
	except OSError as e:
		raise e
	except:
		pass

	try:
		addressFrom = rpcconn.getnewaddress()

		rpcconn.sendtoaddress(addressFrom, (amount/COIN)+1)
		rpcconn.generate(1)

		rawTx = transactions.create(
		    addressFrom,
		    (addressTo, amount),
		    min_confirmations=1,
		)
		deserializeTx = Transaction.unhexlify(rawTx)

		return (addressFrom, rawTx, deserializeTx)
	except Exception as e:
		raise e


def createSignPushTransaction(transactions, rpcconn, addressTo, amount):
	try:
		addressFrom, rawTx, deserializeTx = composeTx(transactions, rpcconn, addressTo, amount)

		privKeyWIF = rpcconn.dumpprivkey(addressFrom)

		signedTx = transactions.sign(rawTx, privKeyWIF)
		hashPushedTx = transactions.push(signedTx)
		amountReceived = rpcconn.getreceivedbyaddress(addressTo)

		return (hashPushedTx, signedTx, deserializeTx, amountReceived)
	except Exception as e:
		raise e


def validAmount(transactions, rpcconn):
	try:
		if rpcconn.getbalance() < 99:
			print("generando ....")
			rpcconn.generate(2)
	except Exception as e:
		raise e


if __name__ == '__main__':
	rpcuser = 'admin1'
	rpcpassword = '123'
	host = 'localhost'
	rpcport = '19001'

	transactions = Transactions(username=rpcuser, password=rpcpassword, host=host, port=rpcport)	
	rpcconn = RegtestDaemonService(username=rpcuser, password=rpcpassword, host=host, port=rpcport)


	#result = createSignPushTransaction(transactions, rpcconn, "mgihCu3YkNQwyTpxbtpyX1Mfm24P6dcfig", 12*COIN)
	#result = composeTx(transactions, rpcconn, "mgihCu3YkNQwyTpxbtpyX1Mfm24P6dcfig", 9.7*COIN)
	#print(result)





