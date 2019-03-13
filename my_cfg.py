#!/usr/bin/python3
#coding=utf-8

import os
import configparser

CONFIG_FILE = r"./sjs_test.ini"

class my_config:
    '''
    获取配置
    '''

    def __init__(self):
        if os.path.exists(CONFIG_FILE):
            self.get_config(CONFIG_FILE)
        else:
            print("读取配置文件[%s]失败。" % CONFIG_FILE)

    def get_config(self, cfg_file):
        '''
        读取配置文件
        :param cfg_file: 配置文件名
        :return:
        '''
        config = configparser.ConfigParser()
        config.read(cfg_file)
        sections = config.sections()

        self.userid = config['USER']['userid']
        self.passwd = config['USER']['passwd']

        self.log_file = config['COMMON']['log_file']


