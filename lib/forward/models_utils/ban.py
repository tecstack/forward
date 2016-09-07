#!/usr/bin/evn python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Command ban function.
Execute before classInstance.execute()
"""

import re

class BAN:
    userLevel = ''
    authList = ''
    banList = ''

def init(userLevel,userStatus,authList,banList):
    BAN.userLevel = userLevel
    BAN.userStatus = userStatus
    BAN.authList = authList
    BAN.banList = banList

def ban(method):
    def ban(*args):
        isIntercept=False
        data = {
            'status' : True,
            'errLog' : '',
            'content' : {}
        }
        #if args[1] in BAN.banList:
        for banCommandRegular in BAN.banList:
            if re.search(banCommandRegular,args[1],flags=re.IGNORECASE):
                data['status'] = False
                data['errLog'] = 'Forward: You are not allowed to execute [%s]' % args[1]
                isIntercept=True
                break
        #elif args[1] in BAN.authList:
        for authCommandRegular in BAN.authList:
            # auth cmd, only auth user can execute
            if re.search(authCommandRegular,args[1],flags=re.IGNORECASE):
            	if BAN.userLevel <= 1:
                	# admin or auth user
                        pass
           	else:
               	        # normal user
                        isIntercept=True
                        data['status'] = False
                        data['errLog'] = 'Forward: You are not allowed to execute [%s]' % args[1]
                break
        if not BAN.userStatus: # user Status
                isIntercept=True
                data['status'] = False
                data['content'] = 'Forward: The current user has been locked !'
        if not isIntercept:
            # normal cmd, access to everyone
            data = method(*args)
        return data
    return ban

def adminPermissionCheck(func):
        def wrapper(*args):
                data = {
                         'status' : False,
                         'errLog' : '',
                         'content' : {}
                }
                if BAN.userLevel <= 1: # is admin or super admin
                        pass
                else:
                        # is general user ,not allwed
                        data['status'] = False
                        data['errLog'] = "You have no permission to execute!"
                        return data
                return func(*args)
        return wrapper
