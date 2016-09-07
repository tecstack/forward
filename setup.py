#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# (c) 2016, Leann Mak <leannmak@139.com>

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from forward.release import __version__, __author__
try:
    from setuptools import setup, find_packages
except ImportError:
    print("forward now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

setup(name='forward',
      version=__version__,
      description='Radically simple IT automation',
      author=__author__,
      author_email='leannmak@139.com',
      url='https://github.com/tecstack/forward',
      license='GPLv3',
      install_requires=['paramiko', 'setuptools', 'cryptography>=1.1'],
      package_dir={'': 'lib'},
      packages=find_packages('lib'),
      package_data={'': [], },
      classifiers=[
          # How mature is this project? Common values are
          # 3 - Alpha
          # 4 - Beta
          # 5 - Production/Stable
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later \
           (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities',
      ],
      scripts=['bin/forward', ],
      data_files=[],)
