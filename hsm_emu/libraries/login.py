import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
	
import os
import random
import hashlib
import struct
import binascii
import base64
import bitcoin
from datetime import datetime
from urllib.parse import urlparse, ParseResult
from bitcoin.core import lx, x, b2x, COIN

from utils_wallets import customPathDerivation, verifyMessage, signMessage

masterkey = 'tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX'	

def check_path(url):
	if not isinstance(url, ParseResult):
		raise ValueError('Expected objects of type `ParseResult`, got {} instead'.format(type(url)))
	m = hashlib.sha256()
	m.update(struct.pack("<I", int(url.query)))
	uri = url.geturl()
	m.update(bytes(uri, 'utf-8'))
	(a, b, c, d, _, _, _, _) = struct.unpack('<8I', m.digest())
	address_n = [0x80000000 | 13, 0x80000000 | a, 0x80000000 | b, 0x80000000 | c, 0x80000000 | d]	
	hdkeypath = "m/" + "/".join([str(x) for x in address_n])		
	return hdkeypath

def sign(challenge_hidden, challenge_visual, hdkeypath):
	h1 = hashlib.sha256(binascii.unhexlify(challenge_hidden)).digest()
	binary_challenge_visual = challenge_visual if isinstance(challenge_visual, bytes) else bytes(challenge_visual, 'utf-8')        
	h2 = hashlib.sha256(binary_challenge_visual).digest()        
	message = h1 + h2	
	return signMessage(hdkeypath, b2x(message), masterkey)

def verify(challenge_hidden, challenge_visual, address, signature, version = 2):
	if not isinstance(signature, bytes):
		raise ValueError('Expected objects of type `bytes`, got {} instead'.format(type(signature)))

	if version == 1:
		message = binascii.unhexlify(challenge_hidden + binascii.hexlify(challenge_visual))
	elif version == 2:
		h1 = hashlib.sha256(binascii.unhexlify(challenge_hidden)).digest()
		binary_challenge_visual = challenge_visual if isinstance(challenge_visual, bytes) else bytes(challenge_visual, 'utf-8')        
		h2 = hashlib.sha256(binary_challenge_visual).digest()        
		message = h1 + h2
	return verifyMessage(address, signature, b2x(message))


if __name__ == '__main__':
	seed64B = hashlib.pbkdf2_hmac('sha256', os.urandom(64), os.urandom(16), random.randint(5, 20))
	challenge_hidden = binascii.hexlify(seed64B).decode() # Use random value
	challenge_visual = str(datetime.today())
	address = "mkcuRYXhBb6Pg8jjXuGSbfTXCJBrHPSp4d"
	signature = ""


	url = urlparse('http://satoshi@bitcoin.org:8080/login?1')

	print("url: ", url)
	hdkeypath = check_path(url)
	print("hdkeypath: ", hdkeypath)
	#deriveKey = derive(masterkey, hdkeypath)
	print(customPathDerivation(masterkey, hdkeypath))
	"""
	res_sign = sign(challenge_hidden, challenge_visual, hdkeypath)
	signature = b2x(res_sign[1])
	print(res_sign[0])

	assert address == str(res_sign[0])
	print("sign message: ", address, signature)

	print("\nverify: ", verify(challenge_hidden, challenge_visual, address, x(signature)))
	"""
