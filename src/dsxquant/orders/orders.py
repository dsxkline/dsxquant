from typing import Dict
from dsxquant import EventType,PositionStatus,logger

"""
收益率（Returns）：回测期内策略的总收益率。
年化收益率（Annualized Returns）：以年为单位计算的收益率。 年化收益率 = [(1 + 总收益率) ^ (365 / 回测天数)] - 1
最大回撤（Max Drawdown）：回测期内，从任意一天开始计算，之后任意一天的收益率高于该天的最大值时，最大亏损幅度的百分比。
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
    def __init__(self,sid) -> None:
        self.sid = sid
        # 根据策略ID分配订单
        if sid not in self.order_list:
            self.orders = []
            self.positions = {}
            self.positions_closed = []
            # 获胜次数
            self.wins = 0
            # 收益率
            self.returns = 0
            # 总收益率
            self.total_returns = 0
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
        else:
            orders:Orders = self.order_list.get(self.sid)
            self.orders = orders.orders
            self.positions = orders.positions
            self.positions_closed = orders.positions_closed
        self.order_list[sid] = self

    def insert(self,name,symbol,market,price,amount,date,trade_type:EventType) -> None:
        self.position(name,symbol,market,price,amount,date,trade_type)
    
    def position(self,name,symbol,market,price,amount,date,trade_type:EventType):
        order:Orders = self.order_list.get(self.sid)
        if order:
            # 查找持仓
            position:tuple = ()
            if symbol in order.positions.keys():
                position = order.positions.get(symbol)
            if not position and trade_type==EventType.BUY:
                # 买入第一笔持仓
                position = [name,symbol,market,price,amount,date,PositionStatus.HOLDING]
                order.positions[symbol] = position
                order.orders.append((name,symbol,market,price,amount,date,trade_type))
            else:
                if position:
                    n,s,m,p,a,d,s = position
                    # 收益
                    income = amount * (price-p)
                    if income>0: 
                        self.profit += income
                        self.wins += 1
                    else:
                        self.loss += income
                    # 盈亏比
                    self.profit_loss_rate = self.loss!=0 and self.profit / abs(self.loss) or 0
                    # 收益率 = （当前价格-持仓价格） / 持仓价格
                    self.returns = (price - p) / p
                    self.max_returns = max(self.max_returns,self.returns)
                    self.min_returns = min(self.min_returns,self.returns)
                    # 总的收益率
                    self.total_returns += self.returns
                    

                    # 持仓股数和价格合并计算
                    if trade_type == EventType.BUY:
                        # 买入合并
                        total = amount * price + a*p
                        # 得到买入均价
                        p = round(total / (amount + a),2)
                        a += amount
                        position = [name,symbol,market,p,a,date,PositionStatus.HOLDING]
                    if trade_type == EventType.SELL:
                        # 卖出收益
                        income = amount * (price - p)
                        # 卖出合并
                        a -= amount
                        s = PositionStatus.HOLDING
                        
                        if a<=0:
                            # 平仓
                            s = PositionStatus.CLOSED
                        position = [name,symbol,market,p,amount,date,s]
                    
                    
                    if s!=PositionStatus.CLOSED:
                        order.positions[symbol] = position
                    else:
                        # 平仓后pop，并保存已平仓数据
                        order.positions_closed.append(position)
                        order.positions.pop(symbol)

                    order.orders.append((name,symbol,market,price,amount,date,trade_type))
                else:
                    logger.info("没有持仓数据,忽略")



