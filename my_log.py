#!/usr/bin/python3
#coding=utf-8

import logging

import my_cfg

def log(msg):
    '''
    错误输出
    :param msg: 消息信息
    :return:
    '''
    print(msg)
    logging.info(msg)

def init_log():
    cfg = my_cfg.my_config()

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=cfg.log_file,
                        level=logging.INFO,
                        format=LOG_FORMAT)
