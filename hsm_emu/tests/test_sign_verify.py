#!/usr/bin/env python3
import unittest
from context import signMessage, verifyMessage, cipherKeyValue, decipherKeyValue

"""
derived = derive('tprv8ZgxMBicQKsPe7ZhPMqWcq8ZkQearQj5rYJCpbvdGF4bq5Hu1bpMKoRpCHgn54E1FF4shVYJrT4ESonYWRLWRyqEEVbgWuATBa3eevd5vRX', "m/0'/0'/276'")
"""

masterkey = 'tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF'


class TestCipherDecipher(unittest.TestCase):
	def test_decipher_success(self):
		path = "m/0'/0'/276'"
		to_cipher = '1c0ffeec0ffeec0ffeec0ffeec0ffee1'		

		value_ciphered = cipherKeyValue(path, masterkey, to_cipher)

		value_deciphered = decipherKeyValue(path, masterkey, value_ciphered)

		self.assertEqual(value_deciphered, to_cipher)

class TestSignVerify(unittest.TestCase):
	def test_verify_success(self):
		path = "m/0'/0'/276'"
		message = "Hola mundo"
		address_and_signature = signMessage(path, message)

		address = address_and_signature[0]	#object btcpy.struct.Address
		signature = address_and_signature[1] #base64 sign 

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
