#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
	
import unittest
from context import signMessage, verifyMessage


class TestSignVerify(unittest.TestCase):
	def test_verify_success(self):
		path = "m/0'/0'/276'"
		message = "Hola mundo"
		address_and_signature = signMessage(path, message)

		address = address_and_signature[0]	# object btcpy.struct.Address
		signature = address_and_signature[1] # base64 sign 

		print("message: ", message)
		print("")
		print("address: ", address)
		print("")
		print("signature: ", signature)
		print("")

		verify = verifyMessage(address, signature.decode(), "Hola mundo")
		self.assertEqual(verify, True)
		print("Verified!!!")


if __name__ == '__main__':
	unittest.main()