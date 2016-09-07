#!/usr/bin/env python
#coding:utf-8


serviceNet = {
	# device firewall  10.11.199.178  Including the network range
	"network":[
				"10.100.0.0/14",
				"10.104.0.0/16",
				"172.17.0.0/22",
		],
	"device":"10.11.199.178",
	"net":"service-net",
}

serviceCore = {
	# Core area. from 10.11.199.2，run 'show ip route connected' 
	"network":[],
	"device":"10.11.199.199",
	"net":"service-core",
}

serviceDMZ = {
	# DMZ area. from 10.11.199.197，run 'display ip interface brief'.
	"network":[],
	"device":"10.11.199.199",
	"net":"service-dmz"
}



serviceCE = {
	# CE area,from 11.11.11.68,run 'show route'
	"network":[],
	"device":"11.11.11.58",
	"net":"service-ce",
} 

serviceInternet = {
	# Internet network
	"network":["0.0.0.0",], # 0.0.0.0 and Public IP
	"device":"11.11.11.42",
	"net":"service-internet"
}
