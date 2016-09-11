#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

from forward import constants as C
from forward.utils.error import ForwardError


class HostOption(object):
    """
        Forward Host Options
    """
    def __init__(
            self, ip=list(C.LOCALHOST)[2],
            vender=list(C.DEFAULT_DEVICE_VENDERS)[0],
            model=list(C.DEFAULT_DEVICE_MODELS)[0],
            connect=C.DEFAULT_TRANSPORT, conpass=None, actpass=None,
            remote_port=C.DEFAULT_REMOTE_PORT,
            remote_user=C.DEFAULT_REMOTE_USER):
        super(HostOption, self).__init__()
        try:
            self.ip = str(ip)
            self.vender = str(vender)
            self.model = str(model)
            self.connect = str(connect)
            self.conpass = str(conpass) if conpass else ''
            self.actpass = str(actpass) if actpass else ''
            self.remote_port = int(remote_port)
            self.remote_user = str(remote_user)
        except TypeError as e:
            raise ForwardError('Bad Host Option: %s.' % e)
