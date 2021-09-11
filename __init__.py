#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :__init__.py
# @Time      :2021/9/4 22:02
# @Author    :russionbear
from resource import resource

# EVN = sys.path[0].replace('\\', '/')


if __name__ == "__main__":
    from resource import resource

    resource.makeMapGeoImage((100, 100))