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

    def day_salary(self) -> None:
        self.__cash += np.random.uniform(MIN_DAILY_SALARY, MAX_DAILY_SALARY)

    def add_position(self, position: int, current_price: float) -> None:
        self.__positions += position
        self.__cash -= position * current_price

    def get_cash(self) -> int:
        return self.__cash
    
    def get_positions(self) -> int:
        return self.__positions

class RandomTrader(Trader): #1000

    RANDOM_TRADE_MIN = 0.06
    RANDOM_TRADE_MAX = 0.18
    OPERATION_RATE_PER_TICK = 0.10
    START_CASH = 20000.0
    START_CASH_SCALE = 3000
    MIN_START_POSITION = 80
    MAX_START_POSITION = 210
    MIN_INCREASE_POSITION_FROM_CASH = 0.10
    MAX_INCREASE_POSITION_FROM_CASH = 0.25
    MIN_DECREASE_POSITION = 0.30
    MAX_DECREASE_POSITION = 1.00
    LOWEST_CASH_ACCEPTABLE = 1500.0

    def __init__(self) -> None:
        cash = self.START_CASH + np.random.normal(0, self.START_CASH_SCALE)
        positions = np.random.uniform(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
    
    def tick_decision(self, current_price) -> int:
        if self.get_cash() < self.LOWEST_CASH_ACCEPTABLE:
            return 0
        if np.random() < self.OPERATION_RATE_PER_TICK:
            if np.random() < 0.5:
                return self.get_cash() // current_price // (1.0 / np.random.uniform(self.RANDOM_TRADE_MIN, self.RANDOM_TRADE_MAX))
            else:
                return -self.get_positions() // (1.0 / np.random.uniform(self.RANDOM_TRADE_MIN, self.RANDOM_TRADE_MAX))
        return 0

class TrendTrader(Trader): #600

    START_CASH = 25000.0
    START_CASH_SCALE = 3500
    MIN_START_POSITION = 200
    MAX_START_POSITION = 500
    INCREASE_WHEN_BUY = 0.03
    DECREASE_WHEN_SELL = -0.03

    def __init__(self, price) -> None:
        cash = self.START_CASH + np.random.normal(0, self.START_CASH_SCALE)
        positions = np.random.uniform(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)
        self.__price_when_buy = price
        self.__increase_when_buy = self.INCREASE_WHEN_BUY * np.random.uniform(0.5, 1.5)
        self.__increase_when_sell = self.DECREASE_WHEN_SELL * np.random.uniform(0.5, 1.5)

    def tick_decision(self, current_price) -> int:
        if (current_price - self.__price_when_buy) / self.__price_when_buy >= self.__increase_when_buy:
            self.__price_when_buy = current_price
            return self.get_cash() // current_price
        elif (current_price - self.__price_when_buy) / self.__price_when_buy <= self.__increase_when_sell:
            self.__price_when_buy = current_price
            return -self.get_positions()
        

class ValueTrader(Trader): #400

    START_CASH = 20000.0
    START_CASH_SCALE = 30000
    MIN_START_POSITION = 200
    MAX_START_POSITION = 500
    DECISION_DEVIATION_SCALE = 0.035

    def __init__(self) -> None:
        cash = self.START_CASH + np.random.normal(0, self.START_CASH_SCALE)
        positions = np.random.uniform(self.MIN_START_POSITION, self.MAX_START_POSITION)
        super().__init__(cash, positions)

    def tick_decision(self, current_price, average_20days, average_5days) -> int:
        average_20days *= 1 + np.random.normal(0, self.DECISION_DEVIATION_SCALE)
        average_5days *= 1 + np.random.normal(0, self.DECISION_DEVIATION_SCALE)
        if current_price < average_20days and current_price < average_5days:
            return self.get_cash() // current_price
        elif current_price > average_20days and current_price > average_5days:
            return -self.get_positions()
        elif average_20days < current_price < average_5days:
            return -self.get_positions()
        else:
            return self.get_cash() // current_price
