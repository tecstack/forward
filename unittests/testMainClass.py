# (c) 2015-2018, Wang Zhe <azrael-ex@139.com>, Zhang Qi Chuan <zhangqc@fits.com.cn>
#
# This file is part of Ansible
#
# Forward is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Forward is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
