#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Class for mysql control.
forward database device_info DESC:
+----------------+----------+------+-----+---------+-------+
| Field          | Type     | Null | Key | Default | Extra |
+----------------+----------+------+-----+---------+-------+
| ip             | char(15) | NO   |     | NULL    |       |
| username       | char(20) | NO   |     | NULL    |       |
| password       | longtext | NO   |     | NULL    |       |
| deviceType     | char(20) | NO   |     | NULL    |       |
| loginMethod    | char(20) | NO   |     | NULL    |       |
| secondPassword | longtext | YES  |     | NULL    |       |
| deviceNumber   | char(30) | NO   |     | NULL    |       |
| port           | int(5)   | NO   |     | NULL    |       |
+----------------+----------+------+-----+---------+-------+

forward database userlist DESC:
+----------+----------+------+-----+---------+-------+
| Field    | Type     | Null | Key | Default | Extra |
+----------+----------+------+-----+---------+-------+
| username | char(20) | NO   |     | NULL    |       |
| auth     | int(5)   | NO   |     | NULL    |       |
+----------+----------+------+-----+---------+-------+

forward database cmdlist DESC:
+---------+-----------+------+-----+---------+-------+
| Field   | Type      | Null | Key | Default | Extra |
+---------+-----------+------+-----+---------+-------+
| command | char(100) | NO   |     | NULL    |       |
| auth    | int(5)    | NO   |     | NULL    |       |
+---------+-----------+------+-----+---------+-------+
"""

import MySQLdb
from forward.models_utils.forwardCrypt import CRYPT

class MYSQLDB:
    def __init__(self,host,user,passwd,db,port,publicKeyPath,privateKeyPath):
        self.njInfo = {
            'status':True,
            'errLog':'',
            'content':{}
        }
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.port = int(port)
        self.crypt = CRYPT(publicKeyPath,privateKeyPath)
        if not self.crypt.njInfo['status']:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = self.crypt.njInfo['errLog']

    def connect(self):
        # Connect to the mysqldb
        try:
            self.connect = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db,port=self.port)
            self.cursor = self.connect.cursor()
        except Exception as e:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = str(e)
        return self.njInfo
    def execute(self,sql):
        # Try to execute the sql command
        try:
            self.cursor.execute(sql)
            # return tuple:(('172.17.0.2', 'xx', 'xx', 'xx', 'xx', '', 'xx', 22L),)
            self.njInfo['content']['fetchall'] = self.cursor.fetchall()
        except Exception as e:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = str(e)
        return self.njInfo
    def getDeviceInfo(self,table,ip):
        # [forward] Get device infomations with the ip address
        sql = "SELECT * FROM %s WHERE ip = '%s';" % (table,ip)
        result = self.execute(sql)
        if result['status']:
            # Execute succeed
            row = result['content']['fetchall']
            if (len(row) != 1):
                # [Not found] or [Found more than 1 device info with the same ip]
                self.njInfo['status'] = False
                self.njInfo['errLog'] = 'Error: [Not found] or [Found more than 1 device info with the same ip]'
            else:
                # (('172.17.0.2', 'root', 'xx', 'bclinux7', 'sshv2', '', 'bc02', 22L),)
                self.njInfo['content']['ip'] = row[0][0]
                self.njInfo['content']['username'] = row[0][1]
                self.njInfo['content']['password'] = row[0][2]
                self.njInfo['content']['deviceType'] = row[0][3]
                self.njInfo['content']['loginMethod'] = row[0][4]
                self.njInfo['content']['secondPassword'] = row[0][5]
                self.njInfo['content']['deviceNumber'] = row[0][6]
                self.njInfo['content']['port'] = row[0][7]

                self.crypt.decrypt(self.njInfo['content']['password']) #decrypt the password
                if self.crypt.njInfo['status']:
                    self.njInfo['content']['password'] = self.crypt.njInfo['content']['plaintext']
                else:
                    self.njInfo['status'] = False
                    self.njInfo['errLog'] = self.crypt.njInfo['errLog']

                self.crypt.decrypt(self.njInfo['content']['secondPassword']) #decrypt the password
                if self.crypt.njInfo['status']:
                    self.njInfo['content']['secondPassword'] = self.crypt.njInfo['content']['plaintext']
                else:
                    self.njInfo['status'] = False
                    self.njInfo['errLog'] = self.crypt.njInfo['errLog']
        else:
            # Execute failed
            self.njInfo['status'] = False
            self.njInfo['errLog'] = 'Get device info failed: '+str(result['errLog'])
        return self.njInfo

    def getUserLevel(self,table,username):
        # [forward] Get user auth level with username
        sql = "SELECT * FROM %s WHERE username = '%s';" % (table,username)
        result = self.execute(sql)
        if result['status']:
            # Execute succeed
            row = result['content']['fetchall']
            if (len(row) != 1):
                # [Not found] or [Found more than 1 user with the same username]
                self.njInfo['status'] = False
                self.njInfo['errLog'] = 'Error: [Not found] or [Found more than 1 user with the same username]'
            else:
                # (('forward',0),)
                self.njInfo['content']['userLevel'] = row[0][1]
        else:
            # Execute failed
            self.njInfo['status'] = False
            self.njInfo['errLog'] = 'Get user level failed: '+str(result['errLog'])
        return self.njInfo
    def getUserStatus(self,table,username):
        # [forward] Get user status with username
        sql = "SELECT is_active FROM %s WHERE username = '%s';" % (table,username)
        result = self.execute(sql)
        if result['status']:
            # Execute succeed
            row = result['content']['fetchall']
            if (len(row) != 1):
                # [Not found] or [Found more than 1 user with the same username]
                self.njInfo['status'] = False
                self.njInfo['errLog'] = 'Error: [Not found] or [Found more than 1 user with the same username]'
            else:
                # (('forward',0),)
                statusCode=int(row[0][0]) # 1 is a valid , 0 is not valid
                if statusCode == 1:
                    userStatus = True
                else:
                    userStatus = False
                self.njInfo['content']['userStatus'] = userStatus
        else:
            # Execute failed
            self.njInfo['status'] = False
            self.njInfo['errLog'] = 'Get user status failed: '+str(result['errLog'])
        return self.njInfo

    def getCommandList(self,table):
        # [forward] Get command list (including auth cmd and ban cmd)
        # banList = ['rm','delete','reboot']
        # authList = ['show tech']
        sql = "SELECT * FROM %s;" % (table)
        result = self.execute(sql)
        if result['status']:
            # Execute succeed
            row = result['content']['fetchall']
            # (('remove',0),('delete',0),('mv',1))
            authList = []
            banList = []
            for cmd in row:
                if cmd[1] == 0:
                    # ban cmd
                    banList.append(cmd[0])
                elif cmd[1] == 1:
                    # auth cmd
                    authList.append(cmd[0])
            self.njInfo['content']['authList'] = authList
            self.njInfo['content']['banList'] = banList
        else:
            # Execute failed
            self.njInfo['status'] = False
            self.njInfo['errLog'] = 'Get cmd list failed: '+str(result['errLog'])
        return self.njInfo


    def close(self):
        self.connect.close()
