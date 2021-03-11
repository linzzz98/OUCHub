如何在Splinx中使用Github Emoji表情 |:fire:|
=======================================================

1. 安装 ``sphinxemoji``

    ::

        pip install sphinxemoji

2. 修改 conf.py 文件 ``extensions``

    ::

        extensions = [
            '...',
            'sphinxemoji.sphinxemoji'
        ]


3. 在 conf.py 中 添加 ``sphinxemoji_style``

    ::

        sphinxemoji_style = 'twemoji'


4. 效果展示

    =============  =============  =============  =============
    效果              代码              效果          代码
    =============  =============  =============  =============
      |:smile:|     `|:smile:|`      |:star:|      `|:star:|`
        ···             ···            ···            ···
    =============  =============  =============  =============

    \ `emoji展示链接 <https://github.com/leoyaojy/tips/issues/11>`_

