#!/usr/bin/env python
#coding:utf-8
"""
-----Introduction-----
[Core][forward] Device class for USG Firewall function.
"""
import re,os,json,time,sys
from forward.models_utils.forwardError import ForwardError
class USGFirewallPolicyAdmin(object):
	"""USG1000 inherit this class"""
	def createAddressName(self,addressName = '',description = '',netIP = [],rangeIP = [],hostIP = []):
		"""
		- param addressName:	Must provide
		- param description:	Can be empty
		- param netIP:		netIP and rangeIP and hostIP, must choose one of them, or choose all.
		"""
		njInfo = {
			"status":False,
			"content":"",
			"errLog":"",
		}
		try:
			mode = self._configMode() #enter config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			if type(netIP) != type([]) or type(rangeIP) != type([]) or type(hostIP) != type([]):
				raise ForwardError("Specified argument must be a list")
			if len(addressName) == 0:
				raise ForwardError("Must be specified addressName")
			# create address name
			data = self.execute("address {addressName}".format(addressName=addressName))
			if not  data["status"]:
				raise ForwardError("create address-name failed:%s" % data["errLog"])
			# create description
			if len(description) != 0:
				data = self.execute("description {description}".format(description = description))
				if not data["status"]:
					raise ForwardError("create address-description failed: %s" % data["errLog"])
			njInfo["status"] = True
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		tmp = self._exitConfigMode() # exit config mode
		if not  tmp["status"]:
			njInfo = tmp
		return njInfo
		
	def deleteAddressName(self,addressName = ''):
		njInfo = {
			"status":False,
			"content":"",
			"errLog":"",
		}
		try:
			if len(addressName) == 0:
				raise ForwardError("Must be specified addressName")
			mode = self._configMode() #enter config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			# execute command
			data = self.execute("no address {addressName}".format(addressName = addressName))
			if not data["status"]:
				raise ForwardError("delete address-name failed: %s"%data["errLog"])
			njInfo["status"] = True
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo

	def modifyAddressName(self,**kws):
		return self.createAddressName(**kws)	

	#def createServiceName(self,serviceName = "",description = "",protocol="tcp",destPort=[]):
	def createServiceName(self,serviceName = "",description = "",tcp=False,udp=False,destTCPtPort=[],destUDPPort=[]):
		"""
		-tcp or udp		Must choose one of them
		- param serviceName:	Must provide
		- param description:	Can be empty
		- destUDPPort:		["22 23","80 81"]
		- destTCPPort:		["22 23","80 81"]
		eg:	(self,serviceName = "",description = "",tcp=False,udp=True,destTCPtPort=[],destUDPPort=["22 33","44 55"]):
		eg:	(self,serviceName = "",description = "",tcp=True,udp=False,destTCPtPort=["66 77","88"],destUDPPort=[]):
		"""
		njInfo = {
			"status":False,
			"content":"",
			"errLog":"",
		}
		try:
			# parameters check
			# serviceName
			if len(serviceName) == 0:
				raise ForwardError("Must be specifyied serviceName")
			# protocol
			if  (tcp is False ) and (udp is False):
				raise ForwardError("select tcp=True/udp=True")
			# dest-Port
			if tcp is True:
				if not type(destTCPPort) == type([]):
					raise ForwardError("destTCPPort must be as list")
			elif udp is True:
				if not type(destUDPPort) == type([]):
					raise ForwardError("destUDPPort must be as list")
			else:
				raise ForwardError("tcp or udp shoud True/False")
			
			mode = self._configMode() #enter config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			# create it
			data = self.execute("service {serviceName}".format(serviceName = serviceName))
			if not data["status"]:
				raise ForwardError("create service-name failed: %s"% data["status"])
			
			# create description
			data = self.execute("description {description}".format(description = description))
			if not data["status"]:
				raise ForwardError("create description failed: %s"% data["status"])
			# create tcp port
			if tcp is True:
				for port in destTCPPort:
					data = self.execute("tcp dest {port} source 1 65535".format(port = port))
					if not data["status"]:
						raise ForwardError("create destPort failed): %s"%data["errLog"])
			# create udp port
			if udp is True:
				for port in destUDPPort:
					data = self.execute("udp dest {port} source 1 65535".format(port = port))
					if not data["status"]:
						raise ForwardError("create destPort failed): %s"%data["errLog"])
			# create it succcessed
			njInfo["status"] = True
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		tmp = self._exitConfigMode() # exit config mode
		if not  tmp["status"]:
			njInfo = tmp
		return njInfo

	def deleteServiceName(self,serviceName=''):
		njInfo = {
			"status":False,
			"content":"",
			"errLog":"",
		}
		try:
			if len(serviceName) == 0:
				raise ForwardError("Must be specifyied serviceName")
			mode = self._configMode() #enter config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			# delete service name
			data = self.execute("not service {serviceName}".format(serviceName = serviceName))
			if not data["status"]:
				raise ForwardError("delete service-name failed: %s"%data["errLog"])
			# successed
			njInfo["status"] = True
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		tmp = self._exitConfigMode() # exit config mode
		if not  tmp["status"]:
			njInfo = tmp
		return njInfo

	def modifyServiceName(self,**kws):
		return self.createServiceName(**kws)
	def createFirewallPolicy(self,id = '',sourceInterface = '',destInterface = '',sourceAddressName = '',destAddressName = '',serviceName = '',description=''):
		njInfo = {
			"status":False,
			"content":"",
			"errLog":"",
		}
		try:
			# parameters check
			if len(id) == 0:
				raise ForwardError("Must be specifyied ID")
			if len(sourceInterface) == 0:
				raise ForwardError("Must be specifyied sourceInterface")
			if len(destInterface) == 0:
				raise ForwardError("Must be specifyied destInterface")
			if len(sourceAddressName) == 0:
				raise ForwardError("Must be specifyied sourceAddressName")
			if len(destAddressName) == 0:
				raise ForwardError("Must be specifyied destAddressName")
			if len(serviceName) == 0:
				raise ForwardError("Must be specifyied serviceName")
			mode = self._configMode() #enter config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			# create
			data =self.execute("policy {id} {sourceInterface destInterface} {sourceAddressName} {destAddressName}  {serviceName} always permit  description {description}".format(id = id,sourceInterface =  sourceInterface,destInterface = destInterface,serviceName = serviceName,description =  description))
			if not data["status"]:
				raise ForwardError("create firewall policy failed: %s" % data["errLog"])
			# create success
			njInfo["status"] = True
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		tmp = self._exitConfigMode() # exit config mode
		if not  tmp["status"]:
			njInfo = tmp
		return njInfo

	def deleteFirewallPolicy(self,id=''):
		njInfo = {
			"status":False,
			"content":"",
			"errLog":"",
		}
		try:
			if len(id) == 0:
				raise ForwardError("Must be specifyied ID")
			mode = self._configMode() #enter config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			# delete firewall policy
			data = self.execute("no policy {id}".format(id = id))
			if not data["status"]:
				raise ForwardError("delete firewall policy failed: %s"%data["errLog"])
			njInfo["status"] = True
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		tmp = self._exitConfigMode() # exit config mode
		if not  tmp["status"]:
			njInfo = tmp
		return njInfo
	
	def modifyFirewallPolicy(self,**kws):
		return self.createFirewallPolicy(**kws)
