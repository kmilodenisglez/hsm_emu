#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
import unittest
	
from context import (setup, ExtendedKey, PublicKey, PrivateKey, 
	generatePrivateMasterKey)

setup('regtest')
actived_mainnet = False

masterpriv_regtest  = 'tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF'
masterpub_regtest   = 'tpubD6NzVbkrYhZ4YXycNn1nMZ94dUd967zeLEhHePMYWnCqJ5Mro7c39AM2NDkx4dDVmnDiajAqfLqdb4W9gxHLv8SwE8BqahJrnkoDEKWkUji'
masterpub_hex = "02cd0a395663fa55ca0adfeb8c0aaf14184199411fb322075d10e1091de9b3a134"
masterpriv_wif = "cVVKM8QJwdSomomhfpirgiHjtEppFcnWscvpXyoVHUgxUDQtar4n"

path = "m/0'/0'/276'"
derived_privkey = "tprv8hCq5soFxuy348MWAwZTfR5UXs7GTnFLfgxFB6GfmQyBZo6qD5nS8wESxYYBP5YvU1amXqK6TS3GRHUFLDRUjtQYEm4nWoPbMZoVKCsa7Af"
derived_privkey_hex = "5ba2423cf815f82dd2291b162cd6f34d6b55b6ac51958576eacb13f7a562e35d"
derived_privkey_wif = "cQeprJmTEw8QsKK6aZxtntMY8VmEhiGK9aWPfkqfsu1b2bZqpCb6"
derived_publkey = "tpubDDtsEHqW7HehwbPJ4bE44pjb6tdCd7SFEzZ2TcJyBgmaQHMbqUc2KRrK8fQsAW2Znn2V62yJGwtN4pRcQCeS4u2ZxCacirM3TCM1x3ZKWJZ"
derived_publkey_hex = "02521316bf307a8a5c0303ed15a659f902cf9eccb87366447655d7308f397dfbbf"
address_derived_publkey = "ms681MZr3MX9Y2mmWVkDB4souqwL9Y5h5A"

derived_chaincode = "d530a984bdb9499cf444267d5d16633ca7eecd7f29930802e5a04d93ea33213f"
derived_version = "04358394"
derived_depth = 3
derived_fingerprint = "fe6f590a"
derived_child_index = 276

priv = ExtendedKey.decode(masterpriv_regtest, check_network=actived_mainnet) #aqui no hace falta especificar mainnet, lo detecta x 1ro byte

class TestBIP32WalletCreation(unittest.TestCase):
	def test_master_publickey_success(self):
		masterpub = priv.pub()
		self.assertEqual(masterpub_regtest, masterpub.encode(mainnet=actived_mainnet))
		self.assertEqual(masterpub_hex, masterpub.key.hexlify())

	def test_path_derive_success(self):
		derived = priv.derive(path)		
		self.assertEqual(derived_privkey_hex, derived.key.hexlify())
		self.assertEqual(derived_privkey_wif, derived.key.to_wif())		
		self.assertEqual(derived_chaincode, derived.chaincode.hex())		
		self.assertEqual(derived_version, derived.get_version().hex())
		self.assertEqual(derived_depth, derived.depth)
		self.assertEqual(derived_fingerprint, derived.parent_fingerprint.hex())
		self.assertEqual(derived_child_index, derived.index)

		derived_pub = derived.pub().encode(mainnet=actived_mainnet)
		self.assertEqual(derived_publkey, derived_pub)
		self.assertEqual(address_derived_publkey, str(derived.key.pub().to_address()))
		self.assertEqual(derived_publkey_hex, derived.key.pub().hexlify())

	def test_fail_generate_key(self):
		k1 = generatePrivateMasterKey()
		k2 = generatePrivateMasterKey()
		self.assertNotEqual(k1, k2)


if __name__ == '__main__':
	unittest.main()		
