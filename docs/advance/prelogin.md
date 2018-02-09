## 预登陆 Prelogin

* 预登陆模式(默认)，获取实例同时完成自动登录，可直接执行指令。

```Python
# get instances that have logined
instances = fw.getInstances()
```

* 非登陆模式，获取实例时只做初始化操作，不执行自动登陆，可后续代码控制登陆。

```Python
# get instances that haven't logined
instances = fw.getInstances(preLogin=False)
# manual login
instances['192.168.1.10'].login()
```

* 非登陆模式主要用于应对以下场景:
  * 目标节点数量巨大，且不需要全部登陆，例如在庞大组网结构中逐跳定位路径场景。
  * 设备执行指令耗时巨大，可能导致其他等待节点自动断开连接，从而影响场景执行，例如核查分析全量配置场景。
  * 其他类似场景。
