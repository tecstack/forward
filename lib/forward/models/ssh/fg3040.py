
#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for fg3040.
"""

import re
# from base.sshv2 import sshv2
from forward.models.baseSSHV2 import BASESSHV2
from forward.models.fgFirewallPolicyAdmin import FGFirewallPolicyAdmin
class FG3040(BASESSHV2,FGFirewallPolicyAdmin):
	pass	
