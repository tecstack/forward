#!/usr/bin/env python
# encodint:utf-8
# Author:Cheung Kei-Chuen
import unittest
import importlib
from forward.utils.forwardError import ForwardError


class deviceClassInitTest(unittest.TestCase):
    def setUp(self):
        self.devclass = ["adx03100",
                         "asa",
                         "asr1006",
                         "baseBaer",
                         "baseDepp",
                         "baseF5",
                         "baseFortinet",
                         "baseHuawei",
                         "baseCisco",
                         "baseJuniper",
                         "baseLinux",
                         "baseRaisecom",
                         "baseZte",
                         "c2960",
                         "c4510",
                         "c6506",
                         "c6509",
                         "e1000e",
                         "e8000e",
                         "e8160e",
                         "f1000",
                         "f510000",
                         "fg1240",
                         "fg3040",
                         "fg3950",
                         "m6000",
                         "mx960",
                         "n5548",
                         "n5596",
                         "n7010",
                         "n7018",
                         "n7710",
                         "n7718",
                         "ne40ex16",
                         "ne40ex3",
                         "r3048g",
                         "s3300",
                         "s5328",
                         "s5352",
                         "s5800",
                         "s8512",
                         "s9303",
                         "s9306",
                         "s9312",
                         "sr7750",
                         "srx3400",
                         "usg1000",
                         "vlb",
                         "zx5952"]
        self.initParameters = ["ip",
                               "username",
                               "password",
                               "port",
                               "timeout",
                               "privilegePw",
                               "isLogin",
                               "isEnable",
                               "channel",
                               "shell",
                               "basePrompt",
                               "prompt",
                               "moreFlag"]
        self.baseClassMethod = ["login",
                                "logout",
                                "execute",
                                "getMore",
                                "getPrompt",
                                "cleanBuffer"]

    def test__all_instance(self):
        for dev in self.devclass:
            _dev = getattr(importlib.import_module('forward.devclass.{dev}'.format(dev=dev)), dev.upper())
            _dev(1,2,3)

    def test_class_parameters(self):
        for dev in self.devclass:
            _dev = getattr(importlib.import_module('forward.devclass.{dev}'.format(dev=dev)), dev.upper())
            for parameter in self.initParameters:
                if not hasattr(_dev(1,2,3), parameter):
                    raise IOError('%s not have parameter:' % (dev), parameter)
