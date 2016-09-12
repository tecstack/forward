#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>

import unittest
import os
import shutil
from mock import patch, Mock

from forward.cli import CLI
from forward.cli.console import ConsoleCLI


class TestForward(unittest.TestCase):
    '''
        Unit test for Console CLI Forward
    '''
    def setUp(self):
        ''' create test data folder and relative files '''
        self.test_folder = '.test'
        if not os.path.exists(self.test_folder):
            os.mkdir(self.test_folder)
        self.test_script = os.path.join(self.test_folder, 'forward_script.py')
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

    def tearDown(self):
        ''' remove test files '''
        test_pyc = ''
        if os.path.exists(self.test_script):
            os.remove(self.test_script)
            test_pyc = '%s.pyc' % os.path.splitext(self.test_script)[0]
        if os.path.exists(test_pyc):
            os.remove(test_pyc)
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_out):
            os.remove(self.test_out)
        if os.path.isdir(self.test_folder):
            if len(os.listdir(self.test_folder)) == 0:
                shutil.rmtree(self.test_folder, True)

    def test_forward_console_cli(self):
        ''' run a forward console cli task '''
        # forward -w 4 -s .test/forward_script.py -a {} --loglevel debug
        # -l .test/forward.log --no-stdout-log -t txt -o .test/forward_out
        # -i '["127.0.0.1", "192.168.182.14-192.168.182.16"]' -v bclinux7
        # -m bclinux7 --connect ssh -P -A -p 22 -u maiyifan -T 2 -S
        args = [
            'forward', '-w', '4', '-s', self.test_script, '-a', '{}',
            '--loglevel', 'info', '-l', self.test_log,
            '--no-stdout-log', '-t', 'txt', '-o', self.test_out,
            '-i', '["127.0.0.1", "192.168.182.14-192.168.182.16"]',
            '-v', 'bclinux7', '-m', 'bclinux7', '--connect', 'ssh',
            '-P', '-A', '-p', '22', '-u', 'maiyifan', '-T', '2']
        mycli = ConsoleCLI(args=args)
        mycli.parse()
        result = None
        passwords = Mock(return_value=('111111', ''))
        with patch.object(CLI, 'ask_passwords', passwords):
            result = mycli.run()
        self.assertEqual(result['stdout']['status'], True)
        self.assertTrue(os.path.exists(self.test_log))
        self.test_out = '%s.%s' % (self.test_out, 'txt')
        self.assertTrue(os.path.exists(self.test_out))
