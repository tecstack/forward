## Version Update Record 版本更新记录
### V3.0.8
1. 新增sshv1和telnet通道标准类的command命令模式。

### V3.0.7
1. 新增sshv2通道标准类的command命令模式，通过高度自定义用法来实现网络设备配置模式。
2. 新增baseFenghuo标准类库。
3. 修复S9312,S5800,NE40EX16,S9300,S9312类库中的部分bug。

### V3.0.6
1. 新增vyoslinux类的zcli命令模式
2. 修复vyoslinux执行命令返回状态不正确的缺陷和特别字符问题。
3. 新增S5800类支持创建VLan、设置Vlan接口、设置Trunk接口。
4. 新增S9312类支持创建VLan、设置VLan接口。
5. 修复baseTELNET参数不一致问题。

### V3.0.5
1. 修复bug:
 * 修复了USG设备的privilege模式。
 * 修复了vyos设备的部分指令返回卡死的问题。
 * 添加了bclinux7设备的zcli模式。

### V3.0.4
1. 修复bug:
 * telnet与sshv1分支系列设备不能成功初始化的问题已经修复。
 * cisco系列设备的二次认证问题已经修复。

### V3.0.3
1. 新增类库: 目前所有1.0版本中的类库已经重构完毕，可以使用，但未经过测试。
 * 根级基础类：baseTELNET,baseSSHV1
 * 厂家级基础类：baseJuniper,baseBear,baseDepp,baseF5,baseFortinet,baseRaisecom,baseZte
 * 华为类：s3300,e1000e
 * Juniper类：mx960,srx3400
 * 启明星辰类：usg1000
2. 修复继承关系:
 * f510000,fg1240,fg3040,fg3950,m6000,r3048g,s5800,sr7750,zx5952：这些类库目前正确地继承了厂家基础类。

### V3.0.2
1. 新增类库:
 * 华为类：e8000e,s9306,s9312,e8160e,ne40ex3,ne40ex16,s5328,s5352,s8512
 * 思科类：adx03100,asa,asr1006,f1000,f510000
 * linux类：bclinux7
 * 其他类：sr7750,zx5952,fg1240,fg3040,fg3950,m6000,r3048g,s5800,vlb

### V3.0.1
1. 新增类库:
 * 厂家级基础类：baseHuawei
 * 华为类：s9303
2. 修正bug: n7018类现在可以被正确的调用了。

### V3.0.0
1. 版本重构，欢迎体验精简的Forward3.0，参考快速入门。
2. 当前支持的类库:
 * 根级基础类：basesshv2
 * 厂家级基础类：basecisco,baselinux
 * 思科类：c2960,c4510,c6506,c6509,n5548,n5596,n7010,n7018,n7710,n7718
3. 添加预登陆模式: 默认所有类实例将会在用户调用getInstances方法时批量登陆，如果你不需要预先登陆所有机器，可以指定preLogin属性，例如：Forward.getInstances(preLogin=False)，然后在单独的实例中调用login()方法进行登陆。
