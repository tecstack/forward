## 基本介绍

* 支持Linux设备的操作。

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

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="login">login</a>

	调用此接口进行登录(参数来自init)，成功后取得shell环境、清除登陆后设备发送的欢迎信息、设置超时时间(timeout)，判断登录设备是否遇到密码过期提醒需要修改、以及取得主机提示符，比如 `[root@localhost ] # ` 。

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="logout">logout</a>

    注销与单个设备的会话。

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="execute">execute</a>

	在目标设备上执行一个`查询`命令，比如`show`、`display`，然后取得该命令的执行结果，最后返回一个字典（dict）格式的数据。
	
	注意： 不要使用该接口执行切换模式的命令，比如`enable`、`sys`、`config`、`interface`，也不要在切换模式后使用该接口,如果真的有需要，请使用<a href="#command">command高级开发接口</a>。 

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="command">command</a>

	在目标设备上执行`任何`命令，然后一直等待收取该命令的执行结果，直到`预期的消息出现`或`等待超时`为止，最后返回一个字典（dict）格式的数据。

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="getPrompt">getPrompt</a>

	取得目标设备上的主机提示符，比如：`TEST-N7710-1# `、`TEST-N7710-1> `等。

	`注意：该接口一般仅用于Forward内部使用。`
	
	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="getMore">getMore</a>

	自动获取因一个命令结果较长而导致的分页内容。

	`注意：该接口仅用于Forward内部使用`。

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)

---

* <a name="cleanBuffer">cleanBuffer</a>

	清除在`socket`内，因接受消息不彻底而遗留的字符数据。

	注意：`execute`、`command`在每次执行命令之前会自动调用该接口进行清除，该接口一般只用于Forward内部使用。

	功能特性继承自[baseSSHV2](/docs/class/sshv2/README.md)
