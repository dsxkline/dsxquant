# Dsxquant

Dsxquant 是一个基于python语言开发的的量化工具箱，主要特征是其工具属性，专为上层策略应用提供服务。

## 框架设计
Dsxquant 采用模块化设计思想，通过事件驱动整合各个模块的功能。

框架采用事件驱动机制，集成了数据、回测、策略、因子、仿真、资管、交易等模块。

以下是Dsxquant的框架设计图

## 数据结构

文档数据结构描述主要基于Pandas的 Series 和DataFrame，框架接口都支持返回Json数据，Series、DataFrame，支持 csv 文件转换等。

## 安装
Dsxquant 托管在 Github,Gitee,PyPi，默认采用PyPi包安装方式

### 1、PyPi 安装

```
pip install dsxquant
```

### 2、Git 源码安装导入

```
git clone https://github.com/dsxkline/dsxquant.git
```

### 3、安装依赖

```
# pandas==1.5.1
```

## 快速上手

安装后直接导入包即可使用

默认无需注册，框架内置了免费的服务器地址和端口号，如果发现服务器无法连接，请联系客服获取最新服务器地址

``` python
import dsxquant
# 连接 默认无需注册即可使用
dd = dsxquant.dataser()
if dd.connect():
   # 读取实时行情
   result = dd.get_quotes("sh000001,sh600000").series()
   print(result)
```
