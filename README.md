# Forward
[![Build Status](https://travis-ci.org/tecstack/forward.svg?branch=forward)](https://travis-ci.org/tecstack/forward)
[![Download Status](https://img.shields.io/badge/download-1024%2Fmonth-green.svg)](https://github.com/tecstack/forward)

Forward is a simple automation tool for IT Operations.

(c) 2016, C-Ant, Inc.

## Prerequests

* python 2.7
* git
* easy_install && pip
* pyenv && pyenv-virtualenv

## Usage

```
$ git clone https://github.com/tecstack/forward.git
$ cd forward
$ pip install -r requirements.txt
$ python setup.py install
$ forward --help
$ forward-cross --help
```

## Examples

### 1. Forward Console CLI

```
$ forward -w 4 -s sample/example.py -a {} --loglevel debug
  -l sample/forward.log --no-stdout-log -t txt -o sample/forward_out
  -i '["127.0.0.1", "192.168.182.14-192.168.182.16"]' -v bclinux7
  -m bclinux7 --connect ssh -P -A -p 22 -u root -T 2
```

### 2. Forward Cross CLI

```
$ forward-cross -I sample/hosts -C sample/play.cfg
```

### 3. Forward Class API

```
>>> from forward.api import Forward
>>> inventory = [
        dict(ip='127.0.0.1', vender='bclinux7', model='bclinux7',
             connect='ssh', conpass='111111', actpass='',
             remote_port=22, remote_user='maiyifan',),
        dict(ip='192.168.182.14', vender='bclinux7', model='bclinux7',
             connect='ssh', conpass='111111', actpass='',
             remote_port=22, remote_user='maiyifan',),
        dict(ip='192.168.182.16', vender='bclinux7', model='bclinux7',
             connect='ssh', conpass='111111', actpass='',
             remote_port=22, remote_user='maiyifan',)]
>>> forward = Forward(
        worker=4, script='sample/example.py', args={},
        loglevel='info', logfile='sample/forward.log',
        no_std_log=True, out='txt', outfile='sample/forward_out',
        inventory=inventory, timeout=2)
>>> result = forward.run()
```
