#!/usr/bin/python3
#coding=utf-8

class my_exception(Exception):
    def __init__(self, info):
        # super().__init__(self)  # 初始化父类
        self.info = info

    def __str__(self):
        return self.info
