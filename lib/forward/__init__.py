# coding:utf8
#
# This file is part of Forward.
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

import threading
import importlib
import forward.release
from forward.utils.forwardError import ForwardError
from forward.utils.loginThread import loginThread
from forward.utils.paraCheck import paraCheck
from forward.utils.deviceListSplit import DEVICELIST

__version__ = forward.release.__version__
__author__ = forward.release.__author__


class Forward(object):
    """Forward Module Main Class"""
    def __init__(self, targets=None):
        # target: [[ip,model,user,pw,{port},{timeout}],...]
        super(Forward, self).__init__()
        self.instances = {}
        if (targets is None):
            self.targets = []
        elif paraCheck(targets):
            self.targets = targets
        else:
            raise ForwardError('[Forward Init Failed]: parameters type error')

    def addTargets(self, iplist, model, username, password, **kwargs):
        # iplist,model,username,password,port=??,timeout=??
        ipAdds = DEVICELIST(iplist).getIpList()
        targetList = []

        for ip in ipAdds:
            if paraCheck([[ip, model, username, password, kwargs]]):
                targetList.append([ip, model, username, password, kwargs])
            else:
                print "[Add Targets Error]: %s parameters type error, please check." % ip

        self.targets.extend(targetList)

    def getInstances(self, preLogin=True):
        # thread init
        threads = []

        # init instances
        if preLogin:
            for target in self.targets:
                model = target[1]
                className = model.upper()
                self.instances[target[0]] = getattr(
                    importlib.import_module('forward.devclass.%s' % (model)),
                    className
                )(target[0], target[2], target[3], **target[4])

                threadNode = threading.Thread(target=loginThread, args=(self.instances[target[0]],))
                threadNode.start()
                threads.append(threadNode)
        else:
            for target in self.targets:
                model = target[1]
                className = model.upper()
                self.instances[target[0]] = getattr(
                    importlib.import_module('forward.devclass.%s' % (model)),
                    className
                )(target[0], target[2], target[3], **target[4])

        # pre login thread join
        if preLogin:
            for t in threads:
                t.join()

        return self.instances
