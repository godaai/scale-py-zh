# 构建指南

本书基于名为 [Jupyter Book](https://jupyterbook.org/) 的 Python 工具构建，并部署在 GitHub Pages 上。本书主要内容使用 `.ipynb` 和 `.md` 文件保存。Jupyter Book 工具可以将 `.ipynb` 或 `.md` 文件转化为 HTML 格式。

## 文字与代码风格指南

文字和代码的规范和风格，请遵照 [样式规范](style.md)。

## 克隆仓库

参考 [Github Desktop 教程](https://www.classicpress.net/github-desktop-a-really-really-simple-tutorial/) 或 [Git 教程](https://git-scm.com/book/zh/v2/GitHub-对项目做出贡献) 创建 Fork，并将代码仓库克隆到本地。

```bash
git clone https://github.com/<username>/scale-py-zh.git
```

## 环境配置

准备环境：

* 选择一个包管理工具，比如 `conda`。
* 安装 Python >= 3.8
* 安装 requirements.txt 和 requirements-dev.txt 中的各个依赖。包括本书各个案例所需要的工具 pandas 等，以及本电子书构建工具 Jupyter Book：

```bash
conda create -n dispy
source activate dispy
conda install python=3.11 anaconda::graphviz
pip install -r requirements.txt
```

## 构建 HTML 格式

进入该项目文件夹，对项目进行构建：

```bash
sh build.sh
```

## 启动 HTTP Server

构建好 HTML 文件后，如果是在自己的个人电脑，可以使用 Python 自带的 HTTP Server，并在浏览器里打开 http://127.0.0.1:8000 查看效果：

```bash
cd docs
python -m http.server 8000
```

之后会在 `_build` 目录下生成各类网页相关文件。

## 部署到 GitHub Pages

本项目的 HTML 部署在 GitHub Pages 上，GitHub Pages 读取本项目中 `docs` 目录下内容。在生成 HTML 格式后，请检查 `docs` 目录下内容已更新。