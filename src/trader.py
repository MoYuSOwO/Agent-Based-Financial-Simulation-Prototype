from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import pareto

class Trader(ABC):

    MARKET_IMPACT_COEF = 0.15

    def __init__(self, cash: float, positions: float):
        self.__cash = cash
        self.__positions = positions
        self.__order_positions = 0
        self.__cooldown = 0

    @abstractmethod
    def tick_decision(self) -> int:
        pass

    def get_cash(self) -> int:
        return self.__cash
    
    def get_positions(self) -> int:
        return self.__positions
    
    def finish_position_change(self, current_price: float, depth: float) -> int:
        maxn = np.floor(depth * self.MARKET_IMPACT_COEF)
        if self.__order_positions < 0:
            finish_order = max(self.__order_positions, -maxn)
        elif self.__order_positions > 0:
            finish_order = min(self.__order_positions, maxn)
        else:
            return 0
        self.__order_positions -= finish_order
        if finish_order > 0 and self.__cash < finish_order * current_price:
            amount = np.floor(self.__cash / current_price)
            self.__positions += amount
            self.__cash -= amount * current_price
            self.__order_positions = 0
            return amount
        elif finish_order < 0 and self.__positions + finish_order < 0:
            amount = self.__positions
            self.__cash += amount * current_price
            self.__positions = 0
            self.__order_positions = 0
            return -amount
        else:
            self.__positions += finish_order
            self.__cash -= finish_order * current_price
            return finish_order

    def trade(self, positions: int) -> None:
        if self.__positions + self.__order_positions < -positions:
            positions = -int(self.__positions + self.__order_positions)
        self.__order_positions += positions
    
    def is_cooldown(self) -> bool:
        if self.__cooldown > 0:
            self.__cooldown -= 1
            return True
        else:
            return False
        
    def set_cooldown(self, cooldown: int) -> None:
        self.__cooldown = cooldown

class RandomTrader(Trader): #400

    AVERAGE_BUY = 15
    AVERAGE_SELL = 15
    AVERAGE_WAIT = 5.0
    MIN_START_CASH = 6000.0
    MAX_START_CASH = 12000.0
    MIN_START_POSITION = 100
    MAX_START_POSITION = 300
    BANKRUPTCY_CASH = 600.0

    def __init__(self) -> None:
        cash = np.random.uniform(self.MIN_START_CASH, self.MAX_START_CASH)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
        self.set_cooldown(int(np.random.exponential(self.AVERAGE_WAIT)))
    
    def tick_decision(self, current_price: float, depth: float) -> int:
        if self.is_cooldown() is False:
            self.set_cooldown(int(np.random.exponential(self.AVERAGE_WAIT)))
            if self.get_cash() < self.BANKRUPTCY_CASH:
                amount = max(np.floor((self.BANKRUPTCY_CASH - self.get_cash()) / current_price * 2.0), np.floor(np.random.exponential(self.AVERAGE_SELL)))
                amount = max(1, amount)
                self.trade(-amount)
            else:
                random = np.random.rand()
                if random < 0.4:
                    self.trade(max(1, np.floor(np.random.exponential(self.AVERAGE_BUY))))
                elif 0.4 <= random < 0.8:
                    self.trade(-max(1, np.floor(np.random.exponential(self.AVERAGE_SELL))))
                else:
                    self.trade(0)
        amount = self.finish_position_change(current_price, depth)
        # print("random: " + str(amount))
        return amount

class TrendTrader(Trader): #600

    MIN_START_CASH = 6000.0
    MAX_START_CASH = 12000.0
    MIN_START_POSITION = 100
    MAX_START_POSITION = 300
    BUY_MIN = 0.1
    BUY_MAX = 0.2
    SELL_MIN = 0.2
    SELL_MAX = 0.3
    BANKRUPTCY_CASH = 600.0

    def __init__(self) -> None:
        cash = np.random.uniform(self.MIN_START_CASH, self.MAX_START_CASH)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
        self.__decision_time = np.random.randint(120, 360)
        self.__buy_judge = np.random.uniform(1.02, 1.08)
        self.__sell_judge = 1 / self.__buy_judge
        self.__risk_judge = np.random.uniform(1.2, 1.8)
        self.set_cooldown(int(self.__decision_time * 3))

    def get_MA_t(self, price_1080ticks: list, t: int) -> float:
        length = len(price_1080ticks)
        if length == 0:
            return 0
        if length < t:
            return sum(price_1080ticks) / length
        else:
            price_t_ticks = price_1080ticks[-t:]
            return sum(price_t_ticks) / t

    def tick_decision(self, current_price: float, price_1080ticks: list, MSI: float, depth: float) -> int:
        if self.get_cash() < self.BANKRUPTCY_CASH:
            amount = max(1, np.floor((self.BANKRUPTCY_CASH - self.get_cash()) / current_price * 1.5))
            self.trade(-amount)
        elif self.is_cooldown() is False:
            self.set_cooldown(int(np.random.exponential(self.__decision_time)))
            MA_t = self.get_MA_t(price_1080ticks, self.__decision_time)
            MA_3t = self.get_MA_t(price_1080ticks, self.__decision_time * 3 - 1)
            if MA_t == 0:
                return 0
            if MA_t > MA_3t * self.__risk_judge:
                amount = np.floor(np.random.uniform(self.SELL_MIN, self.SELL_MAX) * self.get_positions())
                self.trade(-amount * 2)
            if MA_t > MA_3t * self.__buy_judge:
                amount = np.floor(self.get_cash() / current_price * np.random.uniform(self.BUY_MIN, self.BUY_MAX))
                self.trade(amount)
            elif MA_t < MA_3t * self.__sell_judge:
                amount = np.floor(np.random.uniform(self.SELL_MIN, self.SELL_MAX) * self.get_positions())
                self.trade(-amount)
        amount = self.finish_position_change(current_price, depth)
        # print("trend: " + str(amount))
        return amount

class ValueTrader(Trader): #400

    MIN_START_CASH = 6000.0
    MAX_START_CASH = 12000.0
    MIN_START_POSITION = 100
    MAX_START_POSITION = 300
    DECISION_DEVIATION_SCALE = 0.035
    BUY_MIN = 0.1
    BUY_MAX = 0.2
    SELL_MIN = 0.2
    SELL_MAX = 0.3
    AVERAGE_WAIT = 240.0
    BANKRUPTCY_CASH = 600.0

    def __init__(self) -> None:
        cash = np.random.uniform(self.MIN_START_CASH, self.MAX_START_CASH)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
        self.set_cooldown(int(np.random.exponential(self.AVERAGE_WAIT)))
        self.__judge_coef = np.random.uniform(-0.05, 0.05)

    def tick_decision(self, current_price: float, basic_value: float, depth: float) -> int:
        if self.get_cash() < self.BANKRUPTCY_CASH:
            amount = max(1, np.floor((self.BANKRUPTCY_CASH - self.get_cash()) / current_price * 1.5))
            self.trade(-amount)
        elif self.is_cooldown() is False:
            self.set_cooldown(int(np.random.exponential(self.AVERAGE_WAIT)))
            basic_value *= 1 + np.random.normal(0, self.DECISION_DEVIATION_SCALE)
            buy_signal = 0.9 * basic_value * (1 + self.__judge_coef)
            sell_signal = 1.1 * basic_value * (1 + self.__judge_coef)
            if current_price < buy_signal:
                amount = np.floor(self.get_cash() / current_price * np.random.uniform(self.BUY_MIN, self.BUY_MAX))
                self.trade(amount)
            elif current_price > sell_signal:
                amount = np.floor(self.get_positions()  * np.random.uniform(self.SELL_MIN, self.SELL_MAX))
                self.trade(-amount)
        amount = self.finish_position_change(current_price, depth)
        # print("value: " + str(amount))
        return amount
