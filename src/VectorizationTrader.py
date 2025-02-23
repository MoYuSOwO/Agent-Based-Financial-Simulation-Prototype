import numpy as np

def finish_position_change(traders, current_price: float) -> tuple[np.int32, np.int32]:
    current_price = np.float64(current_price)
    buy_traders = traders['order_positions'] > 0
    sell_traders = traders['order_positions'] < 0
    not_enough_cash = (traders['order_positions'] > 0) & (traders['cash'] < traders['order_positions'] * current_price)
    if np.any(not_enough_cash):
        traders['order_positions'][not_enough_cash] = np.floor(traders['cash'][not_enough_cash] / current_price).astype(np.int32)
        traders['positions'][not_enough_cash] += traders['order_positions'][not_enough_cash]
        traders['cash'][not_enough_cash] -= traders['order_positions'][not_enough_cash] * current_price
    not_enough_position = (traders['order_positions'] < 0) & ((traders['positions'] + traders['order_positions']) < 0)
    if np.any(not_enough_position):
        traders['order_positions'][not_enough_position] = -traders['positions'][not_enough_position]
        traders['cash'][not_enough_position] -= traders['order_positions'][not_enough_position] * current_price
        traders['positions'][not_enough_position] = 0
    others = ~(not_enough_position | not_enough_cash)
    if np.any(others):
        traders['positions'][others] += traders['order_positions'][others]
        traders['cash'][others] -= traders['order_positions'][others] * current_price
    buy_amount = np.sum(traders['order_positions'][buy_traders])
    sell_amount = np.sum(traders['order_positions'][sell_traders])
    traders['order_positions'] = 0
    return buy_amount, sell_amount

class NoiseTrader():
    def __init__(self, n: int, 
                 min_start_cash = 10000.0, max_start_cash = 30000.0,
                 min_start_positions = 100, max_start_positions = 300,
                 average_trade_amount = 15, average_wait_time = 1.0, backruptcy_cash = 1000.0):
        n = np.int32(n)
        random_trader = np.dtype([
            ('cash', 'float64'),
            ('positions', 'int32'),
            ('order_positions', 'int32'),
            ('cooldown', 'int32'),
        ])
        self.__average_trade_amount = np.int32(average_trade_amount)
        self.__average_wait_time = np.float64(average_wait_time)
        self.__bankruptcy_cash = np.float64(backruptcy_cash)
        self.__traders = np.zeros(n, dtype=random_trader)
        self.__traders['cash'] = np.random.uniform(min_start_cash, max_start_cash, n)
        self.__traders['positions'] = np.random.randint(min_start_positions, max_start_positions, n).astype(np.int32)
        self.__traders['order_positions'] = 0
        self.__traders['cooldown'] = np.random.exponential(self.__average_wait_time, n).astype(np.int32)

    def tick_decision(self, current_price: float) -> tuple[np.int32, np.int32]:
        # deal with bankrupters
        bankrupters = (self.__traders['cash'] <= self.__bankruptcy_cash) & (self.__traders['cooldown'] == 0)
        amount = np.maximum(np.floor((self.__bankruptcy_cash - self.__traders['cash'][bankrupters]) / current_price * 2.0).astype(np.int32), 
                            np.floor(np.random.exponential(self.__average_trade_amount, np.sum(bankrupters))).astype(np.int32))
        amount = np.maximum(1, amount)
        self.__traders['order_positions'][bankrupters] = -amount
        # trade
        decision_random = np.random.rand(np.size(self.__traders))
        trade_random = np.random.exponential(self.__average_trade_amount, np.size(self.__traders)).astype(np.int32)
        buy_traders = (self.__traders['cooldown'] == 0) & (self.__traders['cash'] > self.__bankruptcy_cash) & (decision_random < 0.4)
        sell_traders = (self.__traders['cooldown'] == 0) & (self.__traders['cash'] > self.__bankruptcy_cash) & (decision_random >= 0.4) & (decision_random < 0.8)
        self.__traders['order_positions'][buy_traders] = trade_random[buy_traders]
        self.__traders['order_positions'][sell_traders] = -trade_random[sell_traders]
        # deal with cooldown
        active_traders = (self.__traders['cooldown'] == 0)
        self.__traders['cooldown'][active_traders] = np.random.exponential(self.__average_wait_time, np.sum(active_traders)).astype(np.int32)
        inactive_traders = ~(active_traders)
        self.__traders['cooldown'][inactive_traders] -= 1
        return finish_position_change(self.__traders, current_price)
    
class MomentumTrader():
    def __init__(self, n: int, 
                 min_start_cash = 10000.0, max_start_cash = 30000.0,
                 min_start_positions = 100, max_start_positions = 300,
                 min_buy_proportion = 0.1, max_buy_proportion = 0.2,
                 min_sell_proportion = 0.2, max_sell_proportion = 0.3,
                 backruptcy_cash = 1000.0):
        n = np.int32(n)
        momentum_trader = np.dtype([
            ('cash', 'float64'),
            ('positions', 'int32'),
            ('order_positions', 'int32'),
            ('cooldown', 'int32'),
            ('decision_time', 'int32'),
            ('judge_coef', 'float64'),
            ('risk_coef', 'float64'),
        ])
        self.__min_buy_proportion = np.float64(min_buy_proportion)
        self.__max_buy_proportion = np.float64(max_buy_proportion)
        self.__min_sell_proportion = np.float64(min_sell_proportion)
        self.__max_sell_proportion = np.float64(max_sell_proportion)
        self.__bankruptcy_cash = np.float64(backruptcy_cash)
        self.__traders = np.zeros(n, dtype=momentum_trader)
        self.__traders['cash'] = np.random.uniform(min_start_cash, max_start_cash, n)
        self.__traders['positions'] = np.random.randint(min_start_positions, max_start_positions, n)
        self.__traders['order_positions'] = 0
        rand = np.random.rand(n)
        self.__traders['decision_time'] = np.where(
                rand < 0.5,
                np.random.randint(30, 60, n),
                np.where(
                    rand < 0.8,
                    np.random.randint(120, 180, n),
                    np.random.randint(240, 360, n)
                )
            )
        self.__traders['judge_coef'] = np.random.uniform(1.0, 1.5, n)
        self.__traders['risk_coef'] = np.random.uniform(1.05, 1.15, n)
        active_times = self.__traders['decision_time'] 
        self.__traders['cooldown'] = np.random.randint(active_times * 3, active_times * 4, n)
        self.__price_before_1080ticks = np.zeros(1080, dtype=np.float64)
        self.__price_prefix_sum = np.zeros(1080, dtype=np.float64)
        self.__price_square_prefix_sum = np.zeros(1080, dtype=np.float64)
        self.__len = 0

    def __append(self, current_price: np.float64):
        if self.__len == 0:
            self.__price_before_1080ticks[self.__len] = current_price
            self.__price_prefix_sum[self.__len] = current_price
            self.__price_square_prefix_sum[self.__len] = (current_price) ** 2
            self.__len += 1
        elif self.__len < 1080:
            self.__price_before_1080ticks[self.__len] = current_price
            self.__price_prefix_sum[self.__len] =  self.__price_prefix_sum[self.__len - 1] + current_price
            self.__price_square_prefix_sum[self.__len] = self.__price_square_prefix_sum[self.__len - 1] + (current_price) ** 2
            self.__len += 1
        else:
            self.__price_before_1080ticks[:-1] = self.__price_before_1080ticks[1:]
            self.__price_before_1080ticks[-1] = current_price
            del_element = self.__price_prefix_sum[0]
            self.__price_prefix_sum[:-1] = self.__price_prefix_sum[1:]
            self.__price_prefix_sum[-1] = self.__price_prefix_sum[-2] + current_price
            self.__price_prefix_sum -= del_element
            del_element = self.__price_square_prefix_sum[0]
            self.__price_square_prefix_sum[:-1] = self.__price_square_prefix_sum[1:]
            self.__price_square_prefix_sum[-1] = self.__price_square_prefix_sum[-2] + (current_price) ** 2
            self.__price_prefix_sum -= del_element
    
    def tick_decision(self, current_price: float)-> tuple[np.int32, np.int32]:
        self.__append(current_price)
        # deal with bankrupters
        bankrupters = (self.__traders['cash'] <= self.__bankruptcy_cash) & (self.__traders['cooldown'] == 0)
        amount = np.maximum(np.floor((self.__bankruptcy_cash - self.__traders['cash'][bankrupters]) / current_price * 2.0).astype(np.int32), 1)
        self.__traders['order_positions'][bankrupters] = -amount
        # trade
            # initialization
        MA_t = np.zeros(np.size(self.__traders), dtype=np.float64)
        avg_3t = np.zeros(np.size(self.__traders), dtype=np.float64)
        total_avgsquare_3t = np.zeros(np.size(self.__traders), dtype=np.float64)
        avg_t = np.zeros(np.size(self.__traders), dtype=np.float64)
        total_avgsquare_t = np.zeros(np.size(self.__traders), dtype=np.float64)
        sigma_market = np.zeros(np.size(self.__traders), dtype=np.float64)
        sigma_t = np.zeros(np.size(self.__traders), dtype=np.float64)
        signal = np.zeros(np.size(self.__traders), dtype=np.float64)
        judge = np.zeros(np.size(self.__traders), dtype=np.float64)
            # calculate MA_t, sigma_market, sigma_t
        active_traders = (self.__traders['cooldown'] == 0) & (self.__traders['cash'] > self.__bankruptcy_cash) & (self.__len >= self.__traders['decision_time'] * 3)
        MA_t[active_traders] = (self.__price_prefix_sum[-1] - self.__price_prefix_sum[-1 - self.__traders['decision_time'][active_traders]]) / self.__traders['decision_time'][active_traders]
        avg_3t[active_traders] = (self.__price_prefix_sum[-1] - self.__price_prefix_sum[-1 - self.__traders['decision_time'][active_traders] * 3]) / (self.__traders['decision_time'][active_traders] * 3)
        total_avgsquare_3t[active_traders] = (self.__traders['decision_time'][active_traders] * 3) * (avg_3t[active_traders] ** 2)
        avg_t[active_traders] = (self.__price_prefix_sum[-1] - self.__price_prefix_sum[-1 - self.__traders['decision_time'][active_traders]]) / self.__traders['decision_time'][active_traders]
        total_avgsquare_t[active_traders] = (self.__traders['decision_time'][active_traders]) * (avg_t[active_traders] ** 2)
        sigma_market[active_traders] = (self.__price_square_prefix_sum[-1] - self.__price_square_prefix_sum[-1 - self.__traders['decision_time'][active_traders] * 3]) - total_avgsquare_3t[active_traders]
        sigma_t[active_traders] = (self.__price_square_prefix_sum[-1] - self.__price_square_prefix_sum[-1 - self.__traders['decision_time'][active_traders]]) - total_avgsquare_t[active_traders]
        signal[active_traders] = (current_price - MA_t[active_traders]) / sigma_t[active_traders]
        judge[active_traders] = self.__traders['judge_coef'][active_traders] * sigma_market[active_traders]
            # deal with trade
        risk_trader = (active_traders) & (current_price > MA_t * self.__traders['risk_coef'])
        self.__traders['order_positions'][risk_trader] = -self.__traders['positions'][risk_trader]
        buy_trader = (active_traders) & (~risk_trader) & (signal > judge)
        self.__traders['order_positions'][buy_trader] = np.floor(self.__traders['cash'][buy_trader] / current_price * np.random.uniform(self.__min_buy_proportion, self.__max_buy_proportion, size=np.sum(buy_trader))).astype(np.int32)
        sell_trader = (active_traders) & (~risk_trader) & (signal < -judge)
        self.__traders['order_positions'][sell_trader] = -np.floor(self.__traders['positions'][sell_trader] * np.random.uniform(self.__min_sell_proportion, self.__max_sell_proportion, size=np.sum(sell_trader))).astype(np.int32)
        # deal with cooldown
        active_traders = (self.__traders['cooldown'] == 0)
        if np.any(active_traders):
            active_times = self.__traders['decision_time'][active_traders]
            self.__traders['cooldown'][active_traders] = np.random.randint(active_times, active_times * 2, np.sum(active_traders))
        inactive_traders = ~(active_traders)
        self.__traders['cooldown'][inactive_traders] -= 1
        return finish_position_change(self.__traders, current_price)
    
class ValueInvestors():
    def __init__(self, n: int, 
                 min_start_cash = 40000.0, max_start_cash = 80000.0,
                 min_start_positions = 600, max_start_positions = 1000,
                 min_buy_proportion = 0.1, max_buy_proportion = 0.2,
                 min_sell_proportion = 0.2, max_sell_proportion = 0.3,
                 decision_deviation_scale = 0.015,
                 average_wait_time = 240.0, backruptcy_cash = 2500.0):
        n = np.int32(n)
        value_investors = np.dtype([
            ('cash', 'float64'),
            ('positions', 'int32'),
            ('order_positions', 'int32'),
            ('cooldown', 'int32'),
            ('judge_coef', 'float64'),
        ])
        self.__min_buy_proportion = np.float64(min_buy_proportion)
        self.__max_buy_proportion = np.float64(max_buy_proportion)
        self.__min_sell_proportion = np.float64(min_sell_proportion)
        self.__max_sell_proportion = np.float64(max_sell_proportion)
        self.__decision_deviation_scale = np.float64(decision_deviation_scale)
        self.__average_wait_time = np.float64(average_wait_time)
        self.__bankruptcy_cash = np.float64(backruptcy_cash)
        self.__traders = np.zeros(n, dtype=value_investors)
        self.__traders['cash'] = np.random.uniform(min_start_cash, max_start_cash, n)
        self.__traders['positions'] = np.random.randint(min_start_positions, max_start_positions, n).astype(np.int32)
        self.__traders['order_positions'] = 0
        self.__traders['cooldown'] = np.random.exponential(self.__average_wait_time, n).astype(np.int32)
        self.__traders['judge_coef'] = np.random.uniform(-0.05, 0.05, n)

    def tick_decision(self, current_price: float, basic_value: float) -> tuple[np.int32, np.int32]:
        # deal with bankrupters
        bankrupters = (self.__traders['cash'] <= self.__bankruptcy_cash) & (self.__traders['cooldown'] == 0)
        amount = np.maximum(np.floor((self.__bankruptcy_cash - self.__traders['cash'][bankrupters]) / current_price * 2.0).astype(np.int32), 1)
        self.__traders['order_positions'][bankrupters] = -amount
        # trade
        pridicted_IV = basic_value * (1 + np.random.normal(0, self.__decision_deviation_scale, np.size(self.__traders)))
        buy_signal = 0.9 * pridicted_IV * (1 + self.__traders['judge_coef'])
        sell_signal = 1.1 * pridicted_IV * (1 + self.__traders['judge_coef'])
        buy_traders = (self.__traders['cooldown'] == 0) & (self.__traders['cash'] > self.__bankruptcy_cash) & (current_price < buy_signal)
        self.__traders['order_positions'][buy_traders] = np.floor(self.__traders['cash'][buy_traders] / current_price * np.random.uniform(self.__min_buy_proportion, self.__max_buy_proportion, np.sum(buy_traders))).astype(np.int32)
        sell_traders = (self.__traders['cooldown'] == 0) & (self.__traders['cash'] > self.__bankruptcy_cash) & (current_price > sell_signal)
        self.__traders['order_positions'][sell_traders] = -np.floor(self.__traders['positions'][sell_traders] * np.random.uniform(self.__min_sell_proportion, self.__max_sell_proportion, np.sum(sell_traders))).astype(np.int32)
        # deal with cooldown
        active_traders = (self.__traders['cooldown'] == 0)
        self.__traders['cooldown'][active_traders] = np.random.exponential(self.__average_wait_time, np.sum(active_traders)).astype(np.int32)
        inactive_traders = ~(active_traders)
        self.__traders['cooldown'][inactive_traders] -= 1
        return finish_position_change(self.__traders, current_price)

