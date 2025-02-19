from abc import ABC, abstractmethod
import numpy as np

MIN_DAILY_SALARY = 200
MAX_DAILY_SALARY = 400

class Trader(ABC):
    def __init__(self, cash: float, positions: float):
        self.__cash = cash
        self.__positions = positions

    @abstractmethod
    def tick_decision(self) -> int:
        pass

    def tick_salary(self) -> None:
        self.__cash += np.random.uniform(MIN_DAILY_SALARY, MAX_DAILY_SALARY) / 3600.0

    def add_position(self, position: int, current_price: float) -> None:
        self.__positions += position
        self.__cash -= position * current_price

    def get_cash(self) -> int:
        return self.__cash
    
    def get_positions(self) -> int:
        return self.__positions

class RandomTrader(Trader): #1000

    RANDOM_BUY_MIN = 0.3
    RANDOM_BUY_MAX = 0.5
    OPERATION_RATE_PER_TICK = 0.15
    START_CASH = 20000.0
    START_CASH_SCALE = 3000
    MIN_START_POSITION = 150
    MAX_START_POSITION = 210
    MIN_INCREASE_POSITION_FROM_CASH = 0.10
    MAX_INCREASE_POSITION_FROM_CASH = 0.25
    MIN_DECREASE_POSITION = 0.30
    MAX_DECREASE_POSITION = 1.00
    LOWEST_CASH_ACCEPTABLE = 1500.0

    def __init__(self) -> None:
        cash = self.START_CASH + np.random.normal(0, self.START_CASH_SCALE)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
    
    def tick_decision(self, current_price) -> int:
        if self.get_cash() < self.LOWEST_CASH_ACCEPTABLE:
            return 0
        if np.random.rand() < self.OPERATION_RATE_PER_TICK:
            if np.random.rand() < 0.5:
                return int(self.get_cash() / current_price * np.random.uniform(self.RANDOM_BUY_MIN, self.RANDOM_BUY_MAX))
            else:
                return int(-self.get_positions())
        return 0

class TrendTrader(Trader): #600

    START_CASH = 30000.0
    START_CASH_SCALE = 3500
    MIN_START_POSITION = 200
    MAX_START_POSITION = 400
    INCREASE_WHEN_BUY = 0.035
    DECREASE_WHEN_SELL = -0.025
    MIN_BUY_ONCE = 0.3
    MAX_BUY_ONCE = 0.6
    def __init__(self) -> None:
        cash = self.START_CASH + np.random.normal(0, self.START_CASH_SCALE)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
        self.__increase_when_buy = self.INCREASE_WHEN_BUY * np.random.uniform(0.5, 1.5)
        self.__increase_when_sell = self.DECREASE_WHEN_SELL * np.random.uniform(0.5, 1.5)

    def tick_decision(self, current_price, trend_50ticks) -> int:
        if trend_50ticks >= self.__increase_when_buy:
            return int(self.get_cash() / current_price * np.random.uniform(self.MIN_BUY_ONCE, self.MAX_BUY_ONCE))
        elif trend_50ticks <= self.__increase_when_sell:
            return int(-self.get_positions())
        return 0

class ValueTrader(Trader): #400

    START_CASH = 20000.0
    START_CASH_SCALE = 3000
    MIN_START_POSITION = 120
    MAX_START_POSITION = 280
    DECISION_DEVIATION_SCALE = 0.035
    MIN_BUY_ONCE = 0.3
    MAX_BUY_ONCE = 0.5
    MIN_SELL_ONCE = 0.5
    MAX_SELL_ONCE = 0.7

    def __init__(self) -> None:
        cash = self.START_CASH + np.random.normal(0, self.START_CASH_SCALE)
        positions = np.random.randint(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)

    def tick_decision(self, current_price, basic_value) -> int:
        basic_value *= 1 + np.random.normal(0, self.DECISION_DEVIATION_SCALE)
        if current_price < basic_value:
            return int(int(self.get_cash() / current_price) * np.random.uniform(self.MIN_BUY_ONCE, self.MAX_BUY_ONCE))
        else:
            return int(-self.get_positions()  * np.random.uniform(self.MIN_SELL_ONCE, self.MAX_SELL_ONCE))
