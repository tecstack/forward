## 基本介绍

* 支持凡是使用TELNET协议进行远程控制的设备。
* 使用TelnetLib作为远程登录模块。

## 接口列表


| 接口名 | 描述 | 
| --- | --- |
| <a href="#init">__init__</a> | 实例初始化 |
| <a href="#login">login</a> | 登录目标设备 |
| <a href="#logout">logout</a> | 登出目标设备 |
| <a href="#execute">execute</a> | 执行查询命令(普通) |
| <a href="#command">command</a> | 执行所有命令(高级) |
| <a href="#getPrompt">getPrompt</a> | 获取主机提示符，并识别登录设备后所处模式 |
| <a href="#getMore">getMore</a> | 自动获取分页消息 |
| <a href="#cleanBuffer">cleanBuffer</a> | 清除通道内残留信息 |

## 接口详情




* <a name="init">__init__</a>

	在登录设备之前，Forward需要取得登录设备的基本信息，诸如IP地址、设备型号、账号密码、用户名、特权模式密码等；同时需要设定一些初始化参数，用于记录程序运行状态。最后程序返回一个字典（dict）格式的数据。

	* 调用参数

		| 参数名 | 类型 | 必须 | 描述 |
		| --- | --- | --- | --- |
		| ip | str | 是 | 目标设备的IP地址 |
		| username | str | 是 | 目标设备的登录账户 |
		| password | str | 是 | 目标设备的密码 |
		| privilegePw | str | 否 | 特权模式密码 |
		| port | int | 否 | 目标设备端口，默认端口22 |
		| timeout | int | 否 | 消息接收超时时间，默认30秒 |
		| kwargs | dict | 否 | 自定义参数，非Forward所使用 |

---

* <a name="login">login</a>

	调用此接口进行登录(参数来自init)，成功后取得shell环境、清除登陆后设备发送的欢迎信息、设置超时时间(timeout)，判断登录设备是否遇到密码过期提醒需要修改、以及取得主机提示符，比如 `[root@localhost ] # ` 。

	* 调用参数
	
		无。

	* 返回参数

		| 字段 | 类型 | 描述 | 样例 |
		| --- | --- | --- | --- |
		| status | bool | 调用该接口是否成功 | False | 
		| content | str | 调用该接口所产生的正确内容输出,但可能为空，这取决于所执行命令的结果 |  |
		| errLog |  str | 调用该接口所产生的错误内容或Forward的错误提示信息 | 用户名或密码错误 |

	* 案例
	
	``` Python
	>>> instance=......
	>>> instance.login()
	>>> {"status":False,"content":"","errLog":"用户名或密码错误。"}
	```

---

* <a name="logout">logout</a>

    注销与单个设备的会话。

	* 调用参数
	
		无。

	* 返回参数

		| 字段 | 类型 | 描述 | 样例 |
		| --- | --- | --- | --- |
		| status | bool | 调用该接口是否成功 | True |
		| content | str | 调用该接口所产生的正确内容输出,但可能为空，这取决于所执行命令的结果 |  |
		| errLog |  str | 调用该接口所产生的错误内容或Forward的错误提示信息 |  |

	* 案例
	
	``` Python
	>>> instance=......
	>>> instance.logout()
	>>> {"status":True,"content":"","errLog":""}
	```

---

* <a name="execute">execute</a>

	在目标设备上执行一个`查询`命令，比如`show`、`display`，然后取得该命令的执行结果，最后返回一个字典（dict）格式的数据。
	
	注意： 不要使用该接口执行切换模式的命令，比如`enable`、`sys`、`config`、`interface`，也不要在切换模式后使用该接口,如果真的有需要，请使用<a href="#command">command高级开发接口</a>。 

	* 调用参数
	
		| 参数名 | 类型 | 必须 | 描述 | 样例 |
		| --- | --- | --- | --- | --- |
		| cmd | str | 是 | 设备操作系统命令 | show version |

	
	* 返回参数

		| 字段 | 类型 | 描述 | 样例 |
		| --- | --- | --- | --- |
		| status | bool | 调用该接口是否成功 | True |
		| content | str | 调用该接口所产生的正确内容输出,但可能为空，这取决于所执行命令的结果 | ...cisco Nexus7700 C7710 (10 Slot) Chassis ("Supervisor Module-2")... |
		| errLog |  str | 调用该接口所产生的错误内容或Forward的错误提示信息 |  |

	* 案例
	
	``` Python
	>>> instance=......
	>>> instance.execute("show version")
	>>> {"status":True,"content":"...cisco Nexus7700 C7710 (10 Slot)...","errLog":""}
	```

---

* <a name="command">command</a>

	在目标设备上执行`任何`命令，然后一直等待收取该命令的执行结果，直到`预期的消息出现`或`等待超时`为止，最后返回一个字典（dict）格式的数据。

	* 调用参数
		
		| 参数名 | 类型 | 必须 | 描述 | 样例 |
		| --- | --- | --- | --- | --- |
		| cmd | str | 是 | 设备操作系统命令 | enable |
		| prompt | dict | 是 | 预测将会出现的字符 | {"success":"TEST-N7710-1# ","error":"TEST-N7710-1> "} |
		| timeout | int | 否 | 消息接收超时时间 | 60(单位：秒) |
	
	* 返回参数
	
		| 字段 | 类型 | 描述 | 样例 |
		| --- | --- | --- | --- |
		| status | bool | 调用该接口是否成功 | True |
		| content | str | 调用该接口所产生的正确内容输出,但可能为空，这取决于所执行命令的结果 | TEST-N7710-1#  |
		| errLog |  str | 调用该接口所产生的错误内容或Forward的错误提示信息 |  |


	* 案例
	
	``` Python
	>>> instance......
	>>> instance.command("enable",prompt={"success":"TEST-N7710-1# ","error":"TEST-N7710-1> "})
	>>> {"status":True,"content":"...TEST-N7710-1# ","errLog":""}
	```

---

* <a name="getPrompt">getPrompt</a>

	取得目标设备上的主机提示符，比如：`TEST-N7710-1# `、`TEST-N7710-1> `等。

	`注意：该接口一般仅用于Forward内部使用。`
	
	* 调用参数
	
		无。

	* 返回参数
		无，但可通过self.prompt取得。

---

* <a name="getMore">getMore</a>

	自动获取因一个命令结果较长而导致的分页内容。

	`注意：该接口仅用于Forward内部使用`。

	* 调用参数

		| 参数名 | 类型 | 必须 | 描述 | 样例 |
		| --- | --- | --- | --- | --- |
		| bufferData | str | 是 | 当前已收到的命令结果 | ******-- More -- |

	* 返回参数
		
		无。

---

* <a name="cleanBuffer">cleanBuffer</a>

	清除在`socket`内，因接受消息不彻底而遗留的字符数据。

	注意：`execute`、`command`在每次执行命令之前会自动调用该接口进行清除，该接口一般只用于Forward内部使用。

	* 调用参数
	
		无。
	
	* 返回参数
	
		无。