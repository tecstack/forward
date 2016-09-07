#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core] python script.ConfigParse.
"""

import ConfigParser

class CONFIG:
	def __init__(self,conf='conf/forward.conf'):
		self.status = True
		self.configParse = ConfigParser.ConfigParser()
		if not self.configParse.read(conf):
			self.status = False
			self.errLog = "No such file or directory: %s" % (conf)
			raise TypeError(self.errLog)
	def getConfig(self,section,option):
		try:
			return self.configParse.get(section,option)
		except Exception as e:
			self.status = False
			self.errLog = e
			raise TypeError(self.errLog)
