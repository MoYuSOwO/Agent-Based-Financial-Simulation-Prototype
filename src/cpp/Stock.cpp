#include "Stock.hpp"
#include <algorithm>
#include <iostream>

const double INF = 1e9;

OrderBook::OrderBook(double start_price) {
    next_id = 1;
    current_price = start_price;
    totalBuyVolume = 0;
    totalSellVolume = 0;
}

unsigned int OrderBook::addOrder(unsigned int quantity, OrderDirection direction, OrderType type, double price) {
    Order order = {next_id, quantity, direction, type, price, 0, 0.0};
    next_id++;
    orders[order.id] = order;
    matchOrders(orders[order.id]);
    return order.id;
}

void OrderBook::cancelOrder(unsigned int order_id) {
    auto active_it = orders.find(order_id);
    if (active_it == orders.end()) return;

    auto iter_it = order_iterators.find(order_id);
    if (iter_it == order_iterators.end()) return;

    unsigned int remaining = active_it->second.quantity - active_it->second.filled_quantity;
    if (active_it->second.direction == OrderDirection::Buy) {
        buy_orders.erase(iter_it->second);
        totalBuyVolume -= remaining;
    } else {
        sell_orders.erase(iter_it->second);
        totalSellVolume -= remaining;
    }
    order_iterators.erase(iter_it);
    orders.erase(active_it);
}

OrderResult OrderBook::getOrder(unsigned int order_id) {
    auto it = orders.find(order_id);
    if (it == orders.end()) {
        OrderResult result = {OrderStatus::None, 0, 0.0};
        return result;
    }
    else if (it->second.filled_quantity == 0) {
        OrderResult result = {OrderStatus::Pending, 0, 0.0};
        return result;
    }
    else if (it->second.filled_quantity < it->second.quantity) {
        OrderResult result = {OrderStatus::partlyFilled, it->second.filled_quantity, it->second.filled_price};
        if (it->second.type == Market) {
            orders.erase(it);
        }
        return result;
    }
    else {
        OrderResult result = {OrderStatus::fullyFilled, it->second.filled_quantity, it->second.filled_price};
        orders.erase(it);
        return result;
    }
}

void OrderBook::matchOrders(Order& order) {
    if (order.direction == Buy) {
        if (order.type == Market) {
            while (!sell_orders.empty() && order.filled_quantity < order.quantity) {
                Order* best = *sell_orders.begin();
                unsigned int fillable = std::min(best->quantity - best->filled_quantity, order.quantity - order.filled_quantity);
                order.filled_price = (order.filled_quantity * order.filled_price + fillable * best->price) / (order.filled_quantity + fillable);
                order.filled_quantity += fillable;
                best->filled_price = (best->filled_quantity * best->filled_price + fillable * best->price) / (best->filled_quantity + fillable);
                best->filled_quantity += fillable;
                current_price = best->price;
                totalSellVolume -= fillable;
                if (best->filled_quantity >= best->quantity) {
                    sell_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
            }
        }
        else {
            while (!sell_orders.empty() && order.filled_quantity < order.quantity) {
                Order* best = *sell_orders.begin();
                if (best->price > order.price) {
                    auto& ref = orders[order.id];
                    auto iter = buy_orders.insert(&ref);
                    order_iterators[order.id] = iter;
                    totalBuyVolume += order.quantity - order.filled_quantity;
                    return;
                }
                unsigned int fillable = std::min(best->quantity - best->filled_quantity, order.quantity - order.filled_quantity);
                order.filled_price = (order.filled_quantity * order.filled_price + fillable * best->price) / (order.filled_quantity + fillable);
                order.filled_quantity += fillable;
                best->filled_price = (best->filled_quantity * best->filled_price + fillable * best->price) / (best->filled_quantity + fillable);
                best->filled_quantity += fillable;
                current_price = best->price;
                totalSellVolume -= fillable;
                if (best->filled_quantity >= best->quantity) {
                    sell_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
            }
            if (order.filled_quantity < order.quantity) {
                auto& ref = orders[order.id];
                auto iter = buy_orders.insert(&ref);
                order_iterators[order.id] = iter;
                totalBuyVolume += order.quantity - order.filled_quantity;
            }
        }
    }
    else {
        if (order.type == Market) {
            while (!buy_orders.empty() && order.filled_quantity < order.quantity) {
                Order* best = *buy_orders.begin();
                unsigned int fillable = std::min(best->quantity - best->filled_quantity, order.quantity - order.filled_quantity);
                order.filled_price = (order.filled_quantity * order.filled_price + fillable * best->price) / (order.filled_quantity + fillable);
                order.filled_quantity += fillable;
                best->filled_price = (best->filled_quantity * best->filled_price + fillable * best->price) / (best->filled_quantity + fillable);
                best->filled_quantity += fillable;
                current_price = best->price;
                totalBuyVolume -= fillable;
                if (best->filled_quantity >= best->quantity) {
                    buy_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
            }
        }
        else {
            while (!buy_orders.empty() && order.filled_quantity < order.quantity) {
                Order* best = *buy_orders.begin();
                if (best->price < order.price) {
                    auto& ref = orders[order.id];
                    auto iter = sell_orders.insert(&ref);
                    order_iterators[order.id] = iter;
                    totalSellVolume += order.quantity - order.filled_quantity;
                    return;
                }
                unsigned int fillable = std::min(best->quantity - best->filled_quantity, order.quantity - order.filled_quantity);
                order.filled_price = (order.filled_quantity * order.filled_price + fillable * best->price) / (order.filled_quantity + fillable);
                order.filled_quantity += fillable;
                best->filled_price = (best->filled_quantity * best->filled_price + fillable * best->price) / (best->filled_quantity + fillable);
                best->filled_quantity += fillable;
                current_price = best->price;
                totalBuyVolume -= fillable;
                if (best->filled_quantity >= best->quantity) {
                    buy_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
            }
            if (order.filled_quantity < order.quantity) {
                auto& ref = orders[order.id];
                auto iter = sell_orders.insert(&ref);
                order_iterators[order.id] = iter;
                totalSellVolume += order.quantity - order.filled_quantity;
            }
        }
    }
}

double OrderBook::getCurrentPrice() {
    return current_price;
}

double OrderBook::getBuyPrice() {
    if (buy_orders.empty()) return 0.0;
    return (*buy_orders.begin())->price;
}

double OrderBook::getSellPrice() {
    if (sell_orders.empty()) return 0.0;
    return (*sell_orders.begin())->price;
}

unsigned int OrderBook::getBuyVolume() {
    return totalBuyVolume;
}

unsigned int OrderBook::getSellVolume() {
    return totalSellVolume;
}

void OrderBook::resetAll() {
    buy_orders.clear();
    sell_orders.clear();
    order_iterators.clear();
    orders.clear();
    totalBuyVolume = 0;
    totalSellVolume = 0;
    next_id = 1;
}

void OrderBook::__printOrderBook__() {
    std::cout << "Buy Orders:" << std::endl;
    for (auto it = buy_orders.begin(); it != buy_orders.end(); it++) {
        std::cout << "Order ID: " << (*it)->id << " Quantity: " << (*it)->quantity - (*it)->filled_quantity << " Price: " << (*it)->price << " Filled_Price: " << (*it)->filled_price << std::endl;
    }
    std::cout << "Sell Orders:" << std::endl;
    for (auto it = sell_orders.begin(); it != sell_orders.end(); it++) {
        std::cout << "Order ID: " << (*it)->id << " Quantity: " << (*it)->quantity - (*it)->filled_quantity << " Price: " << (*it)->price << " Filled_Price: " << (*it)->filled_price << std::endl;
    }
    std::cout << "Current Price: " << current_price << std::endl;
    std::cout << "Buy Volume: " << totalBuyVolume << std::endl;
    std::cout << "Sell Volume: " << totalSellVolume << std::endl;
}

Stock::Stock(double basicValue, double startPrice) {
    orderbook = OrderBook(startPrice);
    basicValue = basicValue;
    currentDay = {-INF, INF, 0.0, 0.0};
}

void Stock::tickUpdate() {
    tickPriceDaily.push_back(orderbook.getCurrentPrice());
    if (tickPriceDaily.size() > 1) {
        currentDay.high = std::max(currentDay.high, tickPriceDaily.back());
        currentDay.low = std::min(currentDay.low, tickPriceDaily.back());
        currentDay.close = tickPriceDaily.back();
        currentDay.open = tickPriceDaily.front();
    }
}

void Stock::dayUpdate() {
    dayPriceHistory.push_back(currentDay);
    tickPriceDaily.clear();
    orderbook.resetAll();
    currentDay = {-INF, INF, 0.0, 0.0};
}