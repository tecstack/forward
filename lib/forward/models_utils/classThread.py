#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core] Thread Function for init class instance.
Date: 2016-04-15
"""

import importlib
from forward.models_utils.mysqlDb import MYSQLDB

def classThread(threadVar,device):
    db = MYSQLDB(threadVar.dbHost,threadVar.dbUsername,threadVar.dbPassword,threadVar.db,threadVar.dbPort,threadVar.publicKeyPath,threadVar.privateKeyPath)
    connect = db.connect()
    if connect['status']:
    # mysql connect succeed
        """
        [ex]deviceInfo {
            'status': True,
            'errLog': '',
            'content': {
                'username': 'anonymous',
                'deviceNumber': 'bc02',
                'ip': '172.17.0.2',
                'secondPassword': '',
                'loginMethod': 'sshv2',
                'deviceType': 'bclinux7',
                'password': 'xxx',
                'port': 22L
            }
        }
        """
        deviceInfo = db.getDeviceInfo(threadVar.dbTableDevice,device)
        if deviceInfo['status']:
            # [ex] 'bclinux7'
            typeName = deviceInfo['content']['deviceNumber']
            # [ex] 'BCLINUX7'
            className = typeName.upper()
            try:
                # From models.xx import XX, classInstance = XX(ip,port,timeout)
                tmpInstance = getattr(importlib.import_module('models.%s' % (typeName)),className)(
                    deviceInfo['content']['ip'],
                    deviceInfo['content']['port'],
                    threadVar.timeout,
                )
                tmpLogin = tmpInstance.login(deviceInfo['content']['username'],deviceInfo['content']['password'])
                if tmpLogin['status']:
                    # login succeed
                    # enable
                    tmpPrivilegeMode=tmpInstance.privilegeMode(deviceInfo['content']['secondPassword'],deviceInfo['content']['deviceType'])
                    if tmpPrivilegeMode['status']:
                        # switch mode succeed
                        threadVar.instance[device] = tmpInstance
                        print threadVar.fmtText % (device,'Login Succeed:'+typeName)
                    else:
                        # switch mode failed
                        threadVar.logData['status'] = False
                        threadVar.logData['failedIp'][device] = 'Enable Failed:'+tmpPrivilegeMode['errLog']
                        print threadVar.fmtError % (device,'Enable Failed:'+tmpPrivilegeMode['errLog'])
                else:
                    # login failed
                    threadVar.logData['status'] = False
                    threadVar.logData['failedIp'][device] = 'Login Failed:'+tmpLogin['errLog']
                    print threadVar.fmtError % (device,'Login Failed:'+tmpLogin['errLog'])
            except Exception as e:
                # import failed
                threadVar.logData['status'] = False
                threadVar.logData['failedIp'][device] = 'Class Error:'+str(e)
                print threadVar.fmtError % (device,'Class Error:'+str(e))
        else:
            threadVar.logData['status'] = False
            threadVar.logData['failedIp'][device] = 'DB Error:'+deviceInfo['errLog']
            print threadVar.fmtError % (device,'DB Error:'+deviceInfo['errLog'])
        db.close()
    else:
        # mysql connect failed
        threadVar.logData['status'] = False
        threadVar.logData['failedIp'][device] = 'DB Connect Error:'+connect['errLog']
        print threadVar.fmtError % (device,'DB Connect Error:'+connect['errLog'])
