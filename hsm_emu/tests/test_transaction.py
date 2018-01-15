#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
	
import unittest
from context import (txin, txout, rawTransaction, COIN)

prev_tx_id = "d97bc312048348148cc180dd99cb1befa30c226c2a4d1ef84974b1111b543fe6"
address_me = "n4P8d1TkqvWmNJrcSWKSXoNUzjrceU1wsC"
address_to = "mqTEZZofeDSxRffkpqdVXKHaerTH4v9bPK"

raw_tx = "0200000001e63f541b11b17449f81e4d2a6c220ca3ef1bcb99dd80c18c144883\
0412c37bd90000000000ffffffff0200ca9a3b000000001976a914fad02f8b1\
76df2700a708801c5478519e6a5037f88ac8091d2ed000000001976a9146cfd\
2c6283ff320c98d8d08821ce861c1ae4810f88ac00000000"

class TestTransaction(unittest.TestCase):
	def test_raw_transaction_success(self):
		tin = txin(prev_tx_id)
		tout1 = txout(address_me, 10*COIN)
		tout2 = txout(address_to, 39.9*COIN)
		raw_t = rawTransaction(tin, [tout1,tout2])		
		self.assertEqual(raw_tx, raw_t.hexlify())
		


if __name__ == '__main__':
	unittest.main()