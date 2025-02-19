import numpy as np

PRICE_SENSITIVITY = 0.002
DAY_LIMIT = 0.10

class Node:
    def __init__(self) -> None:
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
        self.__current_price = 100.0 + np.random.normal(0, 10)
        self.__day_price_history = {
            'high': [self.__current_price + np.random.uniform(1.5, 2.0)],
            'low': [self.__current_price - np.random.uniform(1.5, 2.0)],
            'open': [self.__current_price + np.random.uniform(-1.2, 1.2)],
            'close': [self.__current_price],
        }
        self.__basic_value = self.__current_price + np.random.normal(0, 2)
        self.__tick_price_history = []

    def __get_day(self) -> int:
        return len(self.__day_price_history['high'])

    def get_tick_price_history(self) -> list:
        return self.__tick_price_history.copy()
    
    def get_day_price_history(self) -> list:
        return self.__day_price_history.copy()

    def get_average_5days(self) -> float:
        if self.__get_day() < 5:
            return self.__current_price
        else:
            average_5days = 0.0
            for i in range(1, 6):
                average_5days += self.__day_price_history['close'][-i]
            average_5days /= 5.0
            return average_5days

    def get_average_20days(self) -> float:
        if self.__get_day() < 20:
            return self.__current_price
        else:
            average_20days = 0.0
            for i in range(1, 21):
                average_20days += self.__day_price_history['close'][-i]
            average_20days /= 20.0
            return average_20days
        
    def get_average_50ticks(self) -> float:
        if len(self.__tick_price_history) >= 50:
            return (self.__current_price - self.__tick_price_history[-50]) / self.__tick_price_history[-50]
        else:
            return (self.__current_price - self.__day_price_history['close'][-1]) / self.__day_price_history['close'][-1]

    def buy(self, position_change) -> None:
        self.__buy_per_tick += position_change

    def sell(self, position_change) -> None:
        self.__sell_per_tick += position_change

    def get_current_price(self) -> float:
        return self.__current_price
    
    def get_basic_value(self) -> float:
        return self.__basic_value

    def tick_update(self) -> None:
        self.__tick_price_history.append(self.__current_price)
        imbalance = (self.__buy_per_tick - self.__sell_per_tick) / (self.__buy_per_tick + self.__sell_per_tick + 1e-6)
        adjusted_imbalance = np.sign(imbalance) * np.sqrt(abs(imbalance))
        self.__current_price *= 1 + adjusted_imbalance * PRICE_SENSITIVITY
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
    
    def day_update(self) -> None:
        self.__day_price_history['high'].append(max(self.__tick_price_history))
        self.__day_price_history['low'].append(min(self.__tick_price_history))
        self.__day_price_history['open'].append(self.__tick_price_history[0])
        self.__day_price_history['close'].append(self.__tick_price_history[-1])
        self.__current_price *= 1 + np.random.normal(0, 0.01)
        self.__basic_value *= 1 + np.random.uniform(-0.02, 0.01)
        self.__tick_price_history = [self.__current_price]

class Market:
    def __init__(self):
        pass
