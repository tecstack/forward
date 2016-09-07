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
    _just = 16
    _module = 'forward.models'

    def __init__(self, options, inventory, passwords,
                 logger=DEFAULT_LOGGER):
        super(TaskQueueManager, self).__init__()
        self.options = options
        self.inventory = inventory
        self.passwords = passwords
        self.logger = logger
        self._success = []

    def run(self):
        ''' use multi-threads to execute tasks '''
        op = self.options
        if not self.inventory:
            raise ForwardError('No IP Inventory Defined.')
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
            display.display('STATUS%s' % ('-' * 94))
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

    def _get_instance(self, ip):
        ''' connect to a remote host '''
        op = self.options
        if not op.model:
            raise ForwardError('No Device Model Defined.')
        if not op.remote_user:
            raise ForwardError('No Remote User Defined.')
        if not op.vender:
            raise ForwardError('No Device Vender Defined.')
        # use threading lock to ensure globals
        lock.acquire()
        self.logger.debug('Connecting to %s ...' % ip)
        try:
            instance = getattr(
                import_module(
                    '%s.%s' % (self._module, op.model)), op.model.upper())(
                        ip=ip, port=op.remote_port, timeout=op.timeout)
            login = instance.login(
                username=op.remote_user, password=self.passwords['con'])
            if login['status']:
                self.logger.info('%s: Login Succeed.' % ip.ljust(self._just))
                activate = instance.privilegeMode(
                    secondPassword=self.passwords['act'], deviceType=op.vender)
                if activate['status']:
                    self.logger.info(
                        '%s: Enable Succeed.' % ip.ljust(self._just))
                    self.logger.debug('Already Connected to %s.' % ip)
                    self._success.append(ip)
                    return instance, ip
                else:
                    self.logger.warn(
                        '%s: Enable Failed.' % ip.ljust(self._just))
            else:
                self.logger.warn('%s: Login Failed.' % ip.ljust(self._just))
        except ForwardError:
            raise
        except Exception as e:
            self.logger.debug('Cannot Connect to %s.' % ip)
            self.logger.error(repr(e))
            self.logger.debug(traceback.format_exc())
        finally:
            lock.release()

    def _get_failed(self):
        ''' get a list of hosts whose task failed execute '''
        return list(set(self.inventory) ^ set(self._success))

    def _print_task_status(self, ip):
        ''' print task status of all hosts '''
        msg = None
        if ip in self._success:
            msg = '%s: OK' % ip.ljust(self._just)
        else:
            msg = '%s: FAILED' % ip.ljust(self._just)
        display.display(msg)

    def cleanup(self):
        ''' clean up resource '''
        self._success = []
        try:
            lock.release()
        except:
            pass
