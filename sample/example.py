#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
-----Introduction-----
[Node][forward] node example.
Author: wangzhe
"""

"""
nodeInput = {
    'instance':{
        '172.17.0.2' : classInstanceA,
        '192.168.100.100' : classInstanceB
    },
    'parameters': <Which you define in your privateConf>
}
"""

"""
njInfo = {
    'status':True,
    'errLog':'',
    'content':{
        <custom>
    }
}
"""


def node(nodeInput):
    # init njInfo
    njInfo = {
        'status': True,
        'errLog': '',
        'content': {}
    }
    # node
    """
    Instance has method execute(cmd),return format as blow:
        data = classInstance.execute('cat /etc/redhat-release')
        data = {
            'status':True,
            'errLog':'',
            'content':'CentOS Linux release 7.1.1503 (Core) '
        }
    """
    for device in nodeInput['instance']:
        instance = nodeInput['instance'][device]
        version = instance.execute('cat /etc/redhat-release')
        if version['status']:
            # execute succeed
            njInfo['content'][device] = version['content']
        else:
            njInfo['status'] = False
            njInfo['errLog'] = '%s%s:%s\r\n' % (
                njInfo['errLog'], device, version['errLog'])
    return njInfo
