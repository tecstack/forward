#!/usr/bin/env python
#coding:utf8
import sys,re,os
from forward.models_utils.forwardError import ForwardError
class FGFirewallPolicyAdmin(object):
	""" fg3040 inherit this class"""

	def _configFirewallMode(self,command=""):
		"""
		enter config firewall mode
		"""
		njInfo = {
                        "status":False,
                        "content":"",
                        "errLog":"",
                }
		self.shell.send('{command}\n'.format(command=command))
		buff = ''
		self.isConfigMode = False
		while not re.search(self.basePrompt,buff.split('\n')[-1]): # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
			try:
				try:
					buff += self.shell.recv(1024)
				except:
					raise ForwardError('Receive timeout [%s]' %(buff))
				self.getPrompt()	# renew get host prompt
				njInfo["status"] = True
				self.isConfigMode = True
				# successed
			except Exception,e:
				njInfo["errLog"] = str(e)
				njInfo["status"] = False
				break
		return njInfo

	def _editMode(self,name=""):
		njInfo = {
                        "status":False,
                        "content":"",
                        "errLog":"",
                }
		self.send("edit {name}\n".format(name = name))  #execute edit command
		buff = ''
		while not re.search(self.basePrompt,buff.split('\n')[-1]): # When after switching mode, the prompt will change, it should be based on basePrompt to check and at last line
			try:
				try:
					buff += self.shell.recv(1024)
				except:
					raise ForwardError('Receive timeout [%s]' %(buff))
				self.getPrompt()	# renew get host prompt
				njInfo["status"] = True
				self.isConfigMode = True
				# successed
			except Exception,e:
				njInfo["errLog"] = str(e)
				njInfo["status"] = False
				break
		return njInfo
		
	def createAddressName(self,addressName = '',interface = '',ip = ''):
		"""
		- param addressName: addressName
		- param interface:   interface
		- param ip:	    First of all, a range to determine whether the IP parameters, if it is a range of IP, execute the first way, otherwise the second execution
		"""
		njInfo = {
                        "status":False,
                        "content":"",
                        "errLog":"",
                }
                try:
			if len(addressName) == 0 or len(interface) == 0 or len(ip) == 0:
				raise ForwardError('Must specify all effective parameters')
			mode = self._configFirewallMode(command="config firewall address")
			if not mode ['status']:
				raise ForwardError(mode['errLog'])
			#self.shell.execute("edit {addressName}".format(addressName = addressName))
			editMode = self._editMode(addressName) # enter edit mode
			if not editMode["status"]:
				raise ForwardError(editMode['errLog'])
			# check ip type
			if re.search('\-',interface):
				# first method
				# ip range
				# start ip
				startIP = ip.split('-')[0]
				endIP   = ip.split('-')[1]
				self.execute("set associated-interface {interface}".format(interface =  interface))
				self.execute("set type iprange")
				self.execute("set start-ip {startIP}".format(startIP = startIP))
				self.execute("set end-ip {endIP}".format(startIP = endIP))
			elif re.search('/',interface):
				# second method
				# a ip
				self.execute("set associated-interface {interface}".format(interface = interfacde))
				self.execute("set subnet {ip}")
			exitMode = self._exitConfigMode()
			if not exitMode["status"]: #exit config mode, go to the privileged mode
				raise Forward(editMode['errLog'])
			njInfo["status"] = True
			# successed
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo

	def _deleteConfig(self,modeCommand="",deleteName=""):
		"""
		- param modeCommand:	enter config firewall mode's command
		- deleteName:		delete any-name
		"""
		njInfo = {
                        "status":False,
                        "content":"",
                        "errLog":"",
                }
		try:
			mode = self._configFirewallMode(command=modeCommand) # enter config firewall mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			data = self.execute("delete {deleteNme}".format(deleteName = deleteName))
			if not data["status"]:
				raise ForwardError(data["errLog"])
			exitMode = self._exitConfigMode()
			if not exitMode["errLog"]: # exit config mode, go to the privileged mode
				raise Forward(exitMode['errLog']) 
			njInfo["status"] = True
			# successed
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo
	
	def deleteAddressName(self,addressName=""):
		return self._deleteConfig(modeCommand="config firewall address",deleteName=addressName)

	def deleteServiceName(self,serviceName=""):
		return self._deleteConfig(modeCommand="config firewall service custom",deleteName=serviceName)
		
	def deleteFirewallPolicy(self,id=""):
		return self._deleteConfig(modeCommand="config firewall policy",deleteName=id)
		

	def createServiceName(self,serviceName="",protocol="TCP",port=''):
		"""
		create service name
		- param protocol:	TCP/UDP
		- param port:		22 or 22-33
		- param serviceName	any-name
		"""
		njInfo = {
                        "status":False,
                        "content":"",
                        "errLog":"",
                }
		try:
			# parameter check protocol
			if (not protocol == "TCP") and (not protocol== "UDP"):
				raise ForwardError("protocol's value must be a TCP or UDP")
			# parameter check protocol type
			if protocol == "TCP":
				portRange="TCP"
			else:
				portRange="UDP"
			mode = self._firewallServiceNameMode(command = "config firewall service custom") # enter config firewall mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			mode = self.editMode(serviceName) # enter edit name mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			# first  command
			data = self.execute("set protocol TCP/UDP/SCTP")
			if not data["status"]:
				raise ForwardError(data["errLog"])
			if protocol == "TCP":
				portRange="TCP"
			else:
				portRange="UDP"
			# second command
			data = self.execute("set {portRange} {port}".format(portRange=portRange,port=port))
			if not data["status"]:
				raise ForwardError(data["errLog"])
			mode = self._exitConfigMode() # exit config mode
			if not mode["status"]:
				raise ForwardError(mode["errLog"])
			njInfo["status"] = True
			# successed
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo

	def createFirewallPolicy(self,id="",sourceInterface="",destInterface="",sourceAddressName="",destAddressName="",serviceName="",description=""):
		"""
		create firewall policy
		- param id:			id,must be
		- param sourceInterface:	any,must be
		- param destInterface:		any,must be
		- param sourceAddressName:	any,must be
		- param destAddressName:	any,must be
		- param serviceName:		any,must be
		- param description:		can  be temp
		
		"""
		njInfo = {
                        "status":False,
                        "content":"",
                        "errLog":"",
                }
		try:
			# parameters check
			if len(id) == 0 or len(sourceInterface) == 0 or len(destInterface) == 0 or  len(sourceAddressName) == 0 or len(destAddressName) == 0 or len(serviceName) == 0:
				raise ForwardError('''Has not yet been parameters must be specified,(id="",sourceInterface="",destInterface="",sourceAddressName="",destAddressName="",serviceName="")''')
			mode = self._configFirewallMode(command="config firewall policy") # enter config firewall mode
			if not mode["status"]:
				raise ForwardError(mode['errLog'])
			editMode =  self._editMode(self,id) # enter edit mode
			if not editMode["status"]:
				raise ForwardError(editMode['errLog'])
			# command
			data = self.shell.execute("set srcintf {sourceInterface}".format(sourceInterface = sourceInterface))
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set dstintf {destInterface}".format(destInterface = destInterface))
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set srcaddr {sourceAddressName}".format(sourceAddressName = sourceAddressName))
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set srcaddr {sourceAddressName}".format(sourceAddressName = sourceAddressName))
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set srcaddr {destAddressName}".format(destAddressNmae =  destAddressName))
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set action accept")
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set schedule always") 
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			data = self.shell.execute("set service {serviceName}".format(serviceName = serviceName))
			if not data["status"]:
				raise ForwardError(data['errLog'])
			# command
			# description can be temp
			if not len(description) == 0:
				data = self.shell.execute("set comments {description}".format(description = description))
				if not data["status"]:
					raise ForwardError(data['errLog'])
			exitMode = self._exitConfigMode() # exit config firewall mode
			if not exitMode["status"]:
				raise ForwardError(exitMode["errLog"])
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo

	
