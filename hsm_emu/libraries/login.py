import hashlib
import struct
import binascii
import base64
import bitcoin
from urllib.parse import urlparse, ParseResult
from bitcoin.core import lx, x, b2x, COIN

from utils_wallets import verify_message, sign_message

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
	return sign_message(hdkeypath, b2x(message))

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
	return verify_message(address, signature, b2x(message))


if __name__ == '__main__':	
	challenge_hidden = "cd8552569d6e4509266ef137584d1e62c7579b5b8ed69bbafa4b864c6521e7c2" # Use random value
	challenge_visual = "2015-03-23 17:39:22"
	address = "mkcuRYXhBb6Pg8jjXuGSbfTXCJBrHPSp4d"
	signature = ""


	url = urlparse('http://satoshi@bitcoin.org:8080/login?1')

	print("url: ", url)
	hdkeypath = check_path(url)
	print("hdkeypath: ", hdkeypath)
	res_sign = sign(challenge_hidden, challenge_visual, hdkeypath)
	signature = b2x(res_sign[1])
	print(res_sign[0])

	assert address == str(res_sign[0])
	print("sign message: ", address, signature)

	print("\nverify: ", verify(challenge_hidden, challenge_visual, address, x(signature)))
