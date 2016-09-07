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
```

## Examples

### 1. Script Sample

```
$ vi conf/forward_script.py
def node(nodeInput):
    # init njInfo
    njInfo = {
        'status':True,
        'errLog':'',
        'content':{}
    }

    # node
    for device in nodeInput['instance']:
        instance = nodeInput['instance'][device]
        version = instance.execute('cat /etc/redhat-release')
        if version['status']:
            # execute succeed
            njInfo['content'][device] = version['content']
        else:
            njInfo['status'] = False
            njInfo['errLog'] = '%s%s:%s\r\n' % (njInfo['errLog'], device, version['errLog'])
    return njInfo
```

### 2. Calling Methods

Note: Configuration file can be used together with pure CLI,
 which will overwrite configurations in pure CLI. 

#### 2.1 Pure CLI

```
$ forward -w 4 -s conf/forward_script.py -a {} --loglevel debug
  -l log/forward.log --no-stdout-log -t txt -o data/forward_out
  -i '["127.0.0.1", "192.168.182.14-192.168.182.16"]' -v bclinux7
  -m bclinux7 --connect ssh -P -A -p 22 -u root -T 2
```

#### 2.2 CLI with Configuration File

```
$ vi conf/forward_custom.cfg
[runtime]
worker = 2

[script]
script = conf/forward_script.py
args = {}

[logging]
loglevel = debug
logfile = log/forward.log
#no_std_log = True

[output]
out = stdout
#out = txt
outfile = data/out

[inventory]
inventory = ['127.0.0.1', '192.168.182.14-192.168.182.16']
vender = bclinux7
model = bclinux7

[connection]
connect = ssh
ask_pass = True
ask_activate = True
remote_user = root
timeout = 3

$ forward -c conf/forward_custom.cfg
```

#### 2.3 Class API

```
>>> from forward.api import Forward
>>> forward = Forward(
        worker=4, script='conf/forward_script.py', args={},
        loglevel='info', logfile='log/forward.log',
        no_std_log=True, out='txt', outfile='out/forward_out',
        inventory=['127.0.0.1', '192.168.182.14', '192.168.182.16'],
        vender='bclinux7', model='bclinux7', connect='ssh',
        conpass='111111', actpass='',
        remote_port=22, remote_user='root', timeout=2)
>>> result = forward.run()
```
