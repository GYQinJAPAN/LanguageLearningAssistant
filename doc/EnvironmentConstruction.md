# git软件配置

- 配置全局用户名和邮箱

```
git --version
git config --global user.name "你的姓名"
git config --global user.email "you@example.com"
```

# 仓库初始化方法

1. 通过克隆已有仓库（git clone）

```
git clone <repository-url> [目标目录]
```

- 默认创建与 远程 同名目录，也可指定后面带上目录名：

```
git clone https://github.com/user/repo.git myproject
```

克隆后,会自动设置 origin 远程,并创建对应的 远程追踪分支
ps:如果想要把代码保存在桌面,就需要从桌面进入Git Bash Here

2. 新建空仓库（git init）
   如果是自己新建的一个项目,可以创建 一个文件夹,作为项目的总文件夹 . 然后,进入文件夹页面,在文件夹下,打开git bash.

```
mkdir myproject && cd myproject  
git init
```

- git立刻生成隐藏的 .git 管理目录，让这个文件夹变成“Git可管理的仓库”。用来管理即将新建的源代码.
- Git 2.28+ 可用 git init --initial-branch=main 自定义初始分支名。

第一次提交

```
git add .
git commit -m "Initial commit"
```

添加远程仓库并推送

```
git remote add origin <你的远程仓库地址>
```

验证

```
git remote -v
```

推送到 GitHub

```
git branch -M main
git push -u origin main
```

# 在已有项目中创建虚拟环境

步骤：
打开项目
进入： File → Settings（设置）
找到： Project: xxx → Python Interpreter
点击右上角： ⚙️（齿轮） → Add Interpreter
选择： Add Local Interpreter
→ Virtualenv
配置： Location（建议 .venv）
Base interpreter（选择 Python 版本）
点击： OK / Apply

# 使用requirements.txt安装模块

```
1. .venv\Scripts\activate
2. pip install -r requirements.txt
 - pip install -r backend/requirements.txt
3. pip freeze > requirements.txt
4. deactivate
```

# 安装代码整型工具

1. Black（代码格式化工具）-->用 Black 自动格式化代码
2. Flake8
3. File Watcher（文件监听器）-->用 Watcher 在保存时自动执行 Black
   注意仍要先进入虚拟环境,再pip

```
.venv\Scripts\activate
pip install black flake8
pip list
```

## Black 的 Watcher 正确配置

点击： File → Settings → Tools → File Watchers → + → Custom
然后填：
① Name : Black <br>
② File type : Python <br>
③ Program（⚠️最容易错） 必须指向你虚拟环境里的 black <br>
如果你是 Windows：
```$ProjectFileDir$\.venv\Scripts\black.exe ```
如果你是 Mac / Linux：
```$ProjectFileDir$/.venv/bin/black ``` <br>
④ Arguments:
```$FilePath$ ``` <br>
⑤ Working directory:
```$ProjectFileDir$ ``` <br>
⑥ 勾选： ✅ Auto-save edited files to trigger the watcher <br>

## 配置 Flake8 Watcher

新建 Watcher： File → Settings → Tools → File Watchers → +  <br>
填写如下： <br>
① Name : Flake8 <br>
② File type :Python <br>
③ Program（⚠️重点） :指向虚拟环境里的 flake8 <br>
Windows：
```$ProjectFileDir$\.venv\Scripts\flake8.exe```
Mac/Linux：
```$ProjectFileDir$/.venv/bin/flake8 ``` <br>
④ Arguments:
```$FilePath$ ``` <br>
⑤ Working directory:
```$ProjectFileDir$ ```

## 关于PyCharm版本升级之后,原先的File Watchers无法使用的替代方案.

替代方案:Ruff 接管格式化 + lint，PyCharm 原生集成接管保存时动作，pre-commit 接管提交前兜底

```
pip install -U ruff pre-commit
pip list
ruff --version
pre-commit --version
```

## 首先在根目录创建pyproject.toml文件,规则内容可以询问ai.内容确定之后,在终端执行下述命令.

ruff check .：lint 主入口,检查，类似 Flake8
ruff check . --fix：自动修一部分可修问题
ruff format .：格式化主入口，定位上就是 Black 的替代物。

```
ruff check backend
ruff check backend --fix
ruff format backend
ruff check backend
```

## 在 PyCharm 里启用原生 Ruff 集成

打开：

```
Settings
  -> Python
    -> Tools
      -> Ruff
```

然后这样设置：
勾选 Enable
Execution mode 选 Interpreter mode
如果下面有按钮，点 Install Ruff
勾选：

- Inspections
- Formatting
- Import optimizer
  你选 Interpreter mode 的好处是最简单：
- PyCharm 会去你当前项目解释器里找 Ruff。这样不同项目各自用自己的 venv，不容易串环境。

## 配置保存时自动生效

```
Settings
  -> Tools
    -> Actions on Save
```

勾选：

- Reformat code
- Optimize imports

Actions on Save 可以在保存时自动做 Reformat code 和 Optimize imports；
而 Ruff 集成启用后，这两个动作会使用 Ruff。

注意事项：
文件类型尽量只选 Python
```
コードの整形
- 文件类型：Python
- 范围：ファイル全体
- 触发：すべての保存
インポートの最適化
- 文件类型：Python
- 范围：ファイル全体
- 触发：すべての保存
```

## 配置 pre-commit，

在项目根目录新建 .pre-commit-config.yaml。
文件内容:略

然后执行：
```
# 1) 确认在项目根目录
# 2) 创建 .pre-commit-config.yaml

# 3) 安装
pip install pre-commit

# 4) 安装 git hooks
pre-commit install

# 5) 首次全量检查
pre-commit run --all-files

# 6) 如有改动，再跑一次确认
pre-commit run --all-files
```
这样以后你每次 git commit 时，它都会帮你再兜底一次。

# 其他配置

## 自动保存设置

路径：File（文件） -> Settings（设置） -> Appearance & Behavior（外观与行为） -> System Settings（系统设置）
找到 "Autosave" 区域：
Save files if the IDE is idle for ... seconds: 当你停止打字达到指定秒数后，PyCharm 会自动保存。
Save files when switching to a different application...: 当你切换到浏览器、终端或其他软件时，PyCharm 会立即保存当前修改。

## 看到“未保存”的小星号

路径：Settings -> Editor -> General -> Editor Tabs
勾选：Mark modified (*)
开启后，如果你修改了代码但自动保存还没触发，标签页的文件名旁边会出现一个 * 号。

## 保存时自动格式化

路径：Settings -> Tools -> Actions on Save
勾选：Reformat code（重新格式化代码）或 Optimize imports（优化导入）。
这样你每次触发保存（或自动保存触发）时，代码都会瞬间变得整整齐齐。

## 开启“显示空格” (Show Whitespaces)

路径：File -> Settings (macOS 是 PyCharm -> Settings)
具体位置：Editor -> General -> Appearance
操作：勾选 Show whitespaces。
进阶细节：你可以点击这个选项左侧的小箭头，展开后可以精细选择：
Leading: 只显示行首的空格（缩进处）。
Inner: 显示代码中间的空格。
Trailing: 显示行尾多余的空格（建议开启，保持代码整洁）。

# 安装Node.js

React / Vite 前端开发必须依赖 Node.js + npm。
去官网下载：https://nodejs.org
建议安装： LTS版本（长期支持）
安装时注意： 必须勾选这一项： Add to PATH 一般默认已经勾选。其他默认即可!!!

## 安装完成后验证

重新打开PowerShell。

然后运行： node -v
如果成功会看到类似： v20.11.1
再运行： npm -v
例如： 10.2.4

只要这两个命令成功，你就可以继续了。
重启PyCharm!!!

# Vite React 项目构建

在项目根目录打开终端：

```
cd frontend
```

```
npm create vite@latest . -- --template react
```

如果提示： Need to install create-vite
输入： y

然后有可能会出现 ：当前 frontend 目录不是空的。

Vite 在创建项目时发现：

```
frontend/
src/
__init__.py
App.js
```

所以它问你： Current directory is not empty.

意思是： 当前目录已经有文件了，你想怎么处理？

这三个选项是什么意思
1️⃣ Cancel operation :取消操作（什么也不做）
2️⃣ Remove existing files and continue :删除当前目录里的文件，然后创建新的 Vite 项目
⚠️ 会删除：
frontend/src
frontend/__init__.py
3️⃣ Ignore files and continue ✅ 推荐
意思是： 保留现有文件 ,在当前目录创建 Vite 项目 不会删除你的东西。

直接选： Ignore files and continue

操作方式：
键盘按： ↓
直到光标到： Ignore files and continue
然后按： Enter

自动生成的文件一览

```
frontend/
│
├─ index.html
├─ package.json
├─ vite.config.js
├─ node_modules
│
└─ src
   ├─ App.jsx
   ├─ main.jsx
   └─ style.css
```

```
npm install
```

Vite 官方的创建方式就是通过 create vite 来初始化项目。
如果它提示目录非空，你有两种办法：

- 一种是先把 frontend 里现在的内容备份后清空再执行。
- 另一种是新建一个临时前端目录测试，跑通后再并回你的项目。


# 防止commmit失败设定 
建议在项目根目录放一个 .gitattributes，统一规则，例如：

* text=auto

*.py text eol=lf
*.js text eol=lf
*.jsx text eol=lf
*.css text eol=lf
*.md text eol=lf
*.txt text eol=lf
*.json text eol=lf

然后全局 Git 可以设成：
```git config --global core.autocrlf false```


这样以后通常会更稳定。

