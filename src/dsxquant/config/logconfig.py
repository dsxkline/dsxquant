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
from dsxquant.config import config
import logging,logging.config

if config.DSXDEBUG:
    LOGLEVEL = logging.DEBUG
else:
    LOGLEVEL = logging.INFO
logger = logging.getLogger("dsxquant")  # 生成一个log实例
handle = logging.StreamHandler()
formater = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s')
handle.setFormatter(formater)
logger.addHandler(handle)
logger.setLevel(LOGLEVEL)
