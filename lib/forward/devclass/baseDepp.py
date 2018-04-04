#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for Depp.
Author: Cheung Kei-chuen
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASEDEPP(BASESSHV2):
    """This is a manufacturer of depp, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def createIPObject(self, name, ip=None, url=None, username=None, password=None):
        # load module of suds.
        from suds.client import Client
        # create a ip or ip-range
        """
        parameter name    : str type, any
        parameter ip      : str type, ip address, such as 10.0.0.1  or  10.0.0.100-10.0.0.200
        parameter url     : str type, webservice URL
        parameter username: str type, device's username,for authentiction
        parameter password: str typedevice's password,for authentication
        """
        result = {
            'status': False,
            'content': '',
            'errLog': ''
        }
        # parameters check
        if ip is None or url is None:
            raise IOError("Specify IP and url parameters.")
        if re.search("\/", ip):
            # for 10.0.0.1/32
            ip = "{ip}/32".format(ip.split("/")[0])
        elif re.search("\-", ip):
            # The other one is 10.0.0.100-10.0.200,remove mask
            ip = re.sub("\/[0-9]+", "", ip)
        try:
            # connect to url
            client = Client(url, username=username, password=password)
        except Exception, e:
            result["errLog"] = "[Forward Error] Connected to {url} was\
                                failure, reason: {err}".format(err=str(e), url=url)
            return result
        try:
            result = client.service.addAddrObj(**{"name": name, "ip": ip})
            result["status"] = True
        except Exception, e:
            num = e.message[0]
            if num == 401:
                result["errLog"] = "username or password invalid."
            elif num == 506:
                result["errLog"] = "Specify parameters error,or the configuration-name already exist."
            else:
                result["errLog"] = "Unknow error."
        return result

    def createServiceObject(self, name, url=None, protocol=None, sRange=None,
                            dRange=None, vsysName="PublickSystem", username=None, password=None):
        # load module of suds.
        from suds.client import Client
        """
        create a service object
        parameter name: str type, any
        parameter url : str type, webservice url
        parameter protocol : str type, tcp,udp or icmp
        parameter sRange   : str type, such as 90-91
        parameter dRange   : str type, suce as 100-101
        parameter vsysName : str type, default is PublickSystem
        parameter username : str type, device's username
        parameter password : str type, device's password
        """
        result = {
            'status': False,
            'content': '',
            'errLog': ''
        }
        # parameters check.
        if protocol is None or sRange is None or dRange is None or url is None:
            raise IOError("Specify url,protocol,url,sRange and dRange parameters.")
        # Protocol code conversion
        if re.search("tcp", protocol, re.IGNORECASE):
            protocolNumber = 6
        elif re.search("udp", protocol, re.IGNORECASE):
            protocolNumber = 17
        elif re.search("icmp", protocol, re.IGNORECASE):
            protocolNumber = 1
        else:
            result["errLog"] = "Unkow protocol"
            return result
        try:
            # connect to url
            client = Client(url, username=username, password=password)
        except Exception, e:
    	    result["errLog"] = "[Forward Error] Connected to {url} was\
                                failure, reason: {err}".format(err=str(e), url=url)
        p = {"name": name,
             "protocol": protocolNumber,
             "sourcePortRange": sRange,
             "destinationPortRange": dRange,
             "vsysName": vsysName}
        try:
            client.service.createServerObject(p)
            result["status"] = True
        except Exception, e:
            num = e.message[0]
            if num == 401:
                result["errLog"] = "username or password invalid."
            elif num == 506:
                result["errLog"] = "Specify parameters error,the configuration-name already exist,or vsysName not exist"
            else:
                result["errLog"] = "Unknow error."
        return result

    def createSecurityPolicy(self, name, action=None, url=None,
                             sZone=None, dZone=None,
                             sIPType=None, sIPName=None,
                             dIPType=None, dIPName=None,
                             serviceType=None, serviceName=None,
                             vsysName="PublickSystem",
                             username=None, password=None):
        from suds.client import Client
        result = {
            'status': False,
            'content': '',
            'errLog': ''
        }
        # default parameters
        # default sort 1
        position = 1
        # default should  be true
        enabled = "true"
        """
        Create security policy
        parameter name : str type, any
        parameter vsysName : str type, it must exist ,such as PublicSystem
        parameter position : int type, sort
        parameter enable   : str type, true/false
        parameter sZone    : str type, source security zone,must be exist
        parameter dZone    : str type, destination security zone,must be  exist
        parameter action   : str type, allow/deny
        parameter sIPType  : str type, source ip object name, single/group
        parameter sIPName  : str type, source ip object name ,must be exist
        parameter dIPType  : str type, destination ip object name, single/group
        parameter dIPName  : str type, destination ip object name ,must be exist
        parameter serviceType  : str type, service object,single/group
        parameter serviceName  : str type, service object name ,must be exist

        """
        # parameters check
        if action is None or (not action == "allow") or (not action == "deny"):
            result["errLog"] = "[Forward Error] Please specify the value of the parameter action as allow/deny."
            return result
        if sZone is None:
            result["errLog"] = "[Forward Error] Please specify a parameter for the sZone."
            return result
        if dZone is None:
            result["errLog"] = "[Forward Error] Please specify a parameter for the dZone."
            return result
        if sIPType is None or (not sIPType == "single") or (not sIPType == "group"):
            result["errLog"] = "[Forward Error] Please specify a parameter\
                                for the sIPType,and value is single/group"
            return result
        if sIPName is None:
            result["errLog"] = "[Forward Error] Please specify a parameter\
                                for the sIPName,and value is single/group"
            return result
        if dIPType is None or (not dIPType == "single") or (not dIPType == "group"):
            result["errLog"] = "[Forward Error] Please specify a parameter\
                                for the dIPType,and value is single/group"
            return result
        if dIPName is None:
            result["errLog"] = "[Forward Error] Please specify a parameter for the dIPName."
            return result
        if serviceType is None or (not serviceType == "single") or (not serviceType == "group"):
            result["errLog"] = "[Forward Error] Please specify a parameter\
                                for the serviceType,and value is single/group"
            return result
        if serviceName is None:
            result["errLog"] = "[Forward Error] Please specify a parameter for the serviceName."
            return result
        # Parameter transformation
        if sIPType == "single":
            sIPTypeCode = "0"
        else:
            sIPTypeCode = "1"
        if dIPType == "single":
            dIPTypeCode = "0"
        else:
            dIPTypeCode = "1"
        if serviceType == "single":
            serviceTypeCode = "0"
        else:
            serviceTypeCode = "1"
        try:
            # connect to url
            client = Client(url, username=username, password=password)
        except Exception, e:
    	    result["errLog"] = "[Forward Error] Connected to {url} was\
                                failure, reason: {err}".format(err=str(e), url=url)
            return result
        p = {
            "name": name,
            "vsysName": vsysName,
            "position": position,
            "enabled": enabled,
            "action": action,
            "sourceSecurityZone": sZone,
            "destinationSecurityZone": dZone,
            "sourceIpObjects": [
                {
                    "type": sIPTypeCode,
                    "name": sIPName,
                }
            ],
            "destinationIpObjects": [
                {
                    "type": dIPTypeCode,
                    "name": dIPName,
                }
            ],
            "serverObjects": [
                {
                    "type": serviceTypeCode,
                    "name": serviceName
                }
            ]
        }
        try:
            result = client.service.createSecurityPolicy(p)
            result["status"] = True
        except Exception, e:
            num = e.message[0]
            if num == 401:
                result["errLog"] = "username or password invalid."
            elif num == 506:
                result["errLog"] = "Specify parameters error,or the configuration-name already exist."
            else:
                result["errLog"] = "Unknow error."
        return result
