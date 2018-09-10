## Installation
1. Building virtual environment (optional) 构建虚拟环境 (可选)
  * &ensp;&ensp;开发者用户推荐，使用pyenv和virtualenv构建纯净的python环境，推荐python版本2.7.10及以上版本，兼容python3
  * &ensp;&ensp;We recommend that developer users use pyenv and virtualenv to build a pure Python environment, and recommend Python version 2.7.10 and later versions, including python3.
  ```Bash
  pyenv virtualenv 2.7.10 forward
  pyenv activate forward
  ```
2. Pull 拉取当前版本
  ```Bash
  git clone https://github.com/tecstack/forward.git
  cd forward
  ```
3. Dependency 安装依赖包
  ```Bash
  pip install -r requirements.txt
  ```
4. Setup 安装
  ```Bash
  python setup.py install
  ```
