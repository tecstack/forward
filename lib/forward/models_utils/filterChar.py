#!/usr/bin/env python
import re
def filterChar(func):
	def wrapper(cmd):
		data=func(cmd)
		_data=""
		for line in data['content'].split('\r\n'):
			_line=re.sub('\\x1b\[7m\-\-More\-\-\\x1b\[m\\r+(\\x1b\[K)?','',line)	#delete --More--
			_data=str(_line)+'\r\n'
		data['content']=_data
		return data
	return wrapper

