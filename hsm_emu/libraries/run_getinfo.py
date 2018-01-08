#!/usr/bin/env python3

from regtest import Manager
from btcpy.setup import setup

from btcpy.structs.transaction import Transaction, Sequence, TxOut, Locktime, TxIn, MutableTransaction, MutableTxIn
from btcpy.structs.sig import P2pkhSolver, P2pkhScript, P2shSolver, SingleSigSolver, P2pkSolver, P2pkScript
from btcpy.structs.script import Script, ScriptBuilder,ScriptSig
from btcpy.structs.hd import ExtendedKey, ExtendedPrivateKey, ExtendedPublicKey
from btcpy.structs.crypto import PrivateKey

from btcpy.structs.address import Address
from binascii import hexlify, unhexlify

setup('regtest')

regtest = Manager(user='admin1', password='123', base_port=19000, base_rpcport=19001)
regtest.generate_nodes2(1)
regtest.start_nodes2()

info = regtest.send_rpc_cmd(['getinfo'], 0)

print(info)
print(regtest.send_rpc_cmd(['getbalance'], 0))
print(info['blocks'])
print(info['balance'])



def simple_transaction(addr_to_string, amount):
	txid = regtest.send_rpc_cmd(['sendtoaddress', addr_to_string, amount], 0)
	return txid


def generate(block):
	out = regtest.send_rpc_cmd(['generate', block], 0)
	return out



def sign_transaction(private_key, address_me, address_to, amount_send_me, amount_send_to, txid, vout):	
	script_pubkey_me = P2pkScript(private_key.pub())
	#script_pubkey_me = P2pkhScript(Address.from_string(address_me))
	#script_pubkey_to = P2pkhScript(Address.from_string(address_to))
	#to_spend = Transaction.unhexlify(regtest.send_rpc_cmd(['createrawtransaction', txid, '0'], 0))
	unsigned = MutableTransaction(version=2,
		ins=[TxIn(txid=txid,
					txout=vout,
					script_sig=ScriptSig.empty(),
					sequence=Sequence.max())
			],
		outs=[#TxOut(value=amount_send_to, n=0, script_pubkey=script_pubkey_to),	
			TxOut(value=amount_send_to, n=0, script_pubkey=script_pubkey_me)
			],
		locktime=Locktime(0))
	#print(unsigned)

	#solver = P2pkhSolver(private_key)
	#solver = P2shSolver(script_pubkey_me,  # the redeemScript
	#                    P2pkhSolver(private_key))
	solver = P2pkSolver(private_key)
	#print(solver)	
	signed = unsigned.spend([unsigned.outs[0]], [solver])
	#print(signed)	
	print("signed...enviando now")
	print(signed.hexlify())
	#regtest.send_rpc_cmd(['sendrawtransaction', signed.hexlify()], 0)
	#print('Mempool size: {}'.format(len(regtest.send_rpc_cmd(['getrawmempool'], 0))))
	#print("valor: ", value)

"""
def sign_transaction(private_key, address_me, address_to, amount_send_me, amount_send_to, txid, vout):	
	script_pubkey_me = P2pkScript(private_key.pub())	
	#script_pubkey_me = P2pkhScript(Address.from_string(address_me))	
	#script_pubkey_to = P2pkhScript(Address.from_string(address_to))
	#to_spend = Transaction.unhexlify(regtest.send_rpc_cmd(['createrawtransaction', txid, '0'], 0))
	unsigned = MutableTransaction(version=2,
		ins=[TxIn(txid=txid,
					txout=vout,
					script_sig=ScriptSig.empty(),
					sequence=Sequence.max())
			],
		outs=[#TxOut(value=amount_send_to, n=0, script_pubkey=script_pubkey_to),	
			TxOut(value=amount_send_to, n=0, script_pubkey=script_pubkey_me)
			],
		locktime=Locktime(0))
	#print(unsigned)

	#solver = P2pkhSolver(private_key)
	#solver = P2shSolver(script_pubkey_me,  # the redeemScript
	#                    P2pkhSolver(private_key))
	solver = P2pkSolver(private_key)
	#print(solver)	
	signed = unsigned.spend([unsigned.outs[0]], [solver])
	#print(signed)	
	print("signed...enviando now")
	print(signed.hexlify())
	#regtest.send_rpc_cmd(['sendrawtransaction', signed.hexlify()], 0)
	#print('Mempool size: {}'.format(len(regtest.send_rpc_cmd(['getrawmempool'], 0))))
	#print("valor: ", value)
"""

txid='7a82c0a2cd0c5a86be6cf974b37971eb8d93155cc63d98a37865840a70108b1e'
#private_key = PrivateKey.unhexlify('9decdfd662d1b3cf49ba3fe1d14114f8426bdbea633f89601123707b8e5cf1ab')
private_key = PrivateKey.from_wif('cUgMT4rFkhAUbJJ4ZUXLRLTfF8HEaKBGazq2PAKRrjCR5PP4SWiF')
#private_key = ExtendedPrivateKey.decode('tprv8h9fumap7U2nASh3bLZT71rTCoviJcSCegc7pUwPcELGdk4mmoc21sMgD163zx6QYPoyDfW8Nn8Bh1haRqM2KMUvALcLfgkfHffVJwiFo3D').key
address_me = 'mmJZhiu6anTbp8a5Jqvf9o8me2Wu1LQZTW'
address_to = 'mmJZhiu6anTbp8a5Jqvf9o8me2Wu1LQZTW'#'miRbXv7JXbBw6PAXXKXHJtxCMvuamRBNLU'
amount_send_me = int(0.9 * 100000000)
amount_send_to = int(49.9 * 100000000)
#8.9 
#890000000
#170.0
#17000000000
#X 1000000
vout = 0
#print generate(1)
#print(simple_transaction("miRbXv7JXbBw6PAXXKXHJtxCMvuamRBNLU", 1))

"""
# Create a connection to local Bitcoin Core node
p = RawProxy()
# Run the getinfo command, store the resulting data in inf
info = p.getinfo()
# Retrieve the 'blocks' element from the info
print(info['blocks'])
"""

sign_transaction(private_key, address_me, address_to, amount_send_to, amount_send_to, txid, vout)

#script_sig = Script.unhexlify('47304402203c68ce022a5348b17c5c951eb351c9db1281f3b0fbae2a7c2a0bbee014a2eb26022054e01e99b7d162bd1a64738fb588f8a03f34851aa30e5549f894adddffff231b01')
#print(script_sig)
