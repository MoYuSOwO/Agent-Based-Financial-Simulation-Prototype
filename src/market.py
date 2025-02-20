import numpy as np

PRICE_SENSITIVITY = 0.002
DAY_LIMIT = 0.10
GAP_AFTER_CLOSE_COEF = 0.3

class Node:
    def __init__(self, total_volume: int) -> None:
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
        self.__current_price = 95.0
        self.__day_price_history = {
            'high': [self.__current_price + np.random.uniform(1.5, 2.0)],
            'low': [self.__current_price - np.random.uniform(1.5, 2.0)],
            'open': [self.__current_price + np.random.uniform(-1.2, 1.2)],
            'close': [self.__current_price],
        }
        self.__basic_value = 100.0
        self.__total_volume = total_volume
        self.__tick_price_history = []

    def __get_day(self) -> int:
        return len(self.__day_price_history['high'])

    def get_tick_price_history(self) -> list:
        return self.__tick_price_history.copy()
    
    def get_day_price_history(self) -> list:
        return self.__day_price_history.copy()
        
    def get_15tick_before(self) -> float:
        if len(self.__tick_price_history) >= 15:
            return self.__tick_price_history[-15]
        else:
            return self.__day_price_history['close'][-1]

    def __buy(self, position_change) -> None:
        self.__buy_per_tick += position_change

    def __sell(self, position_change) -> None:
        self.__sell_per_tick += position_change

    def trade(self, position_change) -> None:
        if position_change > 0:
            self.__buy(position_change)
        else:
            self.__sell(-position_change)

    def get_current_price(self) -> float:
        return self.__current_price
    
    def get_basic_value(self) -> float:
        return self.__basic_value

    def tick_update(self) -> None:
        self.__tick_price_history.append(self.__current_price)
        delta = (self.__buy_per_tick - self.__sell_per_tick) * PRICE_SENSITIVITY / self.__total_volume
        delta *= (self.__buy_per_tick - self.__sell_per_tick) / (self.__buy_per_tick + self.__sell_per_tick + 1e-6)
        self.__current_price *= 1 + delta
        # if abs((self.__current_price - self.__tick_price_history[0]) / self.__tick_price_history[0]) > DAY_LIMIT:
        #     self.__current_price = self.__tick_price_history[0] * (1 + DAY_LIMIT)
        print(str(self.__buy_per_tick) + ' ' + str(self.__sell_per_tick))
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
    
    def day_update(self) -> None:
        self.__day_price_history['high'].append(max(self.__tick_price_history))
        self.__day_price_history['low'].append(min(self.__tick_price_history))
        self.__day_price_history['open'].append(self.__tick_price_history[0])
        close_price = sum(self.__tick_price_history[-301:]) / 300.0
        self.__day_price_history['close'].append(close_price)
        day_vol = (self.__day_price_history['high'][-1] - self.__day_price_history['low'][-1]) / self.__tick_price_history[0]
        day_vol *= GAP_AFTER_CLOSE_COEF
        gap = np.random.uniform(-day_vol, day_vol)
        self.__current_price = close_price * (1 + gap)
        self.__tick_price_history = [self.__current_price]

class Market:
    def __init__(self):
        pass
