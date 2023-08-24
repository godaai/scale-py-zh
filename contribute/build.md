# 构建指南

本书基于名为 d2lbook 的 Python 工具构建，并部署在 GitHub Pages 上。本书主要内容使用 `.md` 文件保存。文件格式流程为：`ch-xxxx/*.md` -> `_build/eval/*.ipynb` -> `_build/rst/*.rst` -> `_build/html/*.html`。d2lbook 工具可以将 `.ipynb` 或 `.md` 文件转化为 HTML 格式。可以通过以下方式构建 HTML。

如果觉得下文所讲述的构建 HTML 的教程对你来说难度过大，也可以仅修改 `ch-xxxx` 各章节的 `.md` 文件，提交 PR(Pull Request)，由我们来进行构建。

## 文字与代码风格指南

文字和代码的规范和风格，请遵照 [样式规范](style.md)。

## 克隆仓库

参考 [Git 教程](https://git-scm.com/book/zh/v2/GitHub - 对项目做出贡献) 创建 Fork，并将代码仓库克隆到本地。

```git
git clone https://github.com/your-username/distributed-python.git
```

## 环境配置

准备环境：

* 选择一个包管理工具，比如 `conda` 或者 `venv`
* 安装 Python >= 3.8
* 安装 requirements.txt 中的各个依赖。包括本书各个案例所需要的工具 Dask、Ray 等，以及本电子书构建工具 d2lbook：

```bash
pip install -r requirements.txt
```

若 d2lbook 安装失败，请参考 [d2lbook 官方文档](https://book.d2l.ai/install.html) 安装。

## 构建 HTML 格式

- 从 `.md` 文件开始构建工程：

使用 `build_from_scratch.sh`，转换为 HTML 格式，并拷贝到 `docs` 目录：

```bash
sh build_from_scratch.sh
```

- 从 `.ipynb` 文件开始构建工程：

由于 d2lbook 使用了名为 [notedown](https://github.com/d2l-ai/notedown/) 工具，将 `.md` 文件运行，并转化为 `.ipynb` 文件，这个过程只使用了 1 个 CPU 核心，那意味着运行每个 `.ipynb` 文件的速度较慢，可能超时，部分 `.md` 文件可能无法生成 `.ipynb`。

解决办法：我们将 `_build/eval/` 内容也加进了 git 仓库，每次只对有改动的 `.md` 文件转换为 `.ipynb` 并运行，例如，修改了 `ch-xxxx/yyyy.md`，构建时，调用该命令，重新生成对应的 `.ipynb`：

```bash
notedown ch-xxxx/yyyy.md --run --timeout=1200 > _build/eval/ch-xxxx/yyyy.ipynb
```

然后运行下面的命令从已经有运行结果的 `.ipynb` 转化为 HTML，并拷贝到 `docs` 目录：

```bash
sh build_from_eval_ipynb.sh
```

## 部署到 GitHub Pages

本项目的 HTML 部署在 GitHub Pages 上，GitHub Pages 读取本项目中 `docs` 目录下内容。在生成 HTML 格式后，请检查 `docs` 目录下内容已更新。

## 启动 HTTP Server

构建好 HTML 文件后，如果是在自己的个人电脑，可以使用 Python 自带的 HTTP Server，并在浏览器里打开 http://127.0.0.1:8000 查看效果：

```bash
cd docs
python -m http.server 8000
```