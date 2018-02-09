## 初始化 Initialize

##### Forward初始化过程可以简单分为三步：

```Python
# import
from forward import Forward
fw = Forward()

# add targets
fw.addTargets(['192.168.1.10', '192.168.1.21-192.168.1.30'], 'n7018', 'username', 'password')
fw.addTargets(['192.168.2.10'], 'mx960', 'username2', 'password2')
fw.addTargets(['192.168.3.10', '192.168.3.11-192.168.3.20'], 's5328', 'username3', 'password3')

# get instances
instances = fw.getInstances()
```

* 在这个代码段中，forward接受到了11台cisco n7018、1台juniper mx960和11台huawei s5328，共计23台设备信息作为目标，完成初始化并返回一个包含23台设备forward类实例的字典结构，用户可以通过下面的方法拿到其中任何一个实例，每一种设备类实例包含的属性和方法可能是不一样的，请参考详细的[类库文档](/docs/class):

```Python
cisco1 = instances['192.168.1.10']
```

* 这些类实例已经完成登陆，可以直接调用execute和command方法执行指令，如果你不需要在初始化环节进行登陆而希望自己控制登陆行为，请在第三步设置一个简单参数即可(例子中关闭了预登陆，并且代码控制只登陆了其中一台设备)，更多关于预登陆的信息请参考[预登陆](/docs/advance/prelogin):

```Python
instances = fw.getInstances(preLogin=False)
instances['192.168.1.21'].login()
```
