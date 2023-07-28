# Python 分布式编程

## 参与编写

### 环境安装

本书基于名为 `d2lbook` 的 Python 工具编译，并部署在GitHub Pages上。

选择一个包管理工具，比如 `conda` 或者 `venv`，安装 `d2lbook`：

```bash
pip install git+https://github.com/d2l-ai/d2l-book
```

更多 `d2lbook` 工具的使用方法，请参考其官方文档：[D2L-Book: A Toolkit for Hands-on Books](https://book.d2l.ai/)

构建 PDF 时如果有 SVG 图片需要安装 LibRsvg 来转换 SVG 图片，安装 `librsvg` 可以通过`apt-get install librsvg`（如果是 macOS 可以用 Homebrew）。

构建 PDF 必须要有 LaTeX，请安装[Tex Live](https://www.tug.org/texlive/).

### 编译HTML版本

在编译前先 `git clone` [https://github.com/py-101/distributed-python/](https://github.com/py-101/distributed-python/)， 所有的编译命令都在这个文件目录内执行。

```bash
 git clone https://github.com/py-101/distributed-python.git
 cd distributed-python
```

使用d2lbook工具编译HTML。 请尽量使用 `build_html.sh` 脚本进行编译，保证首页正确合并到书籍中去。

```bash
sh build_html.sh
```

生成的html会在`_build/html`。

如果是在本地，可以使用 Python 自带的 HTTP Server：

```bash
cd _build/html
python -m http.server
```
