#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest
import importlib
from forward import Forward
from forward.utils.forwardError import ForwardError

class TestMainForward(unittest.TestCase):

    def test_init(self):
        # new blank instance
        new_blank = Forward()
        self.assertEquals(new_blank.targets, [])
        self.assertEquals(new_blank.instances, {})
        self.assertTrue(isinstance(new_blank, Forward))

        # new success instance
        new_success = Forward(targets=[
            ['192.168.1.1', 'vlb', 'admin', 'admin_pw', {'port': 22, 'timeout': 30}],
            ['192.168.1.1', 'vlb', 'admin', 'admin_pw']
        ])
        self.assertEquals(new_success.targets, [
            ['192.168.1.1', 'vlb', 'admin', 'admin_pw', {'port': 22, 'timeout': 30}],
            ['192.168.1.1', 'vlb', 'admin', 'admin_pw']
        ])
        self.assertTrue(isinstance(new_success, Forward))

        # new fail instance
        with self.assertRaises(ForwardError):
            new_fail = Forward(targets=[['192.168.1.1', 'vlb', 'admin', 234]])

    def test_add_targets(self):
        new_blank = Forward()
        new_blank.addTargets(
            ['192.168.113.123'],
            'bclinux7',
            'north_king',
            'wolf_spirit',
            timeout=40,
            port=25
        )
        new_blank.addTargets(
            ['192.168.113.124-192.168.113.126'],
            'vlb',
            'south_king',
            'fish_spirit'
        )
        self.assertEquals(new_blank.targets, [
            ['192.168.113.123', 'bclinux7', 'north_king', 'wolf_spirit', {'timeout': 40, 'port': 25}],
            ['192.168.113.124', 'vlb', 'south_king', 'fish_spirit', {}],
            ['192.168.113.125', 'vlb', 'south_king', 'fish_spirit', {}],
            ['192.168.113.126', 'vlb', 'south_king', 'fish_spirit', {}]
        ])

    def test_get_instances(self):
        new_blank = Forward()
        new_blank.addTargets(
            ['192.168.113.123'],
            'bclinux7',
            'north_king',
            'wolf_spirit',
            timeout=40,
            port=25
        )
        new_blank.addTargets(
            ['192.168.113.124-192.168.113.126'],
            'vlb',
            'south_king',
            'fish_spirit'
        )
        instances = new_blank.getInstances(preLogin=False)
        node123 = instances['192.168.113.123']
        node124 = instances['192.168.113.124']
        node125 = instances['192.168.113.125']
        node126 = instances['192.168.113.126']

        self.assertTrue(isinstance(node123, getattr(
            importlib.import_module('forward.devclass.%s' % 'bclinux7'),
            'BCLINUX7'
        )))
        self.assertTrue(isinstance(node125, getattr(
            importlib.import_module('forward.devclass.%s' % 'vlb'),
            'VLB'
        )))
