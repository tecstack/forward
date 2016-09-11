#!/usr/bin/evn python
#coding:utf-8
"""     It applies only to models of network equipment  mx960
        See the detailed comments C6506.py
"""
import sys,re,os
from forward.models_utils.forwardError import ForwardError
from forward.models_utils.deviceListSplit import DEVICELIST
class Bandwidth(object):
	def __init__(self,shell = '', ip = '',bandwidth = ''):
		device = DEVICELIST(['112.33.0.0-112.33.10.255','221.176.53.0-221.176.54.255']) # mobile cloud IP
		self.ipRange = device.getIpList()
		self.targetIP = ip # bind ip
		self.shell = shell # device shell
		self.bandwidth = bandwidth # bind bandwidth
		self.resolvTermAndIP()
		self.getTerm()
		self.checkBandwidthCommand="""show configuration firewall family inet prefix-action Action-Name-{bandwidth}M""".format(bandwidth=self.bandwidth) # wheather check bandwidth exist
		self.checkIPAndBandwidthCommand1="""show configuration firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} then prefix-action""".format(ip=self.ip)

	def getTerm(self):
		# Get IP terminal number
		for term in self.termAndIP.keys():
			if self.ip in self.termAndIP[term]:  # find it
				self.termNumber=term
				break
				
	
	def resolvTermAndIP(self):
		term0=DEVICELIST(["221.176.53.0-221.176.53.255"])
		term1=DEVICELIST(["221.176.54.0-221.176.54.255"])
		term3=DEVICELIST(["112.33.0.0-112.33.0.255"])
		term4=DEVICELIST(["112.33.1.0-112.33.1.255"])
		term5=DEVICELIST(["112.33.2.0-112.33.2.255"])
		term6=DEVICELIST(["112.33.3.0-112.33.3.255"])
		term7=DEVICELIST(["112.33.4.0-112.33.4.255"])
		term8=DEVICELIST(["112.33.5.0-112.33.5.255"])
		term9=DEVICELIST(["112.33.6.0-112.33.6.255"])
		term10=DEVICELIST(["112.33.7.0-112.33.7.255"])
		term11=DEVICELIST(["112.33.8.0-112.33.8.255"])
		term12=DEVICELIST(["112.33.9.0-112.33.9.255"])
		term13=DEVICELIST(["112.33.10.0-112.33.10.255"])
			
		
		self.termAndIP = {
			"0":term0.getIpList(),
			"1":term1.getIpList(),
			"3":term3.getIpList(),
			"4":term4.getIpList(),
			"5":term5.getIpList(),
			"6":term6.getIpList(),
			"7":term7.getIpList(),
			"8":term8.getIpList(),
			"9":term9.getIpList(),
			"10":term10.getIpList(),
			"11":term11.getIpList(),
			"12":term12.getIpList(),
			"13":term13.getIpList(),
		}

	def ipStatus(self):
		# To judge whether the IP is legal
		njInfo={
			"content":"",
			"errLog":"The specify ip is not valid",
			"status":False
		}
		if self.targetIP in self.ipRange:
			self.getTerm() # self.termNumber
			njInfo["status"]=True
		return njInfo

	def createBandwidth(self):
		modeData = self.shell._configMode()
		if modeData["status"]:
			# switch to config mode success
			self.shell.execute("set firewall family inet prefix-action Action-Name-{bandwidth}M policer Policer-CIDC-T-BW-11100000-{bandwidth}M".format(bandwidth=self.bandwidth))
			self.shell.execute("set firewall family inet prefix-action Action-Name-{bandwidth}M filter-specific")
			self.shell.execute("set firewall family inet prefix-action Action-Name-{bandwidth}M subnet-prefix-length 24")
			self.shell.execute("set firewall family inet prefix-action Action-Name-{bandwidth}M source-prefix-length 32")
			self.shell.execute("set firewall policer Policer-CIDC-T-BW-11100000-{bandwidth}M if-exceeding bandwidth-limit {bandwidth}m".format(bandwidth=self.bandwidth))
			self.shell.execute("set firewall policer Policer-CIDC-T-BW-11100000-{bandwidth}M if-exceeding burst-size-limit 512k".format(bandwidth=self.bandwidth))
			self.shell.execute("set firewall policer Policer-CIDC-T-BW-11100000-{bandwidth}M then discard".format(bandwidth=self.bandwidth))
			# commit
			commitData = self._commit()
			if commitData["status"]:
				# commit success
				data = self._exitConfigMode() # exit config mode
				if not  data["status"]:
					# exit failed
					raise ForwardError(data["errLog"])
				# Check whether bandwidth to create success
				data = self.bandwidthConfigExist()
				if  not data["status"]:
					# create bandwidth ,but failed
					data["errLog"] = "create bandwidth {bandwidth}M is failed".format(bandwidth=self.bandwidth)
				else:
					pass
					# create bandwid is successed.
			else:
				# commit failed
				data = commitData
		else:
			# failed
			data = modeData
		return data
		

	def bandwidthConfigExist(self):
		#  wheather  check bandwidth config exist
		njInfo = {
			"content":"",
			"errLog":"The specify bandwidth config is not exist.",
			"status":False
		}
		result = self.shell.execute(self.checkBandwidthCommand)
		if result["status"]:
			content = result["content"]
			if re.search("""policer Policer\-CIDC\-T\-BW\-[0-9]{3,}\-%sM;"""% (self.bandwidth) ,content):
				njInfo["status"] = True
				# bandwidth config is exist
			else:
				# bandwidth config is not exist
				njInfo["status"] = False
		else:
			raise ForwardError(result["errLog"])
		return njInfo
	def ipAndBandwidthExist(self):
		njInfo = {
			"content":"",
			"errLog":"",
			"status":False
		}
		try:
			data = self.shell.execute(self.checkIPAndBandwidthCommand) # check it
			if data["status"]:
				if re.search("""prefix\-action Action\-Name\-%sM""" % self.bandwidth,data["content"]):
					# exist bind
					# get term num
					# check again
					data = self.shell.execute("""show configuration firewall filter Policer-For-Each-Address term {term} |  match {ip}/32""".format(term=self.termNumber,ip=self.ip))
					if data["status"]:
						if re.search("%s/32 except" % (self.ip),data["content"]  ):
							# success
							njInfo["status"] = True
						else:
							raise ForwardError("not exist bind")
					else:
						raise ForwardError(data["errLog"])
					njInfo["status"] = True
		
				else:
					raise ForwardError("not exist bind")
					# not exist bind
				
			else:
				raise FowardError(data["errLog"])
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo

	def bindIPAndBandwidth(self):
		njInfo={
			"content":"",
			"errLog":"",
			"status":False
		}
		try:
			data = self._configMode()
			if data["status"]:
				# switch to config mode successed
				self.shell.execute("""set firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} from address {ip}/32""".format(ip=self.ip))
				self.shell.execute("""set firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} then forwarding-class queue_2""".format(ip=slef.ip))
				self.shell.execute("""set firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} then accept""".format(ip=self.ip))
				self.shell.execute("""set firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} then prefix-action Action-Name-{bandwidth}M""".format(bandwidth=self.bandwidth,ip=self.ip))
				self.shell.execute("""set firewall filter Policer-For-Each-Address term {term}  from address {ip}/32 except""".format(ip=self.ip,term=self.termNumber))
				self.shell.execute("""insert firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} before term {term}""".format(term=self.termNumber,ip=self.ip))
				# commit
				data = self._commit()
				if data["status"]:
					# commit success
					data = self._exitConfigMode()
					if data["status"]:
						data =  self.ipAndBandwidthExist() # check it
						if data["status"]:
							njInfo["status"] = True
							# bind successed
						else:
							raise ForwardError("bind ip and bandwidth failed,Error:",data["errLog"])
					else:
						raise ForwardError(data["errLog"])			
				else:
					raise ForwardError(data["errLog"])			
			else:
				raise ForwardError(data["errLog"])
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo
	def modifyIPAndBandwidth(self):
		njInfo={
			"content":"",
			"errLog":"",
			"status":False
		}
		try:
			data=self.shell._configMode()
			if data["status"]:
				# switch to config mode successed
				self.shell.execute("""set firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip} then prefix-action Action-Name-{bandwidth}M""".format(bandwidth=self.bandwidth,ip=self.ip))
				data = self._commit() # commit
				if data["status"]:
					data = self._exitConfigMode()
					if not  data["status"]:
						# exit failed
						raise ForwardError(data["errLog"])
					else:
						# Check whether the binding is successful
						data = self.ipAndBandwidthExist()
						if data["status"]:
							# modify successed
							njInfo["status"] = True
						else:
							raise ForwardError("Modify the binding failed")
				else:
					# commit failed
					raise ForwardError(data["errLog"])
				
			else:
				raise ForwardError(data["errLog"])
		except Exception,e:
			njInfo["status"] = False
			njInfo["errLog"] = str(e)
		return njInfo
			
	def bindBandwidth(self):
		njInfo={
			"content":"",
			"errLog":"",
			"status":False
		}
		try:
			ipIsTrue=self.ipStatus()
			if ipIsTrue["status"]:
				# ip is invalid
				if self.bandwidthConfigExist()["status"]:
					# bandwidth config is exist
					pass
				else:
					# bandwidth config is not exist,then create it
					data = self.createBandwidth()
					if data["status"]:
						# create bandwidth is successed
						# check ip and bandwidth is not bind
						data = self.ipAndBandwidthExist()
						if data["status"]:
							# Have binding, should modify it
							data = self.modifyIPAndBandwidth()
							if data["status"]:
								# successed
								njInfo["status"] = True
							else:
								raise ForwardError(data["errLog"])
						else:
							# Have not binding, chould create it
							data = self.bindIPAndBandwidth()
							if data["status"]:
								# successed
								njInfo["status"] = True
							else:
								raise ForwardError(data["errLog"])
					else:
						# failed
						raise ForwardError(data["errLog"])
			else:
				# ip is not valid
				raise ForwardError(ipIsTrue["errLog"])
		except Exception,e:
				njInfo["status"] = False
				njInfo["errLog"] = str(e)
		return njInfo
			
			
			
		
	def deleteBindIPAndBandwidth(self):
		njInfo={
			"content":"",
			"errLog":"",
			"status":False
		}
		try:
			ipIsTrue = self.ipStatus() 
			if ipIsTrue["status"]:
				data = self._configMode()
				if data["status"]:
					self.shell.execute("""delete firewall filter Policer-For-Each-Address term Filter-Term-Name-{ip}""".format(ip=self.ip))
					self.shell.execute("""delete firewall filter Policer-For-Each-Address term {term} from address {ip}/32""".format(ip=self.ip,term=self.termNumber))
					data = self._commit() # commit
					if data["status"]:
						# commit succcessed
						data =  self._exitConfigMode()
						if data["status"]:
							njInfo["status"] = True
						else:
							raise ForwardError(data["errLog"]) #  failed.
					else:
						raise ForwardError(data["errLog"]) #  failed.
				else:
					raise ForwardError(data["errLog"]) # switch to config mode failed.
					
				
			else:
				raise ForwardError("The specify ip is not valid.")
		except Exception,e:
				njInfo["status"] = False
				njInfo["errLog"] = str(e)
		return njInfo
