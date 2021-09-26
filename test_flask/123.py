#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :123.py
# @Time      :2021/9/15 13:14
# @Author    :russionbear

from flask import Flask
app=Flask(__name__)
@app.route('/')
def index():
    return 'hello'

if __name__=='__main__':
    app.run()