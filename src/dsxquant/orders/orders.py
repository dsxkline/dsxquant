import datetime
import math
from typing import Dict

import pandas as pd
from dsxquant import EventType,PositionStatus,logger
import numpy as np

"""
收益率（Returns）：回测期内策略的总收益率。

年化收益率（Annualized Returns）：以年为单位计算的收益率。 年化收益率 = [(1 + 总收益率) ^ (365 / 回测天数)] - 1

最大回撤（Max Drawdown）：回测期内，从任意一天开始计算，之后任意一天的收益率高于该天的最大值时，最大亏损幅度的百分比。
回撤率 = （净值最高点 - 净值最低点）/ 净值最高点
其中，净值最高点是指从某一时点开始到最近的一个峰值点之间的最高净值，净值最低点则是指该峰值点之后的最低净值。

胜率（Winning Rate）：回测期内，策略盈利交易数占总交易数的比例。
夏普比率（Sharpe Ratio）：回测期内，策略年化收益率与风险（以波动率衡量）之比。
信息比率（Information Ratio）：回测期内，策略年化超额收益率与风险（以基准组合波动率衡量）之比。
Beta：回测期内，策略收益率与市场收益率之间的关系。
Alpha：回测期内，策略相对于市场的超额收益率。
Sortino Ratio：回测期内，策略年化超额收益率与下行波动率之比。
Calmar Ratio：回测期内，策略年化收益率与最大回撤之比。
"""

class Orders:
    order_list = {}
    def __init__(self,sid,symbol) -> None:
        self.sid = str(id(sid))+symbol
        # 根据策略ID分配订单
        if self.sid not in self.order_list:
            # 订单表
            self.orders = {}
            # 持仓表
            self.positions = {}
            # 历史持仓表
            self.positions_closed = []
            # 收益记录
            self.records = []
            # 买入队列
            self.buy_orders = []
            # 获胜次数
            self.wins = 0
            # 收益率
            self.returns = 0
            # 收益率历史
            self.returns_list = []
            # 年化收益率 = [(1 + 总收益率) ^ (365 / 回测天数)] - 1
            self.year_returns = 0
            # 最大回撤
            self.max_drawdown = 0
            # 盈利
            self.profit = 0
            # 亏损
            self.loss = 0
            # 盈亏比
            self.profit_loss_rate = 0
            # 单次最大收益率
            self.max_returns = 0
            # 单次收益最小值
            self.min_returns = 0
            # 持股天数
            self.days = 0
            # 夏普比率
            self.sharpe_ratio = 0
        else:
            orders:Orders = self.order_list.get(self.sid)
            self.orders = orders.orders
            self.positions = orders.positions
            self.positions_closed = orders.positions_closed
            self.records = orders.records
            self.buy_orders = orders.buy_orders
            self.wins = orders.wins
            self.returns = orders.returns
            self.returns_list = orders.returns_list
            self.year_returns = orders.year_returns
            self.max_drawdown = orders.max_drawdown
            self.profit = orders.profit
            self.loss = orders.loss
            self.profit_loss_rate = orders.profit_loss_rate
            self.max_returns = orders.max_returns
            self.min_returns = orders.min_returns
            self.days = orders.days
            self.sharpe_ratio = orders.sharpe_ratio

        self.order_list[self.sid] = self

    def insert(self,name,symbol,market,price,amount,date,trade_type:EventType) -> None:
        self.position(name,symbol,market,price,amount,date,trade_type)
        self.sell_income(name,symbol,market,price,amount,date,trade_type)
    
    def position(self,name,symbol,market,price,amount,date,trade_type:EventType):
        order:Orders = self.order_list.get(self.sid)
        if order:
            # 查找持仓
            position:tuple = ()
            if symbol in order.positions.keys():
                position = order.positions.get(symbol)
            # 每笔订单号
            oid = symbol+date+trade_type
            if not position and trade_type==EventType.BUY:
                # 买入第一笔持仓
                start_date = date
                sell_price = 0
                sell_amount = 0
                days = 0
                wins = 0
                fails = 0
                returns = 0
                profile = 0
                loss = 0
                total_amount = amount
                # 名称，代码，市场，价格，股数，日期，状态，总股数，开仓日期，平仓价，持股天数，盈利次数，亏损次数，盈利，亏损，收益率
                position = [name,symbol,market,price,amount,date,PositionStatus.HOLDING,total_amount,start_date,sell_price,days,wins,fails,profile,loss,returns]
                order.positions[symbol] = position
                od = (oid,name,symbol,market,price,amount,date,trade_type,start_date,sell_price,sell_amount,days,wins,fails,profile,loss,returns)
                order.orders[oid] = od
                order.buy_orders.append(od)
            else:
                if position:
                    n,s,m,p,a,d,s,ta,sd,sp,days,wins,fails,profile,loss,returns = position
                    # 持有天数，两个时间相减
                    days = datetime.datetime.strptime(date.split(" ")[0],"%Y%m%d") - datetime.datetime.strptime(sd.split(" ")[0],"%Y%m%d")
                    days = days.days
                    # 持仓股数和价格合并计算
                    if trade_type == EventType.BUY:
                        # 买入合并
                        total = amount * price + a*p
                        # 得到买入均价
                        p = round(total / (amount + a),2)
                        a += amount
                        position = [name,symbol,market,p,a,date,PositionStatus.HOLDING,ta+amount,sd,sp,days,wins,fails,profile,loss,returns]
                    if trade_type == EventType.SELL:
                        # 卖出收益
                        income = round(amount * (price - p),2)
                        if income>0: 
                            wins += 1
                            profile = income
                        else:
                            fails += 1
                            loss = income
                        #收益率
                        returns = round((price - p) / p * 100,2)
                        # 卖出合并
                        a -= amount
                        s = PositionStatus.HOLDING
                        
                        if a<=0:
                            # 平仓
                            s = PositionStatus.CLOSED
                        position = [name,symbol,market,p,a,date,s,ta+amount,sd,price,days,wins,fails,profile,loss,returns]

                    if s!=PositionStatus.CLOSED:
                        order.positions[symbol] = position
                    else:
                        # 平仓后pop，并保存已平仓数据
                        order.positions_closed.append(position)
                        order.positions.pop(symbol)

                    od = (oid,name,symbol,market,price,amount,date,trade_type,date,0,0,0,0,0,0,0,0)
                    order.orders[oid] = od
                    if trade_type==EventType.BUY:order.buy_orders.append(od)
                else:
                    logger.info("没有持仓数据,忽略")



    def sell_income(self,name,symbol,market,price,amount,date,trade_type:EventType):
        if trade_type==EventType.SELL:
            order:Orders = self.order_list.get(self.sid)
            if order and order.buy_orders:
                # 卖出计算每笔交易的收益
                old_order = order.buy_orders[0]
                oid,n,s,m,p,a,d,t,start_date,sell_price,sell_amount,days,wins,fails,profile,loss,returns = old_order
                # 持有天数，两个时间相减
                days = datetime.datetime.strptime(date.split(" ")[0],"%Y%m%d") - datetime.datetime.strptime(start_date.split(" ")[0],"%Y%m%d")
                days = days.days
                self.days += days
                # 收益
                income = round(amount * (price-p),2)
                if income>0: 
                    profile = income
                    wins += 1
                    self.profit += income
                    self.wins += 1
                else:
                    self.loss += income
                    loss = income
                    fails += 1
                # 盈亏比
                self.profit_loss_rate = round(self.loss!=0 and self.profit / abs(self.loss) or 0,2)
                # 收益率 = （当前价格-持仓价格） / 持仓价格
                returns = round((price - p) / p * 100,2)
                self.returns_list.append(returns/100)
                self.max_returns = max(self.max_returns,returns)
                self.min_returns = min(self.min_returns,returns)
                # 总的收益率
                self.returns += returns
                # 年化收益率 = [(1 + 单利收益率) ^ (365 / 持仓天数)] - 1
                self.year_returns = np.real((1.0+self.returns/100) ** (365/self.days) - 1.0)
                self.year_returns = round(self.year_returns*100,2)
                win_rate = round(self.wins/days,2)
                # 回撤 = (最大净值-最低净值) / 最大净值
                max_jz = self.max_returns/100 + 1
                jz = returns/100 + 1
                drawdown = round((max_jz - jz) / max_jz * 100,2)
                self.max_drawdown = max(self.max_drawdown,drawdown)
                # 夏普比率
                returns_series = pd.Series(self.returns_list)
                # 无风险收益率
                risk_free_rate = 0.015
                # 平均收益率
                mean_return = np.mean(returns_series)
                # 标准差
                std_return = np.std(returns_series)
                # 夏普比率
                self.sharpe_ratio = round((mean_return - risk_free_rate) / std_return * 100,2)
                
                # 持有天数，年化收益率，盈亏比，胜率，最大回撤，最大收益，最小收益
                record = (self.days,self.year_returns,self.sharpe_ratio,self.profit_loss_rate,win_rate,self.max_drawdown,self.max_returns,self.min_returns)
                self.records = [record]
                # 更新订单表
                real_order = order.orders.get(oid)
                ri,rn,rs,rm,rp,ra,rd,rt,rstart_date,rsell_price,rsell_amount,rdays,rwins,rfails,rprofile,rloss,rreturns = real_order
                # 计算卖出均价
                rsell_price = (a * price + rsell_amount*rsell_price) / (a + rsell_amount)
                rsell_amount += a
                order.orders[oid] = (ri,rn,rs,rm,rp,ra,rd,rt,rstart_date,rsell_price,rsell_amount,days,wins,fails,profile,loss,returns)
                if amount>a:
                    order.buy_orders.pop(0)
                    # 不够卖，继续卖掉下一个
                    self.sell_income(name,symbol,market,price,amount,date,trade_type)
                elif amount<a:
                    # 没卖完，留着
                    pass
                else:
                    # 刚好卖完了
                    order.buy_orders.pop(0)