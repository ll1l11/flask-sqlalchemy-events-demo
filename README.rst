同步MySQL表到Elastcisearch
==========================

使用 pipenv_ 管理依赖

安装依赖::

    pipenv install


修改配置文件中数据库配置, 创建database


启动工程::

    pipenv run python hello.python


创建table,浏览器访问::

    localhost:5000/create_all

默认使用localhost无密码的 elasticsearch_.


.. _pipenv: https://docs.pipenv.org/
.. _elasticsearch: https://www.elastic.co/cn/products/elasticsearch
