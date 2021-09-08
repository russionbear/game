#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :testMap.py
# @Time      :2021/9/5 15:21
# @Author    :russionbear




if __name__ == "__main__":
while 1:
    try:
        data = float(input('输入石油的量，单位为加仑\n'))
    except:
        pass
    else:
        break

d1 = data * 3.78
d2 = data/19.5
if d2 > int(d2):
    d2 += 1
d3 = data * 20
d4 = data * 115000/75700
d5 = data * 3.00
print('\n{}公斤汽油\n生产所需要{}桶石油\n可产生{}磅二氧化碳\n等效于{}加仑乙醇\n价值为{}美元\n'\
      .format(d1, d2, d3, d4,d5))

data = float(input('输入石油的量，单位为加仑\n'))

d1 = data * 3.78
d2 = data // 19.5
d3 = data * 20
d4 = data * 115000 / 75700
d5 = data * 3.00
print('\n{}公斤汽油\n生产所需要{}桶石油\n可产生{}磅二氧化碳\n等效于{}加仑乙醇\n价值为{}美元\n' \
      .format(d1, d2, d3, d4, d5))
