# git配置

配置全局用户名和邮箱

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

默认创建与 远程 同名目录，也可指定后面带上目录名：

```
git clone https://github.com/user/repo.git myproject
```

克隆后,会自动设置 origin 远程,并创建对应的 远程追踪分支
ps:如果想要把代码保存在桌面,就需要从桌面进入Git Bash Here

2. 新建空仓库（git init）
   如果是自己新建的一个项目,可以创建 一个文件夹,作为项目的总文件夹 . 然后,进入文件夹页面,在文件夹下,打开Git控制台.

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
3. pip freeze > requirements.txt
4. deactivate
```

# 安装代码整型工具

1. Black（代码格式化工具）-->用 Black 自动格式化代码
2. Flask（Web框架）-->用 Flask 写项目
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




