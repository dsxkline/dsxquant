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
import config.config as config
import logging,logging.config
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
    },
    'handlers': {
        # 打印到终端的日志
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        # logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
if config.DSXDEBUG:
    LOGLEVEL = logging.DEBUG
else:
    LOGLEVEL = logging.INFO
logger = logging.getLogger(__name__)  # 生成一个log实例
logger.setLevel(LOGLEVEL)
logging.config.dictConfig(LOGGING)
