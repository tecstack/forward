# coding:utf-8
# (c) 2015-2018, Wang Zhe <azrael-ex@139.com>, Zhang Qi Chuan <zhangqc@fits.com.cn>
#
# This file is part of Ansible
#
# Forward is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Forward is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
-----Introduction-----
[Core][forward] Device class for Baer.
"""
from forward.devclass.baseSSHV2 import BASESSHV2
import re


class BASEBAER(BASESSHV2):
    """This is a manufacturer of baer, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """
    def privilegeMode(self):
        # Switch to privilege mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        """
        *A:NFJD-PSC-S-SR7750-1# configure
        *A:NFJD-PSC-S-SR7750-1>config# service
        *A:NFJD-PSC-S-SR7750-1>config>service#
        """
        result = self.command("exit all", prompt={"success": "[\r\n]+\S+.+# ?$"})
        if result["state"] == "success":
            if re.search("[\r\n]+\S+.+>config>[a-z>]+# ?$", result["content"]):
                njInfo["errLog"] = "Switch to privilegeMode is faild. current located config mode."
            else:
                self.mode == 2
                njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def configMode(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        tmp = self.privilegeMode()
        if tmp["status"] is False:
            return tmp
        result = self.command("config", prompt={"success": "[\r\n]+\S+.+>config# ?$"})
        if result["state"] == "success":
            self.mode == 3
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVersion(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": "",
            "errLog": ""
        }
        result = self.command("show version", prompt={"success": "[\r\n]+\S+.+# ?$",
                                                      "eror": "Bad command[\s\S]+"})
        if result["state"] == "success":
            # TiMOS-C-10.0.R12 cpm/hops ALCATEL SR 7750 Copyright (c) 2000-2013 Alcatel-Lucent. --> TiMOS-C-10.0.R12
            tmp = re.search("(TiMOS\S+)", result["content"])
            if tmp:
                njInfo["content"] = tmp.group(1)
            else:
                njInfo["errLog"] = "Version information was not available."
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showRoute(self):
        # Switch to config mode.
        njInfo = {
            "status": False,
            "content": [],
            "errLog": ""
        }
        result = self.command("show router  route-table", prompt={"success": "[\r\n]+\S+.+# ?$",
                                                                  "eror": "Bad command[\s\S]+"})
        """
        Dest Prefix[Flags]                            Type    Proto     Age        Pref
        Next Hop[Interface Name]                                    Metric
        -------------------------------------------------------------------------------
        0.0.0.0/0                                     Remote  OSPF(10)  28d14h34m  190
            10.32.2.2                                                    102
        0.0.0.0/0                                     Remote  OSPF(10)  28d14h34m  190
           10.32.2.6                                                    102
        10.32.0.1/32                                  Remote  OSPF(10)  0484d16h   10
            10.32.2.2                                                    2
        10.32.0.1/32                                  Remote  OSPF(10)  0484d16h   10
            10.32.2.6                                                    2
        10.32.0.2/32                                  Remote  OSPF(10)  0484d16h   10
            10.32.2.2                                                    2
        """
        if result["state"] == "success":
            allLine = result["content"].split("\r\n")
            i = 0
            for line in allLine:
                lineInfo = {"net": "",
                            "mask": "",
                            "metric": "",
                            "description": "",
                            "type": "",
                            "interface": "",
                            "via": ""}
                tmp = re.search("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})\s+\S+\s+([A-Za-z]+)", line)
                if tmp:
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = tmp.group(2)
                    lineInfo["type"] = tmp.group(3)
                    # Get via and metric of routing from next line.
                    tmp = re.search("([\s\S]+)(\d+)", allLine[i + 1])
                    if tmp:
                        lineInfo["via"] = tmp.group(1).split()[0].strip("()")
                        lineInfo["metric"] = tmp.group(2)
                        njInfo["content"].append(lineInfo)
                    else:
                        continue
                i += 1
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo
