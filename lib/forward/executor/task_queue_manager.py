#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>
#
# This file is part of Forward.

import traceback
from importlib import import_module
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Lock
lock = Lock()

from forward import constants as C
from forward.utils.error import ForwardError
from forward.utils.log import logger as DEFAULT_LOGGER
from forward.executor.task_executor import TaskExecutor

try:
    from __main__ import display
except ImportError:
    from forward.utils.display import Display
    display = Display()

__all__ = ['TaskQueueManager']


class TaskQueueManager(object):
    '''
        This class handles the multi-threading requirements of forward
        by creating a pool of workers.
        The manager is responsible for dispatching tasks to hosts.
    '''
    _just = C.DEFAULT_IP_JUST
    _module = 'forward.models'

    def __init__(self, options, inventory, logger=DEFAULT_LOGGER):
        super(TaskQueueManager, self).__init__()
        self.options = options
        self.inventory = inventory
        self.logger = logger
        self._success = []

    def run(self):
        ''' use multi-threads to execute tasks '''
        op = self.options
        # check host inventory
        if not self.inventory:
            raise ForwardError('No Host Inventory Defined.')
        # use multi-threads to get task instances then run the play
        try:
            pool = ThreadPool(op.worker) if op.worker else ThreadPool()
            instances_t = pool.map(self._get_instance, self.inventory)
            instances = {}
            for x in instances_t:
                if x:
                    instances[x[1]] = x[0]
            result = TaskExecutor(
                instances=instances, script=op.script,
                args=op.args).run()
            display.display('\r\nSTATUS%s' % ('-' * 74))
            pool.map(self._print_task_status, self.inventory)
            return result
        except ForwardError:
            raise
        except Exception as e:
            self.logger.error(repr(e))
            self.logger.debug(traceback.format_exc())
        finally:
            pool.close()
            pool.join()
            self.cleanup()

    def _get_instance(self, host):
        ''' connect to a remote host '''
        if not host.model or host.model == list(C.DEFAULT_DEVICE_MODELS)[0]:
            raise ForwardError('No Device Model Defined.')
        if not host.vender or host.vender == list(C.DEFAULT_DEVICE_VENDERS)[0]:
            raise ForwardError('No Device Vender Defined.')
        if not host.remote_user:
            raise ForwardError('No Remote User Defined.')
        # use threading lock to ensure globals
        lock.acquire()
        self.logger.debug('Connecting to %s ...' % host.ip)
        try:
            instance = getattr(
                import_module(
                    '%s.%s.%s' % (self._module, host.connect, host.model)),
                host.model.upper())(
                    ip=host.ip, port=host.remote_port,
                    timeout=self.options.timeout)
            login = instance.login(
                username=host.remote_user, password=host.conpass)
            if login['status']:
                self.logger.info(
                    '%s: Login Succeed.' % host.ip.ljust(self._just))
                activate = instance.privilegeMode(
                    secondPassword=host.actpass, deviceType=host.vender)
                if activate['status']:
                    self.logger.info(
                        '%s: Enable Succeed.' % host.ip.ljust(self._just))
                    self.logger.debug('Already Connected to %s.' % host.ip)
                    self._success.append(host.ip)
                    return instance, host.ip
                else:
                    self.logger.warn(
                        '%s: Enable Failed.' % host.ip.ljust(self._just))
            else:
                self.logger.warn(
                    '%s: Login Failed.' % host.ip.ljust(self._just))
        except ForwardError:
            raise
        except Exception as e:
            self.logger.debug('Cannot Connect to %s.' % host.ip)
            self.logger.error(repr(e))
            self.logger.debug(traceback.format_exc())
        finally:
            lock.release()

    def _get_failed(self):
        ''' get a list of hosts whose task failed execute '''
        return list(set([x.ip for x in self.inventory]) ^ set(self._success))

    def _print_task_status(self, host):
        ''' print task status of all hosts '''
        msg = None
        if host.ip in self._success:
            msg = '%s: OK' % host.ip.ljust(self._just)
        else:
            msg = '%s: FAILED' % host.ip.ljust(self._just)
        display.display(msg)

    def cleanup(self):
        ''' clean up resource '''
        self._success = []
        try:
            lock.release()
        except:
            pass
