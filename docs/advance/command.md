## 自定义指令 Command

##### Description

* 自定义指令Command是一个通用方法，所有继承于ssh和telnet类的节点类实例都具备该方法，接受"命令行"和"判断依据"两个参数，执行"命令行"之后按照"判断依据"的定义来判断结果，并返回结果。

##### Options

| parameter | required | default | choices | comments |
|:--:|:--:|:--:|:--:|:--:|
| cmd | yes | none |  | The command line you want to execute. |
| prompt | yes | none |  | The prompt dict which will decide the type of CMD execution result. |

* command会在执行cmd之后依次匹配prompt中定义的正则表达式，匹配后中断后续匹配并返回状态结果。

##### Return

* command指令返回一个字典结构

| attr | type | example | comments |
|:--:|:--:|:--:|:--:|
| status | boolean | True | CMD execution status. |
| state | string | 'state_you_defined' | CMD execution result type. |
| content | boolean | True | CMD execution console output. |
| errLog | boolean | True | CMD execution error log(when status is False). |

##### Example

* 使用centos cp 指令场景作为样例，首先列出手工执行cp指令可能遇到的情况:

* 直接成功情况:

```Bash
[admin@SOMEHOST ~]$ cp -i file_a file_b
[admin@SOMEHOST ~]$
```

* 询问覆盖情况:

```Bash
[admin@SOMEHOST ~]$ cp -i file_a file_b
cp: overwrite "file_b"? y
[admin@SOMEHOST ~]$
```

* 权限不够情况:

```Bash
[admin@SOMEHOST ~]$ cp -i file_c file_d
cp: can not open "file_c" : permission denied
[admin@SOMEHOST ~]$
```

* 使用Forward command方法构建一个小型cp函数，一次性实现所有场景

```Python
from forward import Forward
fw = Forward()
fw.addTargets(['192.168.10.10'], 'baseLinux', 'username', 'password')
linux = fw.getInstances()['192.168.10.10']

def cp(from_path, to_path, overwrite):
    cmd = 'cp -i %s %s' % (from_path, to_path)
    prompt = [
      { 'exist': ['overwrite'] },
      { 'denied': ['permission denied'] },
      { 'success': ['COREVM60 \~\]\$', '\$'] }
    ]

    def call_exist():
        confirm_cmd = overwrite
        confirm_prompt = [
          { 'error': ['error'] },
          { 'success': ['COREVM60 \~\]\$', '\$'] }
        ]
        confirm_result = linux.command(cmd=confirm_cmd, prompt=confirm_prompt)
      	if confirm_result['status'] == True and confirm_result['state'] == 'success':
      		  print 'copy complete! overwrite: %s' % overwrite
      	else:
      		  print 'error: %s\r\nerror:%s' % (confirm_result['content'], confirm_result['errLog'])

    def call_denied():
        print 'Permission denied'

    def call_success():
        print 'Success'

    call_function = {
      'exist': call_exist,
      'denied': call_denied,
      'success': call_success
    }

    result = linux.command(cmd=cmd, prompt=prompt)
    if result['status'] == True:
      	call_function[result['state']]()
```

##### Command VS Execute:

* execute适用于简单的查询场景，要求在指令执行之后提示符不会发生变化。
* command适用于复杂的配置场景，由用户自己指定返回值匹配规则，适合用于构建复杂功能操作。
