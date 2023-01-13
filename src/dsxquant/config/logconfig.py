#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置

日志输出
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')

Created on Tue Nov 15 15:05:51 2022

@author: fengming
"""
import os
import logging,logging.config
import datetime
# 定义日志文件目录
logfile_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # log文件的目录，需要自定义文件路径
logfile_dir = os.path.join(logfile_dir, 'log')
logfile_info_dir = os.path.join(logfile_dir, 'info')
logfile_debug_dir = os.path.join(logfile_dir, 'debug')
logfile_error_dir = os.path.join(logfile_dir, 'error')
logfile_collect_dir = os.path.join(logfile_dir, 'info')

# 如果不存在定义的日志目录就创建一个
if not os.path.isdir(logfile_dir):
    os.mkdir(logfile_dir)
if not os.path.isdir(logfile_info_dir):
    os.mkdir(logfile_info_dir)
if not os.path.isdir(logfile_debug_dir):
    os.mkdir(logfile_debug_dir)
if not os.path.isdir(logfile_error_dir):
    os.mkdir(logfile_error_dir)
if not os.path.isdir(logfile_collect_dir):
    os.mkdir(logfile_collect_dir)

#日期
today = datetime.datetime.now().strftime('%Y-%m-%d')
 
# log配置字典
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]'
        },
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
        'collect': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        # 打印到终端的日志
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 打印到文件的日志,收集info及以上的日志
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(logfile_info_dir, today+".log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 3,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # 打印到文件的日志:收集错误及以上的日志
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(logfile_error_dir, today+".log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # 打印到文件的日志
        'collect': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(logfile_collect_dir, today+".log"),
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 5,
            'formatter': 'collect',
            'encoding': "utf-8"
        }
    },
    'loggers': {
        # logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': ['default', 'console', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # logging.getLogger('collect')拿到的logger配置
        'collect': {
            'handlers': ['console', 'collect'],
            'level': 'INFO',
        }
    },
}

def load_logging_cfg():
    logging.config.dictConfig(LOGGING)  # 导入上面定义的logging配置
    logger = logging.getLogger(__name__)  # 生成一个log实例
    return logger
 
logger = logging.getLogger(__name__)  # 生成一个log实例

logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    load_logging_cfg()

