#!/usr/bin/env python
# coding:utf-8
"""
-----Introduction-----
[Core][forward] Device class for s3300.
Author: Cheung Kei-Chuen
"""
import pexpect
import re
from forward.devclass.baseMaipu import BASEMAIPU
from forward.utils.forwardError import ForwardError


class S3300(BASEMAIPU):
    """This is a manufacturer of maipu, so it is integrated with BASEMAIPU library.
    """

    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV1,
        the basic prompt for the device is overwritten here.
        """
        BASEMAIPU.__init__(self, *args, **kws)
        self.moreFlag = re.escape('....press ENTER to next \
line, Q to quit, other key to next page....')

    def _recv(self, _prompt):
        """A message returned after the receiving device has executed the command.
        """
        data = {'status': False,
                'content': '',
                'errLog': ''}
        # If the received message contains the host prompt, stop accepting.
        i = self.channel.expect([r"%s" % _prompt, pexpect.TIMEOUT], timeout=self.timeout)
        result = ''
        try:
            if i == 0:
                # Get result.
                result = self.channel.before
                data['status'] = True
            elif i == 2:
                raise ForwardError('Error: receive timeout')
            else:
                """If the program does not receive the message correctly,
                and does not timeout, the program runs failed.
                """
                data['errLog'] = self.channel.before
            data['content'] = result
        except ForwardError, e:
            data['errLog'] = str(e)
            data['status'] = False
        return data
