#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
	
import unittest
from context import cipherKeyValue, decipherKeyValue

masterkey = 'tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF'


class TestCipherDecipher(unittest.TestCase):
	def test_decipher_success(self):
		path = "m/0'/0'/276'"
		to_cipher = '1c0ffeec0ffeec0ffeec0ffeec0ffee1'		

		value_ciphered = cipherKeyValue(path, masterkey, to_cipher)

		value_deciphered = decipherKeyValue(path, masterkey, value_ciphered)

		self.assertEqual(value_deciphered, to_cipher)


if __name__ == '__main__':
	unittest.main()