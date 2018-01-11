#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
	
import unittest
import base64
from context import (cipherKeyValue, decipherKeyValue, derive)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

masterkey = 'tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX'
path = "m/0'/0'/1'"
key = b'This is displayed on device on encrypt.'
valueToCipher = b'1c0ffeec0ffeec0ffeec0ffeec0ffee1'

keyEncoded = b'dK__XtdhYTQaa6mPND5rMSkTfXpHCF4TZJH3uXUZDKE='

class TestCipherDecipher(unittest.TestCase):
	def test_decipher_success(self):
		valueCiphered = cipherKeyValue(path, key, valueToCipher)
		print('value to cipher: ', valueToCipher)
		print('value ciphered: ', valueCiphered)

		valueDeciphered = decipherKeyValue(path, key, valueCiphered)
		self.assertEqual(valueDeciphered, valueToCipher)
		print('value deciphered: ', valueDeciphered)

	def test_deriving_key_success(self):
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

		keyDerived = hkdf.derive(key)
		key_encode = base64.urlsafe_b64encode(keyDerived)
		self.assertEqual(key_encode, keyEncoded)			
		print("key encode: ", key_encode)
		print("")


if __name__ == '__main__':
	unittest.main()