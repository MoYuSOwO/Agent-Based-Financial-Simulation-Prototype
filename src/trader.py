from abc import ABC, abstractmethod
import numpy as np

class Trader(ABC):
    FORCED_LIQUIDATION_COEF = 0.25
    def __init__(self, positions: float, cooldown: int):
        self.__positions = positions
        self.__short_selling_price = 0
        self.__cooldown = cooldown

    @abstractmethod
    def tick_decision(self) -> int:
        pass
    
    def get_positions(self) -> int:
        return self.__positions

    def check_forced_liquidation(self, current_price: float) -> bool:
        if self.__short_selling_price == 0:
            return False
        if (current_price - self.__short_selling_price) / self.__short_selling_price >= self.FORCED_LIQUIDATION_COEF:
            return True
        return False
    
    def is_cooldown(self) -> bool:
        if self.__cooldown > 0:
            self.__cooldown -= 1
            return True
        return False
    
    def set_cooldown(self, cooldown: int) -> None:
        self.__cooldown = cooldown

    def buy(self, positions: int) -> int:
        if self.__positions < 0:
            change = max(-self.__positions, positions)
            self.__positions += change
            self.__short_selling_price = 0
            return change
        else:
            self.__positions += positions
            return positions
        
    def sell(self, positions: int, current_price: float) -> int:
        if self.__positions > 0 and self.__positions - positions >= 0:
            self.__positions -= positions
        elif self.__positions > 0 and self.__positions - positions < 0:
            self.__positions -= positions
            self.__short_selling_price = current_price
        elif self.__positions <= -500:
            return 0
        else: # self.__positions <= 0
            self.__short_selling_price = (self.__short_selling_price * (-self.__positions) + current_price * positions) / (positions + (-self.__positions))
            self.__positions -= positions
        return -positions
        


class RandomTrader(Trader): #1000
    # min=a, max=b means a <= x < b
    # min=a, max=b+1 means a <= x <= b
    RANDOM_TRADE_MIN = 1
    RANDOM_TRADE_MAX = 8
    MIN_OPERATION_COOLDOWN = 5
    MAX_OPERATION_COOLDOWN = 10
    START_POSITION = 60

    def __init__(self) -> None:
        start_cooldown = np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN)
        super().__init__(self.START_POSITION, start_cooldown)
    
    def tick_decision(self, current_price: float) -> int:
        if self.check_forced_liquidation(current_price):
            return self.buy(-self.get_positions())
        if self.is_cooldown() is False:
            if np.random.rand() < 0.5:
                amount = self.buy(np.random.randint(self.RANDOM_TRADE_MIN, self.RANDOM_TRADE_MAX))
            else:
                amount = self.sell(np.random.randint(self.RANDOM_TRADE_MIN, self.RANDOM_TRADE_MAX), current_price)
            self.set_cooldown(np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN))
            return amount
        return 0

class TrendTrader(Trader): #600

    START_POSITION = 1000
    MIN_OPERATION_COOLDOWN = 60
    MAX_OPERATION_COOLDOWN = 120
    TRADE_MIN = 10
    TRADE_MAX = 20

    def __init__(self) -> None:
        start_cooldown = np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN)
        super().__init__(self.START_POSITION, start_cooldown)
        self.__last_cooldown = start_cooldown

    def tick_decision(self, current_price: float, tick_price_history_120: list) -> int:
        if self.check_forced_liquidation(current_price):
            return self.buy(-self.get_positions())
        if self.is_cooldown() is False:
            lenn = min(int(self.__last_cooldown * 1.5 + 1), len(tick_price_history_120))
            average = sum(tick_price_history_120[-lenn:]) / lenn
            if current_price > average:
                amount = self.buy(np.random.randint(self.TRADE_MIN, self.TRADE_MAX))
            else:
                amount = self.sell(np.random.randint(self.TRADE_MIN, self.TRADE_MAX), current_price)
            self.__last_cooldown = np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN)
            self.set_cooldown(self.__last_cooldown)
            return amount
        return 0
        
class ValueTrader(Trader): #400

    START_POSITION = 1000
    MIN_OPERATION_COOLDOWN = 550
    MAX_OPERATION_COOLDOWN = 650
    MIN_DECISION_BIAS = 0.85
    MAX_DECISION_BIAS = 1.15
    TRADE_MIN = 500
    TRADE_MAX = 1000

    def __init__(self) -> None:
        start_cooldown = np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN)
        super().__init__(self.START_POSITION, start_cooldown)
        self.__decision_bias = np.random.uniform(self.MIN_DECISION_BIAS, self.MAX_DECISION_BIAS)

    def tick_decision(self, current_price, basic_value) -> int:
        if self.check_forced_liquidation(current_price):
            return self.buy(-self.get_positions())
        if self.is_cooldown() is False:
            basic_value *= self.__decision_bias
            if current_price < basic_value:
                amount = self.buy(np.random.randint(self.TRADE_MIN, self.TRADE_MAX))
            else:
                amount = self.sell(np.random.randint(self.TRADE_MIN, self.TRADE_MAX), current_price)
            self.set_cooldown(np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN))
            return amount
        return 0
        
class HighFreqTrader(Trader):
    START_POSITION = 1000
    MIN_OPERATION_COOLDOWN = 1
    MAX_OPERATION_COOLDOWN = 10
    TRADE_MIN = 8
    TRADE_MAX = 15

    def __init__(self, current_price: float) -> None:
        start_cooldown = np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN)
        super().__init__(self.START_POSITION, start_cooldown)
        self.__last_price = current_price

    def tick_decision(self, current_price: float) -> int:
        if self.check_forced_liquidation(current_price):
            return self.buy(-self.get_positions())
        if self.is_cooldown() is False:
            if current_price > self.__last_price:
                amount = self.buy(np.random.randint(self.TRADE_MIN, self.TRADE_MAX))
            elif current_price < self.__last_price:
                amount = self.sell(np.random.randint(self.TRADE_MIN, self.TRADE_MAX), current_price)
            else:
                amount = 0
            self.set_cooldown(np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN))
            return amount
        return 0
        
class ReverseTrader(Trader):
    START_POSITION = 0
    MIN_OPERATION_COOLDOWN = 8
    MAX_OPERATION_COOLDOWN = 14
    BASE_JUDGE_LINE = 0.02
    MIN_DECISION_BIAS = 0.85
    MAX_DECISION_BIAS = 1.15
    TRADE_MIN = 100
    TRADE_MAX = 300

    def __init__(self) -> None:
        start_cooldown = np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN)
        super().__init__(self.START_POSITION, start_cooldown)

    def tick_decision(self, current_price: float, price_15tick_before: float) -> int:
        if self.check_forced_liquidation(current_price):
            return self.buy(-self.get_positions())
        if self.is_cooldown() is False:
            judge_line = self.BASE_JUDGE_LINE * np.random.uniform(self.MIN_DECISION_BIAS, self.MAX_DECISION_BIAS)
            if (current_price - price_15tick_before) / price_15tick_before > judge_line:
                amount = self.buy(np.random.randint(self.TRADE_MIN, self.TRADE_MAX))
            elif (current_price - price_15tick_before) / price_15tick_before < -judge_line:
                amount = self.sell(np.random.randint(self.TRADE_MIN, self.TRADE_MAX), current_price)
            else:
                amount = 0
            self.set_cooldown(np.random.randint(self.MIN_OPERATION_COOLDOWN, self.MAX_OPERATION_COOLDOWN))
            return amount
        return 0
