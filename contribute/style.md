# 样式规范

为了确保本教程前后风格统一，请按照本样式规范书写教程，并提交 PR。

## 文件

当你编写了新的文档后，请正确存放你的文件，并在本地检查它。

- 页面划分：所有文档请存放在 `ch-xxx/` 目录下，ch 是 chapter 的简写，每章建一个目录，每节建立一个 `.md` 文件。

- 图片存放：绘图文件保存到项目 `drawio` 文件夹下，svg 图片保存到 `img` 文件夹下。每章图片请放在同一文件夹下。

- 目录名与文件名字应简洁直观，间隔使用减号式（-）连接，小写。
    > 例 python-ecosystem.svg
    > 例 ch-python-lang

## 文字

本教程面向针对初学者，文字风格请保持简洁高效，易于理解。任何有助于读者理解的文字，标识都是有帮助的。

- 首次出现的英文单词，应使用括号解释中文，下文可以继续使用该英文。
    >例 Deep Learning （深度学习）

- 首次出现的缩写，应使用括号解释全称和中文，下文可继续使用缩写。
    >例 API（Application Programming Interface，应用程序编程接口）

- 请在所有中文文字和半角的英文、数字、符号、链接前后插入空白，可以使用一些插件帮助进行空格的排版，比如 [VSCode pangu](https://marketplace.visualstudio.com/items?itemName=baurine.vscode-pangu)，或者安装 Python 版的 pangu 插件：`pip install -U pangu`。详情参考 [pangu](https://github.com/vinta/pangu.js)
  >例 欢迎star本仓库 --> 欢迎 star 本仓库

## 代码

请尽可能的使你的代码有更强的可读性。Python 代码编写规范，可以参考 [The Black Code Styles](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)，下面是一些具体情境。

- 变量名应尽量使用有一定含义的 `英文` 单词，而不是拼音。

- 变量名尽量有意义，保持可读性。除非简单示例中可以使用 `a = xx`，`b = xx` 外，建议复杂逻辑中不要出现 `a`，`b`，`c` 为名的的变量。可以使用 `i` ，`j` 这样的计数器。

- 函数名应使用下划线式命名，小写。
    >例 hello_world()

- 类名应大写，复杂类名应采用驼峰式命名。
    >例 class HelloWorld

## 图片

图片建议使用软件 [drawio](https://www.drawio.com/) 绘制，它也可以 [在线](https://app.diagrams.net/) 绘制，`.drawio` 绘图文件保存到项目 `drawio` 文件夹下，svg 图片保存到 `img` 文件夹下。
