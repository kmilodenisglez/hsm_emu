#!/usr/bin/python3

import logging
import random
import sys
import time

#from bitcoin.core import lx, x, b2x
from bitcoin.core import *
from bitcoin.core.script import *
from bitcoin.wallet import *

import bitcoin

bitcoin.SelectParams('regtest')

import bitcoin.rpc

logging.root.setLevel(logging.DEBUG)


# IF <recv_pub> CHECKSIG ELSE <expiry> 1 NOP2 2DROP ENDIF
# <send_pub> CHECKSIG

class MicropaymentParams:
    """Initial parameters of a micropayment channel"""

    @property
    def deposit_redeemScript(self):
        return CScript([OP_IF] + \
                           list(self.receiver_deposit_scriptPubKey) + \
                       [OP_ELSE,
                           self.expiry_nlocktime, 1, OP_NOP2, OP_2DROP,
                        OP_ENDIF] + \
                       list(self.sender_deposit_scriptPubKey),
                      )

    @property
    def deposit_scriptPubKey(self):
        return self.deposit_redeemScript.to_p2sh_scriptPubKey()

    def __init__(self,
                 sender_deposit_scriptPubKey,
                 receiver_deposit_scriptPubKey, receiver_dest_scriptPubKey,
                 expiry_nlocktime,
                 deposit_outpoint=COutPoint()):

        self.sender_deposit_scriptPubKey = sender_deposit_scriptPubKey

        self.receiver_deposit_scriptPubKey = receiver_deposit_scriptPubKey
        self.receiver_dest_scriptPubKey = receiver_dest_scriptPubKey

        self.deposit_outpoint = deposit_outpoint

        self.expiry_nlocktime = expiry_nlocktime


    def make_payment_tx(self,
                        change_nValue, dest_nValue,
                        sender_change_scriptPubKey,
                        txin_scriptSig=CScript(),
                        nSequence=0xFFFFFFFF):
        """Make a payment transaction

        Part of the micropayment channel parameters to standardize how the
        payment tx is created.
        """
        return CTransaction([CTxIn(self.deposit_outpoint, txin_scriptSig, nSequence=nSequence)],
                            [CTxOut(change_nValue, sender_change_scriptPubKey),
                             CTxOut(dest_nValue, self.receiver_dest_scriptPubKey)],
                            nLockTime=0,
                            nVersion=1) # be clear!

class MicropaymentChannel:
    """Micropayment channel state base class

    All state common to both sender and receiver
    """
    def __init__(self, params, deposit_nValue, last_payment_tx=None):
        self.params = params
        self.deposit_nValue = deposit_nValue
        self.last_payment_tx = last_payment_tx

    def calc_payment_value(self, payment_tx):
        """Calculate how much value a payment tx transfers to the receiver

        Returns the *total* amount we will get, the sum total sent to us during
        this session.
        """
        # FIXME: don't hardcode the order of txouts
        return payment_tx.vout[1].nValue

    @property
    def total_sent(self):
        """Total value sent as of the most recent payment tx"""
        if self.last_payment_tx is None:
            return 0

        else:
            return self.calc_payment_value(self.last_payment_tx)

class ReceiverMicropaymentChannel(MicropaymentChannel):
    """Micropayment channel state for receivers"""

    def __init__(self, params, receiver_seckey, deposit_nValue):

        self.receiver_seckey = receiver_seckey

        super().__init__(params, deposit_nValue)

    def validate_payment_tx(self, payment_tx):
        """Validate a micropayment tx

        The state of the channel is *not* changed.
        """
        # FIXME: implement!

    def recv_payment_tx(self, payment_tx):
        """Receive a micropayment

        The state of the channel is updated.

        Returns the delta nValue of the previous payment and the new payment.
        """
        self.validate_payment_tx(payment_tx)

        payment_value = self.calc_payment_value(payment_tx)

        if self.last_payment_tx is None:
            self.last_payment_tx = payment_tx
            return payment_value

        else:
            delta_nValue = payment_value - self.calc_payment_value(self.last_payment_tx)

            if delta_nValue > 0:
                self.last_payment_tx = payment_tx

            return delta_nValue

    def make_finalization_tx(self):
        """Create the finalization transaction"""

        sighash = SignatureHash(self.params.deposit_redeemScript, self.last_payment_tx, 0, SIGHASH_ALL)
        sig = self.receiver_seckey.sign(sighash) + bytes([SIGHASH_ALL])

        signed_scriptSig = CScript(list(self.last_payment_tx.vin[0].scriptSig) +
                                   [sig, 1,
                                    self.params.deposit_redeemScript])

        return CTransaction([CTxIn(self.last_payment_tx.vin[0].prevout, signed_scriptSig, self.last_payment_tx.vin[0].nSequence)],
                            self.last_payment_tx.vout,
                            nLockTime=self.last_payment_tx.nLockTime,
                            nVersion=self.last_payment_tx.nVersion)


class SenderMicropaymentChannel(MicropaymentChannel):
    """Micropayment channel state for senders"""

    def __init__(self, params, sender_seckey, sender_change_scriptPubKey, deposit_nValue):

        self.sender_seckey = sender_seckey
        self.sender_change_scriptPubKey = sender_change_scriptPubKey

        super().__init__(params, deposit_nValue)


    def make_payment_tx(self, delta_amount, *, fee):
        """Make a payment transaction

        delta_amount - The incremental amount to send.
        fee          - The fee (absolute)

        Note that delta_amount may be zero; this is useful to create the
        initial null-micropayment.

        The state of the channel is *not* changed.
        """
        if delta_amount < 0:
            raise ValueError("Amount to send must be non-negative")

        change_nValue = self.deposit_nValue - self.total_sent - delta_amount - fee
        if change_nValue < 0:
            raise ValueError("Amount greather than unspent deposit")

        unsigned_tx = self.params.make_payment_tx(change_nValue,
                                                  self.deposit_nValue - change_nValue - fee,
                                                  self.sender_change_scriptPubKey)

        sighash = SignatureHash(self.params.deposit_redeemScript, unsigned_tx, 0, SIGHASH_ANYONECANPAY | SIGHASH_ALL)
        sig = self.sender_seckey.sign(sighash) + bytes([SIGHASH_ANYONECANPAY | SIGHASH_ALL])

        signed_tx = self.params.make_payment_tx(change_nValue,
                                                self.deposit_nValue - change_nValue - fee,
                                                self.sender_change_scriptPubKey,
                                                txin_scriptSig = CScript([sig]))

        return signed_tx


    def send_payment(self, delta_amount, *, fee):
        """Send a micropayment

        Returns the new micropayment object.

        The state of the channel is updated.
        """
        payment_tx = self.make_payment_tx(delta_amount, fee=fee)
        self.last_payment_tx = payment_tx
        return payment_tx


    def make_refund_tx(self, *, fee):
        """Create a refund transaction

        All funds will be returned to the change scriptPubKey; previous
        payments are cancelled.

        fee - Fee to use

        The state of the channel is *not* changed.
        """

        unsigned_tx = CTransaction([CTxIn(self.params.deposit_outpoint, nSequence=0)],
                                   [CTxOut(self.deposit_nValue - fee, self.sender_change_scriptPubKey)],
                                   nLockTime=self.params.expiry_nlocktime)

        sighash = SignatureHash(self.params.deposit_redeemScript, unsigned_tx, 0, SIGHASH_ALL)
        sig = self.sender_seckey.sign(sighash) + bytes([SIGHASH_ALL])

        signed_scriptSig = CScript([sig, 0, self.params.deposit_redeemScript])

        return CTransaction([CTxIn(unsigned_tx.vin[0].prevout, signed_scriptSig, nSequence=0)],
                            unsigned_tx.vout,
                            nLockTime=unsigned_tx.nLockTime)



# test!

#sender_seckey = CBitcoinSecret.from_secret_bytes(Hash(b'alice'))
#receiver_seckey = CBitcoinSecret.from_secret_bytes(Hash(b'bob'))

sender_seckey = CBitcoinSecret('cQR1i1bCUYHEF65H7WFNUDtwcYy1zyXWHdcH8njzB3i6feAwX4Kf')
receiver_seckey = CBitcoinSecret('cRLxmQ6Bx4ymAQKLeNXH2b1BzVMabyzvN9nvAULp9QYPDD21Bdnc')

print('send seckey: %s' % sender_seckey)
print('recv seckey: %s' % receiver_seckey)

sender_change_addr = P2PKHBitcoinAddress.from_pubkey(sender_seckey.pub)
receiver_dest_addr = P2PKHBitcoinAddress.from_pubkey(receiver_seckey.pub)

deposit_outpoint = COutPoint()


channel_params = MicropaymentParams(CScript([sender_seckey.pub, OP_CHECKSIG]),         # sender deposit script
                                    CScript([receiver_seckey.pub, OP_CHECKSIGVERIFY]), # receiver deposit script
                                    receiver_dest_addr.to_scriptPubKey(),              # receiver's destination scriptPubKey
                                    1000000000)                                        # expiry nLockTime

deposit_addr = CBitcoinAddress.from_scriptPubKey(channel_params.deposit_scriptPubKey)
print('Deposit address: %s' % deposit_addr)


channel_params.deposit_outpoint = COutPoint(lx('093639268181b699462a90bd1ebe7d635e804b8acffef5c753b11e4036b6f6de'),0)#lx('fixme'), 0)
deposit_nValue = int(49.99 * 100000000)#int(0.1*COIN)

# Create send and receive sides of the channel from the parameters
send_side = SenderMicropaymentChannel(channel_params,
                                      sender_seckey, sender_change_addr.to_scriptPubKey(),
                                      deposit_nValue)

recv_side = ReceiverMicropaymentChannel(channel_params, receiver_seckey, deposit_nValue)

fee=1000#100000
payment_tx = send_side.send_payment(deposit_nValue/2, fee=fee)
for i in range(0, 1):
    # send some funds!
    payment_tx = send_side.send_payment(1, fee=fee)

    print(payment_tx)

    payment_value = recv_side.recv_payment_tx(payment_tx)

    print('payment-value: %d' % payment_value)


# have receiver finalize channel
finalization_tx = recv_side.make_finalization_tx()
print(b2x(finalization_tx.serialize()))

# have sender create refund
refund_tx = send_side.make_refund_tx(fee=fee)
print(b2x(refund_tx.serialize()))


#0100000001def6b636401eb153c7f5fecf8a4b805e637dbe1ebd902a4699b681812639360900000000e6483045022100fac1ef4ce69b5e681d378d942ad133d807211b0e6465dcd65430b0aa396ff2040220391767146e20fe38888473a1d65b5f017888d0fdbd11586d34c8146d1b92b4ad81483045022100b0ef3a6776951c067c6571ff90b077001088a41d133b4ee85794f5dbbafbef2402202ea6739b7511b12f988ba45e29239c83297120da1dc17ee7aa1402354d2cc8b401514c5163210221c6d85446d55e596702231b19a7aa5226dd4e61c1a5ad1fad4dbe0405d7e0daad670400ca9a3b51b16d682103d966463a13cc6dbe3585cd81d42986815a0423ef55cd073cff8d2bf813b1e125acffffffff02f753fb94000000001976a9140aef93e967ddf394ff7eb229148fa4846cf452ef88ace157fb94000000001976a9140b17a11bb2b7726d3bd2c66d5c894a14c45a69d488ac00000000


#0100000001def6b636401eb153c7f5fecf8a4b805e637dbe1ebd902a4699b6818126393609000000009c473044022056dc59c11444b5e58052e407c5058979c6dac155f2943c3939f912aab79e334202205b8e045fc9f8b19b9f9a43e45c733bbaccb0ac1055d76d3f57c46dbb59cc2fd701004c5163210221c6d85446d55e596702231b19a7aa5226dd4e61c1a5ad1fad4dbe0405d7e0daad670400ca9a3b51b16d682103d966463a13cc6dbe3585cd81d42986815a0423ef55cd073cff8d2bf813b1e125ac0000000001d8abf629010000001976a9140aef93e967ddf394ff7eb229148fa4846cf452ef88ac00ca9a3b
