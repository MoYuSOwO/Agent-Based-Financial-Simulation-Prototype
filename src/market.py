import numpy as np

PRICE_SENSITIVITY = 0.01
DAY_LIMIT = 0.07
START_MARKET_DEPTH = 1000

class Node:
    def __init__(self) -> None:
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
        self.__current_price = 27.0
        self.__day_price_history = {
            'high': [self.__current_price + np.random.uniform(1.5, 2.0)],
            'low': [self.__current_price - np.random.uniform(1.5, 2.0)],
            'open': [self.__current_price + np.random.uniform(-1.2, 1.2)],
            'close': [self.__current_price],
        }
        self.__basic_value = 45.0
        self.__depth = START_MARKET_DEPTH
        self.__tick_price_history = []

    def __get_day(self) -> int:
        return len(self.__day_price_history['high'])
    
    def __night_trade(self) -> None:
        delta_value = np.random.uniform(-0.02, 0.02)
        self.__basic_value *= (1 + delta_value)
        self.__depth *= 0.6
        gap = np.random.normal(0, 0.02) + np.random.laplace(0, 0.005)
        self.__current_price *= (1 + gap)

    def get_tick_price_history(self) -> list:
        return self.__tick_price_history.copy()
    
    def get_day_price_history(self) -> list:
        return self.__day_price_history.copy()
        
    def get_1080ticks_history(self) -> float:
        if len(self.__tick_price_history) < 600:
            return self.__tick_price_history.copy()
        else:
            return self.__tick_price_history[-1080:]

    def clinch(self, position_change: int) -> None:
        if position_change > 0:
            self.__buy_per_tick += int(position_change)
        else:
            self.__sell_per_tick += int(-position_change)

    def get_current_price(self) -> float:
        return self.__current_price
    
    def get_basic_value(self) -> float:
        return self.__basic_value
    
    def get_market_depth(self) -> int:
        return self.__depth
    
    def __update_depth(self) -> None:
        self.__depth = 0.8 * self.__depth + 0.2 * (START_MARKET_DEPTH + 0.2 * (self.__buy_per_tick + self.__sell_per_tick))

    def __update_price(self) -> None:
        net_flow = self.__buy_per_tick - self.__sell_per_tick
        adjust_net = ((np.sign(net_flow) * np.sqrt(abs(net_flow))) / (1 + 0.1 * abs(net_flow)))
        lambda_t = 1.0 / np.sqrt(self.__depth)
        delta = lambda_t * adjust_net * PRICE_SENSITIVITY
        if delta > 0.001:
            print(str(self.__buy_per_tick) + " " + str(self.__sell_per_tick) + " " + str(self.__depth))
        self.__current_price *= 1 + delta
        self.__current_price += np.random.normal(0, 0.0001)
        self.__current_price = round(float(self.__current_price), 4)
        if (self.__current_price - self.__tick_price_history[0]) / self.__tick_price_history[0] >= DAY_LIMIT:
            self.__current_price = self.__tick_price_history[0] * (1 + DAY_LIMIT)

    def tick_update(self, tick=0) -> None:
        self.__tick_price_history.append(self.__current_price)
        self.__update_depth()
        self.__update_price()
        # print("tick " + str(tick) + ": " + "buy:" + str(self.__buy_per_tick) + " sell:" + str(self.__sell_per_tick) + " depth:" + str(self.__depth))
        self.__buy_per_tick = 0
        self.__sell_per_tick = 0
    
    def day_update(self) -> None:
        self.__day_price_history['high'].append(max(self.__tick_price_history))
        self.__day_price_history['low'].append(min(self.__tick_price_history))
        self.__day_price_history['open'].append(self.__tick_price_history[0])
        self.__day_price_history['close'].append(self.__tick_price_history[-1])
        self.__night_trade()
        self.__tick_price_history = [self.__current_price]

class Market:
    def __init__(self):
        pass
