#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
import base64
from bitcoin.rpc import RawProxy, JSONRPCError, Proxy

from regtest import Manager
from btcpy.setup import setup
from btcpy.structs.crypto import PrivateKey
from btcpy.structs.hd import ExtendedKey, ExtendedPrivateKey
from btcpy.structs.sig import P2pkSolver, P2pkScript, P2pkhSolver, P2pkhScript, Sighash, P2shSolver, P2shScript
from btcpy.structs.script import ScriptSig
from btcpy.structs.address import Address
from btcpy.structs.transaction import Transaction, Sequence, TxOut, Locktime, TxIn, MutableTransaction, MutableTxIn
import ecdsa
from ecdsa.curves import SECP256k1
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
	masterkey = getData()['masterprivkey'] # we get the masterkey of a storage.
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
	Generates a 32-bit random seed using 
	HKDF (HMAC-based Extract-and-Expand Key Derivation Function).
"""


def secret(key, salt, info):
	if not isinstance(key, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(key)))
	if not isinstance(salt, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(salt)))
	if not isinstance(info, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(info)))
	try:
		kdf = HKDF(
			algorithm=hashes.SHA256(),
			length=32,
			salt=salt,        
			info=info,
			backend=default_backend()
		)
		sc = kdf.derive(key)    
		return sc
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
	if not isinstance(key, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(key)))    		
	if not isinstance(value, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(value)))    						
	try:
		"""
		Fernet is built on top of a number of standard cryptographic 
		primitives. Specifically it uses:   

		AES in CBC mode with a 128-bit key for encryption; using PKCS7 padding.
		HMAC using SHA256 for authentication.
		Initialization vectors are generated using os.urandom().

		We use a key and path with Fernet. To do this, you need to run the key through 
		a key derivation function such as HKDF (HMAC-based Extract-and-Expand Key Derivation Function)
		is suitable for deriving keys of a fixed size used for other cryptographic operations..
		"""
		private_key_derived = derive(masterkey, path)
		byte_private_key = private_key_derived.key.serialize()

		salt = byte_private_key
		info = b"hkdf-bitcoin-regtest-example"

		sc = secret(key, salt, info)
		key_encode = base64.urlsafe_b64encode(sc)	
			
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
	if not isinstance(key, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(key)))    		
	if not isinstance(value, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(value)))    						
	try:
		private_key_derived = derive(masterkey, path)
		byte_private_key = private_key_derived.key.serialize()

		salt = byte_private_key
		info = b"hkdf-bitcoin-regtest-example"		

		sc = secret(key, salt, info)
		key_encode = base64.urlsafe_b64encode(sc)	
			
		fernet = Fernet(key_encode)
		return fernet.decrypt(value)
	except Exception as e:
		raise e

"""
	Create a key
"""

def generatePrivateMasterKey():	
	key = os.urandom(16)
	salt = os.urandom(16)
	derived_chaincode = os.urandom(32)
	
	info = b"hkdf-bitcoin-regtest-example"  
	seed = secret(key, salt, info)
	key = ecdsa.SigningKey.from_string(seed, curve=SECP256k1)
	prvkey = PrivateKey(key.to_string())	
	
	masterprivkey = ExtendedPrivateKey.master(prvkey, derived_chaincode)
	return masterprivkey


"""
	Create a TxIn

	example:
	tx = b4e0d22d4cfa07c08f5e7777e2aaefac3f80e8306dff8373cfcaa009039a8756	
	txout = 1

	txin(tx, txout)

	return this object:
		TxIn(txid=b4e0d22d4cfa07c08f5e7777e2aaefac3f80e8306dff8373cfcaa009039a8756, txout=0, script_sig=, sequence=4294967295, witness=None)
"""


def txin(prev_hash, prev_index=0):
	if not isinstance(prev_hash, str):
		raise ValueError('Expected objects of type `str`, got {} instead'.format(type(prev_hash)))	
	if not isinstance(prev_index, int):
		raise ValueError('Expected objects of type `int`, got {} instead'.format(type(prev_index)))
	try:
		return TxIn(txid=prev_hash, txout=prev_index, script_sig=ScriptSig.empty(), sequence=Sequence.max())
	except Exception as e:
		raise e		


"""
	Create a TxOut

	example:
	address_to = n4A6y59PPHJns7bbKcHAviTybP9eWUG1BP	
	amount = 3181747

	txout(address_to, amount)

	return this object:
		TxOut(value=318174700000000, n=0, scriptPubKey='OP_DUP OP_HASH160 f85965bfd6f6a0a98a85020020db50539d610670 OP_EQUALVERIFY OP_CHECKSIG')
"""


def txout(address, amount, n=0):
	if not isinstance(address, str):
		raise ValueError('Expected objects of type `str`, got {} instead'.format(type(address)))
	if not (isinstance(amount, int) or isinstance(amount, float)):
		raise ValueError('Expected objects of type `int` or `float`, got {} instead'.format(type(amount)))
	try:		
		script_pubkey = P2pkhScript(Address.from_string(address))
		return TxOut(value=int(amount), n=n, script_pubkey=script_pubkey)
	except Exception as e:
		raise e	


def rawTransaction(ins, outs, version = 2):
	if not isinstance(ins, list) and isinstance(ins, TxIn):
		ins=[ins]
	elif not isinstance(ins, list) and not isinstance(ins, TxIn):
		raise ValueError('Expected objects of type `[TxIn]` or `TxIn`, got {} instead'.format(type(ins)))		
	if not isinstance(outs, list) and isinstance(outs, TxOut):
		outs=[outs]
	elif not isinstance(outs, list) and not isinstance(outs, TxOut):
		raise ValueError('Expected objects of type `[TxOut]` or `TxOut`, got {} instead'.format(type(outs)))
	tx = Transaction(version=version,
		ins=ins,
		outs=outs,
		locktime=Locktime(0))	
	return tx#.hexlify()


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

	raw_t = rawTransaction(ins, outs)


	regtest = Manager(user='admin1', password='123', base_port=19000, base_rpcport=19001)
	regtest.generate_nodes2(1)
	regtest.start_nodes2()

	json_res = regtest.sign_raw_transaction(raw_t, [], [private_key_1.to_wif(),private_key_2.to_wif()], 0)
	if(json_res['complete']):
		tx_id = regtest.send_rpc_cmd(['sendrawtransaction', json_res['hex']], 0)    
	"""
	"""
	tin = txin("d97bc312048348148cc180dd99cb1befa30c226c2a4d1ef84974b1111b543fe6")
	tout1 = txout("n4P8d1TkqvWmNJrcSWKSXoNUzjrceU1wsC", 10)
	tout2 = txout("mqTEZZofeDSxRffkpqdVXKHaerTH4v9bPK", 39.9)
	

	raw_t = rawTransaction(tin, [tout1,tout2])
	print(raw_t)
	"""


	

	"""
	#k = PrivateKey.unhexlify(b2x(key))
	prvkey = PrivateKey(key)
	

	derived_chaincode = generatePrivateMasterKey().to_string()
	print(derived_chaincode)
	#exkey = ExtendedPrivateKey(k, derived_chaincode, 0, "fe6f590a", 0, hardened = True)
	exkey = ExtendedPrivateKey.master(prvkey, generatePrivateMasterKey().to_string())
	derive = exkey.derive("m/0'/0'/276'")
	print(derive.encode(mainnet=actived_mainnet))

	print(secret())
	"""


