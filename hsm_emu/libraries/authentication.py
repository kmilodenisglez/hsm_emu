import os
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import random
import hashlib
import struct
import binascii
from datetime import datetime
from urllib.parse import urlparse, ParseResult
from bitcoin.core import x, b2x

from utils_wallets import verifyMessage, signMessage


"""
	Genera un hash256 (64 bytes) seudoaleatorio en cada nueva llamada.
"""


def getChallengeHidden():
	seed64B = hashlib.pbkdf2_hmac('sha256', os.urandom(64), os.urandom(16), random.randint(5, 20))
	return binascii.hexlify(seed64B).decode() # Use random value


"""
	Devuelve la fecha actual en el formato  2018-01-08 12:35:09.126812
"""


def getChallengeVisual():
	return str(datetime.today())


def checkPath(url):
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


def signAuth(challenge_hidden, challenge_visual, hdkeypath):
	h1 = hashlib.sha256(binascii.unhexlify(challenge_hidden)).digest()
	binary_challenge_visual = challenge_visual if isinstance(challenge_visual, bytes) else bytes(challenge_visual, 'utf-8')        
	h2 = hashlib.sha256(binary_challenge_visual).digest()        
	message = h1 + h2	
	return signMessage(hdkeypath, b2x(message))


def verifyAuth(challenge_hidden, challenge_visual, address, signature, version = 2):
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
	challenge_hidden = getChallengeHidden()
	challenge_visual = getChallengeVisual()
	address = "mrRXNQEvCyajiUhkSmYHSk7aeqsJuXnxLt"
	signature = ""

	url = urlparse('http://satoshi@bitcoin.org:8080/login?1')

	hdkeypath = checkPath(url)

	print("url: ", url)
	print("hdkeypath: ", hdkeypath)
	print("challenge_visual: ", challenge_visual)
	print("challenge_hidden: ", challenge_hidden)

	res_sign = signAuth(challenge_hidden, challenge_visual, hdkeypath)

	signature = b2x(res_sign[1])
	print("address: ", res_sign[0])

	assert address == str(res_sign[0])
	print("sign message: ", signature)

	print("\n        verify: ", verifyAuth(challenge_hidden, challenge_visual, address, x(signature)))
	print("|-------------------------|")
