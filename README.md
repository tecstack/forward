# Forward
  [![Build Status](https://travis-ci.org/tecstack/forward.svg?branch=master)](https://travis-ci.org/tecstack/forward)
  [![Download Status](https://img.shields.io/badge/download-1024%2Fmonth-green.svg)](https://github.com/tecstack/forward)

---

## Introduce 介绍

* Forward是一个python模块，提供与目标设备之间的通道封装，基于指令行(Command Lines)的方式实现多数功能的封装，供开发者快速简便调用，屏蔽不同设备上指令差异。
* 建议使用Forward用于多种(厂家、型号)网络设备的自动化管理场景，可以快速构建出运维场景脚本。
* Forward is a python module, which provides channel encapsulation between target devices, and realizes most functions encapsulation based on Command Lines. It allows developers to invoke quickly and simply, and screen instructions on different devices.
* We recommend the use of Forward for a variety of (manufacturer, model) network equipment automation management scene, can quickly build the operation and maintenance scenario script.

---

## Installation

* Building virtual environment (optional) 构建虚拟环境 (可选)

  * 开发者用户推荐，使用pyenv和virtualenv构建纯净的python环境，基于python版本2.7.10
  * We recommend that developer users use pyenv and virtualenv to build a pure Python environment which is based on Python version 2.7.10.

  ```Bash
  pyenv virtualenv 2.7.10 forward
  pyenv activate forward
  ```

* Pull 拉取当前版本

  ```Bash
  git clone http://192.168.182.51/promise/forward.git
  cd forward
  ```

* Dependency 安装依赖包

  ```Bash
  pip install -r requirements.txt
  ```

* Setup 安装

  ```Bash
  python setup.py install
  ```

---

## Getting Started

* 下方代码段展示了一个简易的forward场景实现，批量连接到两台设备(思科Nexus7018)，执行指令并获取结果。
* The code section below shows a simple forward scenario implementation that is batch connected to two devices (CISCO Nexus7018), executes instructions and gets the results.

  ```Python
  from forward import Forward

  new = Forward()
  new.addTargets(['192.168.113.1-192.168.113.2'], 'n7018', 'username', 'password')
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

* 上述代码段中出现的'cisco1'和'cisco2'就是Forward设备类实例(N7018),不同设备类实例包含的方法可能不同，具体请查阅[类库文档](/docs/class)。
* The 'cisco1' and 'cisco2' appearing in the above code segment are Forward device class instances (N7018). Different device class instances contain different methods. Please consult the [detailed library documents](/docs/class).

---

## Advanced Usage

* [初始化 Initialize](/docs/advance/initialize.md)
* [预登陆 PreLogin](/docs/advance/prelogin.md)
* [自定义指令 command](/docs/advance/command.md)

---

## Class

* Forward目前包含40多种特定型号设备类库，查看详细的[类库文档](/docs/class)。
* Forward currently contains more than 40 specific type of device class libraries, here to look at the [detailed library documents](/docs/class).

---

## Authors

* Forward由王喆(Headkarl: azrael-ex@139.com)创建，并且由张其川(cheung kei-chuen: qichuan.zhang@qq.com)、麦艺帆(Leann Mak:leannmak@139.com)、戴声(Shawn.T:shawntai.ds@gmail.com)等多位用户参与贡献，在此衷心感谢每一位。
* Forward was created by Wang Zhe(Headkarl: azrael-ex@139.com) and contributed by many users, such as Zhang Qichuan(cheung kei-chuen: qichuan.zhang@qq.com), Mai Yi Fan(Leann Mak:leannmak@139.com) and Dai Sheng(Shawn.T:shawntai.ds@gmail.com), and sincerely thanks each one.

---

## License

* GNU General Public License v3.0
* See [COPYING](COPYING) to see the full text.

---

## Branch Info

* RC,Releases和Stables分支都以版本号+各种鱼类命名。
* devel分支对应正在开发的分支。
* alpha分支对应一个早期的内部测试版本。
* RC,Releases and Stables are named after the version number plus any kind of fish.
* The devel branch corresponds to the release actively under development.
* The alpha branch corresponds to a early release thich is used for In-House test.

---

## Version Info

* 在[版本记录](/docs/VersionInfo.md)中查看所有历史记录，开源前的版本更新仅可以看到记录。
* Looking at all the history records in [Version Info](/docs/VersionInfo.md), the pre - source version updates can only see the records.
