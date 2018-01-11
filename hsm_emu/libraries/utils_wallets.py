#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import base64
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from bitcoin.rpc import RawProxy, JSONRPCError, Proxy

from regtest import Manager
from btcpy.setup import setup
from btcpy.structs.hd import ExtendedKey
from btcpy.structs.sig import P2pkSolver, P2pkScript, P2pkhSolver, P2pkhScript, Sighash, P2shSolver, P2shScript
from btcpy.structs.script import ScriptSig
from btcpy.structs.transaction import Transaction, Sequence, TxOut, Locktime, TxIn, MutableTransaction, MutableTxIn
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from bitcoin import SelectParams
from bitcoin.core import lx, x, b2x, COIN
from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage
from storage import getData


net = 'regtest'
actived_mainnet = (True and (net == 'mainnet'))

setup(net)  # set net of btcpy
SelectParams(net)  # set net of bitcoin

try:
	masterkey = getData()['masterprivkey'] #obtenemos las masterkey de un storage
except Exception as e:
	raise e

"""
 Retrives Key Info of an Extended Private key
"""


def bip32KeyInfoFromKey(prvKey):
	privateMasterKey = ExtendedKey.decode(prvKey, check_network=actived_mainnet)
	return privateMasterKey


"""
	Retrieves BIP32 extended public key
	by path.

	path = "m/44'/0'/0'"; // first BIP44 account
"""


def getXPubKey(path):
	try:
		private_key_derived = derive(masterkey, path)
		pubkey = private_key_derived.key.pub()
		pubkey_format_pub = private_key_derived.pub().encode(mainnet=actived_mainnet)

		return (pubkey_format_pub, pubkey, pubkey.to_address())
	except Exception as e:
		raise e


"""
	Derive a key, method which takes as input:

	key: key
	path: a string representing a path

	examples:
		derive('tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX', "m/0'/0'/276'")

	return <class 'btcpy.structs.hd.ExtendedPrivateKey'>
"""


def derive(key, path):
	try:
		extendedKey = ExtendedKey.decode(key, check_network=False)
		return extendedKey.derive(path)
	except Exception as e:
		raise e


def customPathDerivation(key, path):
	try:
		derivedKey = derive(key, path)
		derived_encode = derivedKey.encode(mainnet=actived_mainnet)
		derived_pub_encode = derivedKey.pub().encode(mainnet=actived_mainnet)

		res = {
			'derivedPrivKey': derived_encode,
			'wifDerivedPrivKey': derivedKey.key.to_wif(),
			'derivedPubKey': derived_pub_encode,
			'hexDerivedPubKey': derivedKey.key.pub().hexlify(),
			'address': str(derivedKey.key.pub().to_address())
		}
		return res
	except Exception as e:
		raise e


"""
	Sign a message using the private key derived by given BIP32 path.

	path: a string representing a path
	message: a string

	Message is signed and address + signature is returned
	tuple(address, signature)

	example:
	path = "m/0'/0'/276'"   
"""


def signMessage(path, message):
	try:
		private_key_derived = derive(masterkey, path)
		address = private_key_derived.key.pub().to_address()
		#print(private_key_derived.key.to_wif())
		secret = CBitcoinSecret(private_key_derived.key.to_wif())   
		btc_message = BitcoinMessage(message)
		return (address, SignMessage(secret, btc_message), str(private_key_derived.key.pub()))
	except Exception as e:
		raise e

"""
	Verify a message using the address and signature.

	Message is verified and success is returned.
	address: base54
"""


def verifyMessage(address, signature, message):
	try:	
		if not isinstance(message, str):
			raise ValueError('Expected objects of type `str`, got {} instead'.format(type(message)))    
		btc_message = BitcoinMessage(message)
		return VerifyMessage(address, btc_message, signature)
	except Exception as e:
		raise e

"""
	Encrypt value (must be hexadecimal) using the private key derived by given 
	BIP32 path and the given key.
	
	example:
	path = "m/0'/0'/276'"
	key = ''
	value = '1c0ffeec0ffeec0ffeec0ffeec0ffee1'
"""


def cipherKeyValue(path, key, value):
	try:
		if not isinstance(key, bytes):
			raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(key)))    		
		if not isinstance(value, bytes):
			raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(value)))    					
		"""
		Fernet is built on top of a number of standard cryptographic 
		primitives. Specifically it uses:   

		AES in CBC mode with a 128-bit key for encryption; using PKCS7 padding.
		HMAC using SHA256 for authentication.
		Initialization vectors are generated using os.urandom().
		"""
		private_key_derived = derive(masterkey, path)
		byte_private_key = private_key_derived.key.serialize()


		backend = default_backend()
		salt = byte_private_key
		info = b"hkdf-bitcoin-regtest-example"
		hkdf = HKDF(
		     algorithm=hashes.SHA256(),
		     length=32,
		     salt=salt,
		     info=info,
		     backend=backend
		 )

		key = hkdf.derive(key)
		key_encode = base64.urlsafe_b64encode(key)	
			
		fernet = Fernet(key_encode)
		return fernet.encrypt(value)
	except Exception as e:
		raise e


"""
Decipher value (must be hexadecimal) using the private key derived by given 
BIP32 path and the given key.

path = "m/0'/0'/276'"
key = ''
value = '1c0ffeec0ffeec0ffeec0ffeec0ffee1'
"""


def decipherKeyValue(path, key, value):
	try:
		if not isinstance(key, bytes):
			raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(key)))    		
		if not isinstance(value, bytes):
			raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(value)))    						

		private_key_derived = derive(masterkey, path)
		byte_private_key = private_key_derived.key.serialize()

		backend = default_backend()
		salt = byte_private_key
		info = b"hkdf-bitcoin-regtest-example"
		hkdf = HKDF(
		     algorithm=hashes.SHA256(),
		     length=32,
		     salt=salt,
		     info=info,
		     backend=backend
		 )

		key = hkdf.derive(key)
		key_encode = base64.urlsafe_b64encode(key)	
			
		fernet = Fernet(key_encode)
		return fernet.decrypt(value)
	except Exception as e:
		raise e	


def raw_transaction(ins, outs):
	unsigned = MutableTransaction(version=2,
		ins=ins,
		outs=outs,
		locktime=Locktime(0))   
	return unsigned.hexlify()


if __name__ == '__main__':

	"""
	derived = derive('tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX', "m/0'/0'/276'")
	"""

	path = "m/0'/0'/1'"#"m/0'/0'/276'"
	masterkey = 'tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX'


	#print(bip32KeyInfoFromKey(masterkey))
	"""
	to_cipher = '1c0ffeec0ffeec0ffeec0ffeec0ffee1'

	value_ciphered = cipherKeyValue(path, masterkey, to_cipher)
	print(value_ciphered)

	value_deciphered = decipherKeyValue(path, masterkey, value_ciphered)
	assert value_deciphered == to_cipher
	print(value_deciphered)
	"""

	#ad = sign_message("m/0'/0'/276'", "Hola mundo")
	#print(ad)
	"""
	address='n4o8zBCZuqLxZEyiVgFRU2tEgyVdSYWpqX'
	signature = b'HweBSbDDwbG5Ez5cjN+k+MduL92prh2/UvMH3d1ADtqJE4wx9dUULttm5O6GEGvn3P5tvz3pZwQUfe2e4MLJYT8='
	message = 'Example message'

	print(signature.decode())
	ver = verify_message(ad[0], ad[1], "Hola mundo")
	##ver = verify_message(address, signature.decode(), message)
	print(ver)
	"""


	"""
	from btcpy.structs.crypto import PrivateKey
	from btcpy.structs.address import Address

	txid_1 = 'b4e0d22d4cfa07c08f5e7777e2aaefac3f80e8306dff8373cfcaa009039a8756'
	txid_2 = 'df83e176d22ae8cec23f23367fcdfeef0e5772e553b4eff95f60ccfae1b1d1d8'
	txout = 0
	amount_send_to_1 = 89.9
	amount_send_to_2 = 10
	private_key_derived = derive(masterkey, path)

	private_key_1 = PrivateKey.from_wif('cVPfiYz9kX96e1mfB6PHNMbDQEoTgL7RJKQqXC7jrmr5af6oH4Pz')
	private_key_2 = PrivateKey.from_wif('cUFcJuM8Nr9z2LXe5NBRnPWDpL2V8cT4KNWLjFWqZRnbcRMWVUNV')

	script_pubkey_me_1 = P2pkhScript(Address.from_string('n4A6y59PPHJns7bbKcHAviTybP9eWUG1BP'))
	script_pubkey_me_2 = P2pkhScript(Address.from_string('mxEB5wkyYdZyDim8THu1DFTgks44sqK53W'))
	#script_pubkey_me = P2pkhScript(private_key_derived.pub().key)

	print(private_key_1.pub().to_address())
	print(private_key_2.pub().to_address())

	ins=[TxIn(txid=txid_1, txout=txout, script_sig=ScriptSig.empty(), sequence=Sequence.max()),
		TxIn(txid=txid_2, txout=txout, script_sig=ScriptSig.empty(), sequence=Sequence.max())];
	outs=[TxOut(value=int(amount_send_to_1*COIN), n=0, script_pubkey=script_pubkey_me_1),
		TxOut(value=int(amount_send_to_2*COIN), n=0, script_pubkey=script_pubkey_me_2)];

	raw_t = raw_transaction(ins, outs)


	regtest = Manager(user='admin1', password='123', base_port=19000, base_rpcport=19001)
	regtest.generate_nodes2(1)
	regtest.start_nodes2()

	json_res = regtest.sign_raw_transaction(raw_t, [], [private_key_1.to_wif(),private_key_2.to_wif()], 0)
	if(json_res['complete']):
		tx_id = regtest.send_rpc_cmd(['sendrawtransaction', json_res['hex']], 0)    
	"""