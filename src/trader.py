from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import pareto

class Trader(ABC):

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
        if self.__order_positions > 0 and self.__cash < self.__order_positions * current_price:
            amount = np.floor(self.__cash / current_price)
            self.__positions += amount
            self.__cash -= amount * current_price
            self.__order_positions = 0
            return amount
        elif self.__order_positions < 0 and self.__positions + self.__order_positions < 0:
            amount = self.__positions
            self.__cash += amount * current_price
            self.__positions = 0
            self.__order_positions = 0
            return -amount
        else:
            amount = self.__order_positions
            self.__positions += amount
            self.__cash -= amount * current_price
            self.__order_positions = 0
            return amount

    def trade(self, positions: int) -> None:
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

    AVERAGE_TRADE = 15
    AVERAGE_WAIT = 1.0
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
                amount = max(np.floor((self.BANKRUPTCY_CASH - self.get_cash()) / current_price * 2.0), np.floor(np.random.exponential(self.AVERAGE_TRADE)))
                amount = max(1, amount)
                self.trade(-amount)
            else:
                random = np.random.rand()
                if random < 0.4:
                    self.trade(max(1, np.floor(np.random.exponential(self.AVERAGE_TRADE))))
                elif 0.4 <= random < 0.8:
                    self.trade(-max(1, np.floor(np.random.exponential(self.AVERAGE_TRADE))))
                else:
                    self.trade(0)
        amount = self.finish_position_change(current_price, depth)
        # print("random: " + str(amount))
        return amount

class TrendTrader(Trader): #600

    MIN_START_CASH = 20000.0
    MAX_START_CASH = 60000.0
    MIN_START_POSITION = 100
    MAX_START_POSITION = 300
    BUY_MIN = 0.1
    BUY_MAX = 0.3
    SELL_MIN = 0.4
    SELL_MAX = 0.6
    BANKRUPTCY_CASH = 600.0

    def __init__(self) -> None:
        cash = np.random.uniform(self.MIN_START_CASH, self.MAX_START_CASH)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
        self.__decision_time = np.random.choice([np.random.randint(30, 60), 
                                                 np.random.randint(120, 180),
                                                 np.random.randint(240, 360)],
                                                 p=[0.5, 0.3, 0.2])
        self.__judge_coef = np.random.uniform(1.0, 1.5)
        self.__risk_coef = np.random.uniform(1.05, 1.15)
        self.set_cooldown(np.random.randint(self.__decision_time * 3, self.__decision_time * 4))

    def get_MA_t(self, price_1080ticks: list, t: int) -> float:
        length = len(price_1080ticks)
        if length < t:
            return 0
        else:
            price_t_ticks = price_1080ticks[-t:]
            return sum(price_t_ticks) / t
        
    def get_sigma_t(self, price_1080ticks: list, t: int) -> float:
        length = len(price_1080ticks)
        if length < t:
            return 0
        else:
            price_t_ticks = price_1080ticks[-t:]
            return np.std(price_t_ticks)

    def tick_decision(self, current_price: float, price_1080ticks: list, depth: float) -> int:
        if self.get_cash() < self.BANKRUPTCY_CASH:
            amount = max(1, np.floor((self.BANKRUPTCY_CASH - self.get_cash()) / current_price * 1.5))
            self.trade(-amount)
        elif self.is_cooldown() is False:
            self.set_cooldown(np.random.randint(self.__decision_time, self.__decision_time * 2))
            MA_t = self.get_MA_t(price_1080ticks, self.__decision_time)
            sigma_market = self.get_sigma_t(price_1080ticks, self.__decision_time * 3 - 1)
            sigma_t = self.get_sigma_t(price_1080ticks, self.__decision_time)
            if MA_t == 0:
                return 0
            signal = (current_price - MA_t) / sigma_t
            judge = self.__judge_coef * sigma_market
            if current_price > MA_t * self.__risk_coef:
                self.trade(-self.get_positions())
            elif signal > judge:
                amount = np.floor(self.get_cash() / current_price * np.random.uniform(self.BUY_MIN, self.BUY_MAX))
                self.trade(amount)
            elif signal < -judge:
                amount = np.floor(np.random.uniform(self.SELL_MIN, self.SELL_MAX) * self.get_positions())
                self.trade(-amount)
        amount = self.finish_position_change(current_price, depth)
        # if amount != 0:
        #     print("trend: " + str(amount))
        return amount

class ValueTrader(Trader): #400

    MIN_START_CASH = 20000.0
    MAX_START_CASH = 40000.0
    MIN_START_POSITION = 200
    MAX_START_POSITION = 600
    DECISION_DEVIATION_SCALE = 0.015
    BUY_MIN = 0.1
    BUY_MAX = 0.3
    SELL_MIN = 0.4
    SELL_MAX = 0.6
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
        # if amount != 0:
        #     print("value: " + str(amount))
        return amount
