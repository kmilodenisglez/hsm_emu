# Copyright (C) 2017 chainside srl
#
# This file is part of the btcpy package.
#
# It is subject to the license terms in the LICENSE.md file found in the top-level
# directory of this distribution.
#
# No part of btcpy, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE.md file.

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from bitcoin.rpc import RawProxy, JSONRPCError, Proxy

import subprocess
import errno
from time import sleep
from shutil import copyfile, rmtree
from bitcoin.rpc import RawProxy, JSONRPCError, Proxy


class NodesAlreadyConnected(Exception):
    pass


class RegtestRunning(Exception):
    pass


class SendCommandError(Exception):
    pass


class TxVerifyError(Exception):
    pass


class Manager(object):

    dst_dir = ''
    conf_path = './bitcoin.conf'
    host = '127.0.0.1'

    def __init__(self, user='user', password='pwd', base_port=18300, base_rpcport=18400, path='.'):
        self.nodes_number = 0
        self.nodes = {}
        self.regtest_path = path
        self.base_port = base_port
        self.base_rpcport = base_rpcport
        self.user = user
        self.password = password

    def generate_nodes2(self, num):
        for n in range(num):
            self.gen_node2(n)

    def gen_node2(self, id_):
        self.dst_dir = '{}/node_{}'.format(self.regtest_path, id_)
        #print("--> ", self.dst_dir)
        self.nodes[id_] = None

    def generate_nodes(self, num):
        for n in range(num):
            self.gen_node(n)

    def start_nodes2(self):
        for node in self.nodes:
            self.nodes[node] = {'user': self.user,
                                'password': self.password,
                                'host': self.host,
                                'port': self.base_port + node,
                                'rpcport': self.base_rpcport + node}        

    def gen_node(self, id_):
        dst_dir = '{}/node_{}'.format(self.regtest_path, id_)
        try:
            os.makedirs(dst_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        default_btc_conf = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), Manager.conf_path)
        copyfile(default_btc_conf, '{}/{}'.format(dst_dir, 'bitcoin.conf'))
        ip_port = Manager.base_port + id_
        rcp_port = Manager.base_rpcport + id_
        rpc_user = Manager.user
        rpc_password = Manager.password
        with open('{}/{}'.format(dst_dir, 'bitcoin.conf'), 'a') as config_file:
            config_file.write("rpcuser={}\n".format(rpc_user))
            config_file.write("rpcpassword={}\n".format(rpc_password))
            config_file.write("port={}\n".format(ip_port))
            config_file.write("rpcport={}\n".format(rcp_port))
        self.nodes[id_] = None

    def start_nodes(self):
        for node in self.nodes:
            data_dir = os.path.abspath('{}/node_{}'.format(self.regtest_path, node))
            conf = os.path.abspath('{}/bitcoin.conf'.format(data_dir))
            cmd = ['bitcoind', '-conf={}'.format(conf), '-datadir={}'.format(data_dir),
                   '-maxtxfee=1', '-debug=1', '-prematurewitness', '-zmqpubrawblock=tcp://127.0.0.1:28332']
            # cmd = ['/home/rael/bitcoin/src/bitcoind', '-conf={}'.format(conf), '-datadir={}'.format(data_dir),
            #        '-maxtxfee=1000', '-debug=1', '-prematurewitness']
            subprocess.call(cmd)  # , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.nodes[node] = {'user': self.user,
                                'password': self.password,
                                'host': self.host,
                                'port': self.base_port + node,
                                'rpcport': self.base_rpcport + node}

        sleep(3)

        for n in self.nodes:
            for m in self.nodes:
                if m != n:
                    self.send_rpc_cmd(['addnode',
                                       '{}:{}'.format(Manager.host, self.nodes[m]['port']),
                                       'onetry'],
                                      n)

    def stop_nodes(self):
        self.send_rpc_cmd(['stop'], *[n for n in self.nodes])

    def teardown(self):
        from os.path import abspath
        self.stop_nodes()
        for n in self.nodes:
            rmtree('{}/node_{}'.format(abspath(self.regtest_path), n))

    def sign_raw_transaction(self, raw_tx, prevtxs, privkeys, *nodes):
        proxies = {}
        for n in nodes:
            #proxies[n] = Proxy('http://{user}:{password}@{host}:{rpcport}'.format(**self.nodes[n]), self.base_rpcport, self.conf_path, 1000)
            proxies[n] = RawProxy('http://{user}:{password}@{host}:{rpcport}'.format(**self.nodes[n]), service_port=self.base_rpcport)

        for node in nodes:
            #print(".....>>> node: ", node)
            retry = 1
            while True:
                try:
                    cmd = 'signrawtransaction'
                    args = (raw_tx, prevtxs, privkeys,)
                    #print(getattr(proxies[int(node)], cmd)(500))
                    # print("command:", rpc_cmd)
                    # print("--==--->>> ",cmd, *args)
                    output = getattr(proxies[int(node)], cmd)(*args)
                    # print(output)
                    return output
                except JSONRPCError as e:
                    retry += 1
                    if e.error['code'] == -26:
                        raise TxVerifyError('Error during tx validation: {}'.format(e.error['message']))
                    if e.error['code'] != -28 or retry > 3:
                        raise SendCommandError("Error trying to send command to bitcoincli, "
                                               "error code: {}, message: {}".format(e.error['code'],
                                                                                    e.error['message']))
                    sleep(3 * (retry*2))        

    def send_rpc_cmd(self, rpc_cmd, *nodes):

        # print('Sending rpc command: {}'.format(' '.join(rpc_cmd)))
        proxies = {}
        for n in nodes:
            #proxies[n] = Proxy('http://{user}:{password}@{host}:{rpcport}'.format(**self.nodes[n]), self.base_rpcport, self.conf_path, 1000)
            proxies[n] = RawProxy('http://{user}:{password}@{host}:{rpcport}'.format(**self.nodes[n]), service_port=self.base_rpcport)

        # try convert rpc params from strings to ints
        for idx, val in enumerate(rpc_cmd):
            try:                
                rpc_cmd[idx] = int(val)
            except ValueError:
                if val in {'False', 'false'}:
                    rpc_cmd[idx] = False
                elif val in {'True', 'true'}:
                    rpc_cmd[idx] = True
        #print(".....>>>")
        for node in nodes:
            #print(".....>>> node: ", node)
            retry = 1
            while True:
                try:
                    cmd, *args = rpc_cmd
                    #print(getattr(proxies[int(node)], cmd)(500))
                    # print("command:", rpc_cmd)
                    # print("--==--->>> ",cmd, *args)
                    output = getattr(proxies[int(node)], cmd)(*args)
                    # print(output)
                    return output
                except JSONRPCError as e:
                    retry += 1
                    if e.error['code'] == -26:
                        raise TxVerifyError('Error during tx validation: {}'.format(e.error['message']))
                    if e.error['code'] != -28 or retry > 3:
                        raise SendCommandError("Error trying to send command to bitcoincli, "
                                               "error code: {}, message: {}".format(e.error['code'],
                                                                                    e.error['message']))
                    sleep(3 * (retry*2))

