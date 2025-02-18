import numpy as np

PRICE_SENSITIVITY = 0.002
DAY_LIMIT = 0.10

class Node:
    def __init__(self) -> None:
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
        self.__current_price = 100.0 + np.random.normal(0, 10)
        self.__day_price_history = {
            'highest': [],
            'lowest': [],
            'start': [],
            'end': [],
        }
        self.__tick_price_history = []
        self.__timeout_tick = 0

    def buy(self) -> None:
        self.__buy_per_tick += 1

    def sell(self) -> None:
        self.__sell_per_tick += 1

    def get_current_price(self) -> float:
        return self.__current_price
    
    def is_timeout(self) -> bool:
        return self.__timeout_tick > 0
    
    def __check_timeout(self) -> None:
        if (self.__current_price - self.__tick_price_history[0]) / self.__tick_price_history[0] <= -DAY_LIMIT:
            self.__timeout_tick = 900

    def tick_update(self) -> None:
        if self.is_timeout():
            self.__timeout_tick -= 1
            return
        self.__tick_price_history.append(self.__current_price)
        self.__current_price *= 1 + (self.__buy_per_tick / (self.__buy_per_tick + self.__sell_per_tick) - 0.5) * 2 * PRICE_SENSITIVITY
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
        self.__check_timeout()
    
    def day_update(self) -> None:
        self.__day_price_history['highest'].append(max(self.__tick_price_history))
        self.__day_price_history['lowest'].append(min(self.__tick_price_history))
        self.__day_price_history['start'].append(self.__tick_price_history[0])
        self.__day_price_history['end'].append(self.__tick_price_history[-1])
        self.__tick_price_history = []
        self.__timeout_tick = 0


class Market:
    def __init__(self):
        pass
