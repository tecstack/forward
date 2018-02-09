## Getting Started
* &ensp;&ensp;下方代码段展示了一个简易的forward场景实现，批量连接到两台设备(思科Nexus7018)，执行指令并获取结果。
* &ensp;&ensp;The code section below shows a simple forward scenario implementation that is batch connected to two devices (CISCO Nexus7018), executes instructions and gets the results.

  ```Python
  from forward import Forward

  new = Forward()
  new.addTargets(['192.168.113.1-192.168.113.2'],'n7018','username','password')
  instances = new.getInstances()

  cisco1 = instances['192.168.113.1']
  cisco2 = instances['192.168.113.2']

  result1 = cisco1.execute('show version')
  result2 = cisco2.execute('show version')

  if result1['status']:
      print '[%s] OS version info: %s' % ('cisco1', result1['content'])
  if result2['status']:
      print '[%s] OS version info: %s' % ('cisco2', result2['content'])
  ```
* &ensp;&ensp;上述代码段中出现的'cisco1'和'cisco2'就是Forward设备类实例(N7018),不同设备类实例包含的方法可能不同，具体请查阅类库文档。
* &ensp;&ensp;The 'cisco1' and 'cisco2' appearing in the above code segment are Forward device class instances (N7018). Different device class instances contain different methods. Please consult the class library document.
