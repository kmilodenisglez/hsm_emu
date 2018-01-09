#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

import unittest
from binascii import hexlify, unhexlify
from context import setup, PublicKey, PrivateKey, P2pkhScript, P2shScript, P2wpkhV0Script, Address

setup('regtest')

def get_data(filename):
    import os
    import json
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open('{}/data/{}.json'.format(dir_path, filename)) as infile:
        return json.load(infile)

priv_pub_hash_addr_p2pkh_segwit = get_data('priv_pub_hash_addr_p2pkh_segwit')

class TestPrivPubHashAddrP2pkhSegwit(unittest.TestCase):

    def test(self):
        for data in priv_pub_hash_addr_p2pkh_segwit:
            priv = PrivateKey.from_wif(data['privkey'])
            pub = PublicKey.unhexlify(data['pubkey'])
            pubhash = bytearray(unhexlify(data['pubkeyhash']))
            address = Address.from_string(data['address'], check_network=False)
            p2pkhhex = data['scriptpubkey']
            segwit_addr = data['segwit']

            self.assertEqual(priv.pub(), pub)
            self.assertEqual(pub.hash(), pubhash)
            self.assertEqual(address.hash, pubhash)
            self.assertEqual(P2pkhScript(pub).hexlify(), p2pkhhex)
            self.assertEqual(P2pkhScript(address).hexlify(), p2pkhhex)
            self.assertEqual(P2pkhScript(pubhash).hexlify(), p2pkhhex)
            self.assertEqual(str(P2shScript(P2wpkhV0Script(pub)).address()), segwit_addr)
            self.assertEqual(str(P2shScript(P2wpkhV0Script(pubhash)).address()), segwit_addr)
            self.assertEqual(P2shScript(P2wpkhV0Script(pub)).scripthash, Address.from_string(segwit_addr).hash)
            self.assertEqual(P2shScript(P2wpkhV0Script(pubhash)).scripthash, Address.from_string(segwit_addr).hash)

if __name__ == '__main__':
    unittest.main()            