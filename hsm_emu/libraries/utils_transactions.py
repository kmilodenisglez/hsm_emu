#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from btcpy.setup import setup
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


def createSignPushTransaction(transactions, rpcconn, to_address, amount):
	if not isinstance(transactions, Transactions):
		raise ValueError('Expected objects of type `Transactions`, got {} instead'.format(type(transactions)))
	if not isinstance(rpcconn, RegtestDaemonService):
		raise ValueError('Expected objects of type `RegtestDaemonService`, got {} instead'.format(type(rpcconn)))
	try:		
		CBitcoinAddress(to_address)
	except Base58ChecksumError:
		raise ValueError("address invalid")

	try:
		transactions.import_address(to_address)
	except OSError as e:
		raise e
	except:
		pass

	try:
		from_address = rpcconn.getnewaddress()
		privKeyWIF = rpcconn.dumpprivkey(from_address)

		rpcconn.sendtoaddress(from_address, (amount/COIN)+1)
		rpcconn.generate(1)

		raw_tx = transactions.create(
		    from_address,
		    (to_address, amount),
		    min_confirmations=1,
		)
		signed_tx = transactions.sign(raw_tx, privKeyWIF)
		pushed_tx = transactions.push(signed_tx)
		amountReceived = rpcconn.getreceivedbyaddress(to_address)

		return (pushed_tx, signed_tx, amountReceived)
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


	result = createSignPushTransaction(transactions, rpcconn, "mgihCu3YkNQwyTpxbtpyX1Mfm24P6dcfig", 12*COIN)
	print(result)



