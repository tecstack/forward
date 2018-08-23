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

"""
-----Introduction-----
[Core][Forward] addTargets parameters legal check function
Author: Wang Zhe
"""


def paraCheck(targets):
    # Legal targets: [target1, target2, target3....]
    # Legal target type: [ip-str, model-str, user-str, pw-str, kwargs-dict]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw', {'port': 22, 'timeout': 30}]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw', {'port': 22}]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw', {'timeout': 30}]
    # Legal target: ['192.168.1.1', 'n7k', 'admin', 'admin_pw']
    bool_legal = isinstance(targets, list)

    if bool_legal:
        for target in targets:
            try:
                bool_legal &= (len(target) >= 4 and len(target) < 6)
                bool_legal &= isinstance(target[0], str)
                bool_legal &= isinstance(target[1], str)
                bool_legal &= isinstance(target[2], str)
                bool_legal &= isinstance(target[3], str)
                if len(target) > 4:
                    bool_legal &= isinstance(target[4], dict)
                else:
                    bool_legal &= True
            except Exception:
                return False
            if not bool_legal:
                break
        return bool_legal
    else:
        return False


def int_to_mask(mask_int):
    # 24 --> 255.25.255.0
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


def mask_to_int(mask):
    # 255.255.255.0 --> 24
    return sum(bin(int(i)).count('1') for i in mask.split('.'))
