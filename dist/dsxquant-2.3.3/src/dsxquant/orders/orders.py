import datetime
import math
from typing import Dict

import pandas as pd
from dsxquant import EventType,PositionStatus,logger
import numpy as np

"""
回测指标计算方法
https://www.dsxquant.com/open-arithmetic/2023/03/1597/
"""

class Orders:
    order_list = {}
    def __init__(self,sid,symbol,norisk) -> None:
        self.sid = str(id(sid))+symbol
        # print(self.sid)
        # 根据策略ID分配订单
        if self.sid not in Orders.order_list.keys():
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
            self.fails = 0
            # 收益率,资产收益率
            self.rate = 0
            # 交易收益率
            self.trade_rate = 0
            # 收益率历史
            self.rate_list = []
            # 年化收益率 = [(1 + 总收益率) ^ (365 / 回测天数)] - 1
            self.year_rate = 0
            # 最大回撤
            self.max_drawdown = 0
            # 盈利
            self.profit = 0
            # 亏损
            self.loss = 0
            # 盈亏比
            self.profit_loss_rate = 0
            # 交易成本，用来计算交易收益率，花了多少钱，收益多少
            self.buy_amount = 0
            # 单次最大收益率
            self.max_rate = 0
            # 单次收益最小值
            self.min_rate = 0
            # 持股天数
            self.days = sid.days
            # 夏普比率
            self.sharpe_ratio = 0
            # 无风险收益率
            self.norisk = norisk
            # 资产流水
            self.funds_flow = []
            # 总资产
            self.funds = sid.funds
            # 初始资产
            self.init_funds = self.funds
            # 总交易量
            self.trade_amount = 0
            # 持仓累计市值
            self.position_amount = 0
            # 持仓总周期数
            self.positions_days = 0
            # 周期收益曲线
            self.everyday_rate = []

        else:
            orders:Orders = Orders.order_list.get(self.sid)
            # 获取实例的自定义属性
            custom_attributes = [attr for attr in dir(orders) if not callable(getattr(orders, attr)) and not attr.startswith("__")]
            # 继承自定义属性
            for attr in custom_attributes:
                setattr(self,attr,getattr(orders,attr))

        Orders.order_list[self.sid] = self

    def insert(self,name,symbol,market,price,amount,date,trade_type:EventType,norisk,desc) -> None:
        self.position(name,symbol,market,price,amount,date,trade_type,norisk,desc)
        self.sell_income(name,symbol,market,price,amount,date,trade_type,norisk,desc)
        return True
    
    def position(self,name,symbol,market,price,amount,date,trade_type:EventType,norisk,desc):
        order:Orders = self.order_list.get(self.sid)
        if order:
            # 查找持仓
            position:tuple = ()
            if symbol in order.positions.keys():
                position = order.positions.get(symbol)
            # 每笔订单号
            oid = symbol+date+trade_type
            date = date[:8]
            if not position and trade_type==EventType.BUY:
                # 买入第一笔持仓
                start_date = date
                sell_price = 0
                sell_amount = 0
                days = 0
                wins = 0
                fails = 0
                rate = 0
                profit = 0
                loss = 0
                total_amount = amount
                # 名称，代码，市场，价格，股数，日期，状态，总股数，开仓日期，平仓价，持股天数，盈利次数，亏损次数，盈利，亏损，收益率
                position = [name,symbol,market,price,amount,date,PositionStatus.HOLDING,total_amount,start_date,sell_price,days,wins,fails,profit,loss,rate]
                order.positions[symbol] = position
                od = (oid,name,symbol,market,price,amount,date,trade_type,start_date,sell_price,sell_amount,days,wins,fails,profit,loss,rate,desc)
                order.orders[oid] = od
                order.buy_orders.append(od)
                order.funds_flow.append((oid,symbol,trade_type,amount*price,date,desc))
                order.funds -= amount*price
            else:
                if position:
                    n,s,m,p,a,d,s,ta,sd,sp,days,wins,fails,profit,loss,rate = position
                    # 持有天数，两个时间相减
                    days = datetime.datetime.strptime(date.split(" ")[0],"%Y%m%d") - datetime.datetime.strptime(sd.split(" ")[0],"%Y%m%d")
                    days = days.days
                    # 持仓股数和价格合并计算
                    if trade_type == EventType.BUY:
                        # 可用资金
                        if amount * price > order.funds:
                            logger.debug("可用资金不足 %s" % order.funds)
                            return
                        # 买入合并
                        total = amount * price + a*p
                        # 得到买入均价
                        p = round(total / (amount + a),2)
                        a += amount
                        position = [name,symbol,market,p,a,date,PositionStatus.HOLDING,ta+amount,sd,sp,days,wins,fails,profit,loss,rate]
                        order.funds -= amount*price
                    if trade_type == EventType.SELL:
                        # 是否有可卖股数
                        if not self.can_sell_amount(symbol,market,date): return
                        # 卖出收益
                        income = round(amount * (price - p),2)
                        if income>0: 
                            wins += 1
                            profit = income
                        else:
                            fails += 1
                            loss = income
                        #收益率
                        rate = round((price - p) / p * 100,2)
                        # 卖出合并
                        a -= amount
                        s = PositionStatus.HOLDING
                        
                        if a<=0:
                            # 平仓
                            s = PositionStatus.CLOSED
                        position = [name,symbol,market,p,a,date,s,ta+amount,sd,price,days,wins,fails,profit,loss,rate]
                        order.funds += amount*price
                        
                    if s!=PositionStatus.CLOSED:
                        order.positions[symbol] = position
                    else:
                        # 平仓后pop，并保存已平仓数据
                        order.positions_closed.append(position)
                        order.positions.pop(symbol)

                    od = (oid,name,symbol,market,price,amount,date,trade_type,date,0,0,0,0,0,0,0,0,desc)
                    order.orders[oid] = od
                    order.funds_flow.append((oid,symbol,trade_type,amount*price,date,desc))
                    if trade_type==EventType.BUY:order.buy_orders.append(od)
                else:
                    pass
                    # logger.info("没有持仓数据,忽略")

    def can_sell_amount(self,symbol,market,date):
        order:Orders = self.order_list.get(self.sid)
        if order and order.buy_orders:
            for item in order.buy_orders:
                d = item[6]
                # 当前日期大于买入订单的日期才算有可卖股数 践行T+1
                if int(date)>int(d):
                    return True



    def sell_income(self,name,symbol,market,price,amount,date,trade_type:EventType,norisk,desc):
        date = date[:8]
        if trade_type==EventType.SELL:
            # 是否有可卖股数
            if not self.can_sell_amount(symbol,market,date): return
            # 首先卖出最早的订单
            order:Orders = self.order_list.get(self.sid)
            if order and order.buy_orders:
                # 卖出计算每笔交易的收益
                old_order = order.buy_orders[0]
                oid,n,s,m,p,a,d,t,start_date,sell_price,sell_amount,days,wins,fails,profit,loss,rate,de = old_order
                # 持有天数，两个时间相减
                days = datetime.datetime.strptime(date.split(" ")[0],"%Y%m%d") - datetime.datetime.strptime(start_date.split(" ")[0],"%Y%m%d")
                days = days.days
                # self.days += days
                # 收益
                income = round(amount * (price-p),2)
                if income>0: 
                    profit = income
                    wins += 1
                    order.profit += income
                    order.wins += 1
                else:
                    order.loss += income
                    order.fails += 1
                    loss = income
                    fails += 1
                # 盈亏比
                order.profit_loss_rate = round(self.loss!=0 and order.profit / abs(order.loss) or 0,2)
                # 交易总成本
                order.buy_amount += a*p
                # 收益率 = （当前价格-持仓价格） / 持仓价格
                rate = round((price - p) / p * 100,2)
                order.rate_list.append(rate/100)
                order.max_rate = max(order.max_rate,rate)
                order.min_rate = min(order.min_rate,rate)
                # 总的收益率,这个计算的资产收益率
                order.rate = round(((order.profit+order.loss) / order.init_funds) * 100,2)
                # 交易资金收益率，计算用于交易的资金的收益率，意思就是你花了多少钱赚了多少钱
                order.trade_rate = round(((order.profit+order.loss) / order.buy_amount) * 100,2)
                # 年化收益率 = [(1 + 总收益率) ^ (365 / 回测天数)] - 1
                order.year_rate = np.real((1.0+order.rate/100) ** (365/order.days) - 1.0)
                order.year_rate = round(order.year_rate*100,2)
                # 胜率
                win_rate = round(order.wins/(order.wins+order.fails)*100,2)
                # 回撤 = (最大净值-最低净值) / 最大净值
                max_jz = order.max_rate/100 + 1
                jz = rate/100 + 1
                drawdown = round((max_jz - jz) / max_jz * 100,2)
                order.max_drawdown = max(order.max_drawdown,drawdown)
                # 夏普比率
                rate_series = pd.Series(order.rate_list)
                # 无风险收益率
                risk_free_rate = order.norisk/100
                # 平均收益率
                mean_return = np.mean(rate_series)
                # 收益率标准差
                std_return = np.std(rate_series)
                # 夏普比率
                order.sharpe_ratio = std_return!=0 and round((mean_return - risk_free_rate) / std_return,2) or 0
                # 剩余资产
                funds = order.init_funds + order.profit + order.loss
                # 交易次数
                trade_times = order.wins + order.fails
                # 持有天数，交易次数，收益率，资产收益率，年化收益率，夏普比率，盈亏比，胜率，最大回撤，最大收益，最小收益,总资产,盈利,亏损
                record = (order.days,trade_times,order.trade_rate,order.rate,order.year_rate,order.sharpe_ratio,order.profit_loss_rate,win_rate,
                          order.max_drawdown,order.max_rate,order.min_rate,round(funds,2),round(order.profit,2),round(order.loss,2)
                          )
                order.records = [record]
                # 更新订单表
                real_order = order.orders.get(oid)
                ri,rn,rs,rm,rp,ra,rd,rt,rstart_date,rsell_price,rsell_amount,rdays,rwins,rfails,rprofit,rloss,rrate,rde = real_order
                # 计算卖出均价
                rsell_price = (a * price + rsell_amount*rsell_price) / (a + rsell_amount)
                rsell_amount += a
                # 更新订单
                order.orders[oid] = (ri,rn,rs,rm,rp,ra,date,rt,rstart_date,rsell_price,rsell_amount,days,wins,fails,profit,loss,rate,rde+" "+desc)
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
    
    def update_rate(self,name,symbol,market,date:str,close:float):
        """更新每日收益
        """
        rates = self.get_income_from_day(name,symbol,market,date,close)
        if(rates) : self.everyday_rate.append(rates)

    def get_income_from_day(self,name,symbol,market,date:str,close:float):
        # 买入成本，用总收益/成本就能计算收益率
        total_cost = 0
        # 总收益
        total_income = 0
        # 买入股数 用来计算持仓成本
        buy_amount = 0
        # 剩余股数，相当于当前持仓股数，用来计算浮动收益
        amounts = 0
        # 持仓成本
        position_cost = 0
        for key,item in self.orders.items():
            # ['订单id', '股票名称','代码', '市场','价格','股数','平仓日期','类型','开仓日期','卖出价格','卖出股数','持股天数','盈利次数','亏损次数','盈利','亏损','收益率%',"备注"]
            id,n,s,m,p,a,d,t,start_date,sell_price,sell_amount,days,wins,fails,profit,loss,rate,de = item
            if int(start_date)>int(date): break
            amounts += t=="buy" and a or -a
            buy_amount += t=="buy" and a or 0
            total_cost += t=="buy" and round(a*p,3) or 0
            # 如果是在当前日期之前卖出，就计算卖出的收益
            if(int(d)<int(date)):
                total_income += profit + loss
        
        # 没有持仓说明没有交易了，不要了
        if amounts<=0:return

        # 持仓成本
        position_cost = buy_amount>0 and round(total_cost / buy_amount,3) or 0
        # 浮动收益
        float_rate = 0
        if(amounts>0):
            float_rate = round(amounts * (close - position_cost),3)
        total_income += float_rate
        # 收益率
        rate = total_cost>0 and round(total_income / total_cost * 100,3) or 0
        if(total_cost==0 and rate==0) : return
        # 日期,股票名称,股票代码,市场,总收益,总成本,收益率
        return (date,name,symbol,market,round(total_income,2),total_cost,rate)