# -*- coding: utf-8 -*-
"""
My Own Regtest Daemon Service based in Bitcoin Daemon Service, 
without request and pycoin library
"""
from __future__ import absolute_import, division, unicode_literals

from .service import BitcoinService
from transactions.utils import bitcoin_to_satoshi
from bitcoin.rpc import RawProxy


class RegtestDaemonService(BitcoinService):
    def __init__(self, username, password, host, port, testnet=False):
        super(RegtestDaemonService, self).__init__(testnet=testnet)
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self.proxy = RawProxy(self._url)

    @property
    def _url(self):
        return 'http://%s:%s@%s:%s' % (self._username, self._password,
                                       self._host, self._port)

    """
    Deamon in regtest mode.
    This works for Bitcoin core 0.10.1 and earlier with `regtest=1` set in bitcoin.conf
    this will generate a new block every time a transaction is pushed to the network
    """
    # Todo: Check bitcoin core version and set the correct method to generate a new block

    def make_request(self, method, params=[]):        
        #output = self.proxy.call(method, *params)
        response = self.proxy._call_all_response(method, *params)
        #print("\n-->",method, response)
        if method == 'sendrawtransaction' and response['error'] is None:
            self.make_request("generate", [1])
        return response        

    def get_block_raw(self, block_hash):
        return self.make_request('getblock', (block_hash,))

    def get_block_info(self, block_hash):
        return self.make_request('getblockheader', (block_hash,))

    def getinfo(self):
        return self.make_request('getinfo')

    def generate(self, numblocks):
        """
        As per bitcoin-cli docs:

        Mine blocks immediately (before the RPC call returns)

        .. note:: this function can only be used on the regtest network

        Args:
            numblocks (int): How many blocks are generated immediately.

        Returns:
            blockhashes (List[str]): hashes of blocks generated

        Examples:

            Generate 11 blocks
                >>> generate(11)
        """
        return self.make_request('generate', (numblocks,))

    def getbalance(self):
        response = self.make_request('getbalance')
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        return response.get('result')        


    def getreceivedbyaddress(self, address):
        response = self.make_request('getreceivedbyaddress', (address,))
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        return response.get('result')        

    def getnewaddress(self):
        response = self.make_request('getnewaddress')
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        return response.get('result')


    def dumpprivkey(self, address):
        response = self.make_request('dumpprivkey', params=(address,))
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        return response.get('result')        

    def sendtoaddress(self, address, amount):
        return self.make_request('sendtoaddress', params=(address, amount))

    def push_tx(self, tx):
        """

        :param tx = signed tx hash:
        :return: if successful info on tx, else error tx wasn't pushed
        """
        response = self.make_request("sendrawtransaction", [tx, True])
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        return response

    def decode_raw_transaction(self, tx):
        """

        :param tx = raw transaction
        :return: if successful info on tx, else error tx wasn't decode
        """
        response = self.make_request("decoderawtransaction", [tx])
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        return response

    def import_address(self, address, account="*", rescan=False):
        """
        param address = address to import
        param label= account name to use
        """
        response = self.make_request("importaddress", [address, account, rescan])
        error = response.get('error')
        if error is not None:
            raise Exception(error)
        return response

    def list_transactions(self, address, account="*", max_transactions=200):
        response = self.make_request("listtransactions", [account, max_transactions, 0, True])
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        results = response.get('result', [])
        results = [tx for tx in results if tx.get('address', '') == address and tx.get('category', '') == 'receive']

        out = []
        for tx in results:
            out.append({'txid': tx['txid'],
                        'amount': bitcoin_to_satoshi(tx['amount']),
                        'confirmations': tx['confirmations'],
                        'time': tx['time']})
        return out

    def list_unspents(self, address, min_confirmations):
        response = self.make_request('listunspent', [min_confirmations, 9999999, [address]])
        error = response.get('error')
        if error is not None:
            raise Exception(error)

        results = response.get('result', [])
        out = []
        for unspent in results:
            out.append({'txid': unspent['txid'],
                        'vout': unspent['vout'],
                        'amount': bitcoin_to_satoshi(unspent['amount']),
                        'confirmations': unspent['confirmations']})
        return out

    def get_raw_transaction(self, txid):
        response = self.make_request('getrawtransaction', [txid, 1])
        error = response.get('error')
        if error:
            raise Exception(error)

        raw_transaction = response.get('result')
        return raw_transaction

    def get_transaction(self, txid, raw=False):
        raw_tx = self.get_raw_transaction(txid)
        if raw:
            return raw_tx
        result = self._construct_transaction(raw_tx)
        return result

    def _get_address_for_vout(self, txid, vout_n):
        try:
            raw_tx = self.get_raw_transaction(txid)
            return [vout['scriptPubKey']['addresses'][0] for vout in raw_tx['vout'] if vout['n'] == vout_n][0]
        # TODO: Define exceptions for the daemon error messages
        # Coinbase transaction?
        # TODO review
        except Exception as e:
            if e.args and e.args[0] == {u'message': u'No information available about transaction', u'code': -5}:
                return ''
            else:
                raise

    def _get_value_from_vout(self, txid, vout_n):
        try:
            raw_tx = self.get_raw_transaction(txid)
            return [vout['value'] for vout in raw_tx['vout'] if vout['n'] == vout_n][0]
        # TODO: Define exceptions for the daemon error messages
        # Coinbase transaction?
        # TODO review
        except Exception as e:
            if e.args and e.args[0] == {'message': 'No information available about transaction', 'code': -5}:
                return 0
            else:
                raise

    def _construct_transaction(self, tx):
        result = {}
        result.update({'confirmations': tx.get('confirmations', ''),
                       'time': tx.get('time', ''),
                       'txid': tx.get('txid', ''),
                       'vins': [{'txid': vin['txid'], 'n': vin['vout'], 'value': bitcoin_to_satoshi(self._get_value_from_vout(vin['txid'], vin['vout'])),
                                 'address': self._get_address_for_vout(vin['txid'], vin['vout'])} for vin in tx.get('vin', [])],
                       'vouts': [{'n': vout['n'], 'value': bitcoin_to_satoshi(vout['value']),
                                  'asm': vout['scriptPubKey']['asm'],
                                  'hex': vout['scriptPubKey']['hex'],
                                  'address': vout['scriptPubKey'].get('addresses', ['NONSTANDARD'])[0]} for vout in tx.get('vout', [])]
                       })
        return result



