#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>

import unittest
import os
import shutil
from mock import patch, Mock

from forward.cli import CLI
from forward.cli.cross import CrossCLI


class TestForward(unittest.TestCase):
    '''
        Unit test for Doc CLI Forward
    '''
    def setUp(self):
        ''' create test data folder and relative files '''
        self.test_folder = '.test'
        if not os.path.exists(self.test_folder):
            os.mkdir(self.test_folder)
        self.test_script = os.path.join(self.test_folder, 'forward_script.py')
        self.test_play = os.path.join(self.test_folder, 'forward_play.cfg')
        self.test_inventory = os.path.join(
            self.test_folder, 'forward_inventory.cfg')
        self.test_log = os.path.join(self.test_folder, 'forward.log')
        self.test_out = os.path.join(self.test_folder, 'forward_out')
        with open(self.test_script, 'w') as f:
            code_list = [
                'def node(nodeInput):\r\n',
                '\tnjInfo = {"status": True, "errLog": "", "content": {}}\r\n',
                '\tfor device in nodeInput["instance"]:\r\n',
                '\t\tinstance = nodeInput["instance"][device]\r\n',
                '\t\tversion=instance.execute("echo \'hello world\'")\r\n',
                '\t\tif version["status"]:\r\n',
                '\t\t\tnjInfo["content"][device] = version["content"]\r\n',
                '\t\telse:\r\n',
                '\t\t\tnjInfo["status"] = False\r\n',
                '\t\t\tnjInfo["errLog"] = "%s%s:%s\\r\\n" % ' +
                '(njInfo["errLog"], device, version["errLog"])\r\n',
                '\treturn njInfo\r\n']
            f.writelines(code_list)
        with open(self.test_play, 'w') as f:
            opt_list = [
                '[runtime]\r\n',
                'worker = 4\r\n',
                '[script]\r\n',
                'script = %s\r\n' % self.test_script,
                'args = {}\r\n',
                '[logging]\r\n',
                'loglevel = debug\r\n',
                'logfile = %s\r\n' % self.test_log,
                'no_std_log = False\r\n',
                '[output]\r\n',
                'out = txt\r\n',
                'outfile = %s\r\n' % self.test_out,
                '[connection]\r\n',
                'timeout = 2\r\n']
            f.writelines(opt_list)
        with open(self.test_inventory, 'w') as f:
            opt_list = [
                '[Tony Copper]\r\n',
                'hosts = ["127.0.0.1", "192.168.182.135"]\r\n',
                'vender = bclinux7\r\n',
                'model = bclinux7\r\n',
                'connect = ssh\r\n',
                'ask_pass = True\r\n',
                'ask_activate = True\r\n',
                'share = True\r\n',
                'remote_user = maiyifan\r\n',
                '[Monkey D Luffy]\r\n',
                'hosts = ["192.168.182.14-192.168.182.16"]\r\n',
                'vender = bclinux7\r\n',
                'model = bclinux7\r\n',
                'connect = ssh\r\n',
                'ask_pass = True\r\n',
                'ask_activate = False\r\n',
                'remote_user = maiyifan\r\n',
                'remote_port = 22\r\n']
            f.writelines(opt_list)

    def tearDown(self):
        ''' remove test files '''
        test_pyc = ''
        if os.path.exists(self.test_script):
            os.remove(self.test_script)
            test_pyc = '%s.pyc' % os.path.splitext(self.test_script)[0]
        if os.path.exists(test_pyc):
            os.remove(test_pyc)
        if os.path.exists(self.test_play):
            os.remove(self.test_play)
        if os.path.exists(self.test_inventory):
            os.remove(self.test_inventory)
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_out):
            os.remove(self.test_out)
        if os.path.isdir(self.test_folder):
            if len(os.listdir(self.test_folder)) == 0:
                shutil.rmtree(self.test_folder, True)

    def test_forward_cross_cli(self):
        ''' run a forward cross cli task '''
        args = [
            'forward-cross', '-C', self.test_play, '-I', self.test_inventory]
        mycli = CrossCLI(args)
        mycli.parse()
        result = None
        passwords = Mock(return_value=('111111', ''))
        with patch.object(CLI, 'ask_passwords', passwords):
            result = mycli.run()
        self.assertEqual(result['status'], True)
        self.assertTrue(os.path.exists(self.test_log))
        self.test_out = '%s.%s' % (self.test_out, 'txt')
        self.assertTrue(os.path.exists(self.test_out))
