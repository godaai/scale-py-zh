author = 'Weizheng Lu'
bibtex_bibfiles = ['references.bib']
bibtex_reference_style = 'author_year'
comments_config = {'hypothesis': False, 'utterances': False}
copyright = '2023-2024'
exclude_patterns = ['**.ipynb_checkpoints', '.DS_Store', 'Thumbs.db', '_build']
extensions = ['sphinx_togglebutton', 'sphinx_copybutton', 'myst_nb', 'jupyter_book', 'sphinx_thebe', 'sphinx_comments', 'sphinx_external_toc', 'sphinx.ext.intersphinx', 'sphinx_design', 'sphinx_book_theme', 'sphinxcontrib.bibtex', 'sphinx_jupyterbook_latex']
external_toc_exclude_missing = True
external_toc_path = '_toc.yml'
html_baseurl = ''
html_favicon = ''
html_logo = 'logo.png'
html_sourcelink_suffix = ''
html_theme = 'sphinx_book_theme'
html_theme_options = {
    'search_bar_text': '搜索...', 
    'launch_buttons': {'notebook_interface': 'classic', 'binderhub_url': '', 'jupyterhub_url': '', 'thebe': False, 'colab_url': ''}, 
    'path_to_docs': 'docs', 
    'repository_url': 'https://github.com/godaai/distributed-python', 
    'repository_branch': 'main', 
    'extra_footer': '', 
    'home_page_in_toc': True, 
    'announcement': "如果你觉得内容对你有帮助，请在 <a href=\"https://github.com/godaai/distributed-python\">GitHub</a> 上点个 star 吧！", 
    'analytics': {'google_analytics_id': ''}, 
    'use_repository_button': True, 
    'use_edit_page_button': False, 
    'use_issues_button': False,
    "toc_title": "本节目录",
}
html_title = 'Python 分布式编程'
latex_engine = 'pdflatex'
myst_enable_extensions = ['colon_fence', 'dollarmath', 'linkify', 'substitution', 'tasklist']
myst_url_schemes = ['mailto', 'http', 'https']
nb_execution_allow_errors = False
nb_execution_cache_path = ''
nb_execution_excludepatterns = []
nb_execution_in_temp = False
nb_execution_mode = 'off'
nb_execution_timeout = 30
nb_output_stderr = 'show'
numfig = True
numfig_format = {'figure': '图 %s', 'table': '表 %s', 'code-block': '代码片段 %s', 'section': '章节 %s'}
pygments_style = 'sphinx'
suppress_warnings = ['myst.domains']
use_jupyterbook_latex = True
use_multitoc_numbering = True
