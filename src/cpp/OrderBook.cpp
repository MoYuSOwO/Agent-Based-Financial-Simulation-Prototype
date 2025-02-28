#include "OrderBook.hpp"

OrderBook::OrderBook(double start_price) {
    next_id = 1;
    current_price = start_price;
}

unsigned int OrderBook::addOrder(unsigned int quantity, OrderDirection direction, OrderType  type, double price) {
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

    if (active_it->second.direction == OrderDirection::Buy) {
        buy_orders.erase(iter_it->second);
    } else {
        sell_orders.erase(iter_it->second);
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
                    return;
                }
                unsigned int fillable = std::min(best->quantity - best->filled_quantity, order.quantity - order.filled_quantity);
                order.filled_price = (order.filled_quantity * order.filled_price + fillable * best->price) / (order.filled_quantity + fillable);
                order.filled_quantity += fillable;
                best->filled_price = (best->filled_quantity * best->filled_price + fillable * best->price) / (best->filled_quantity + fillable);
                best->filled_quantity += fillable;
                current_price = best->price;
                if (best->filled_quantity >= best->quantity) {
                    sell_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
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
                if (best->filled_quantity >= best->quantity) {
                    buy_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
            }
        }
        else {
            while (!buy_orders.empty() && order.filled_quantity < order.quantity) {
                Order* best = *buy_orders.begin();
                if (best->price > order.price) {
                    auto& ref = orders[order.id];
                    auto iter = sell_orders.insert(&ref);
                    order_iterators[order.id] = iter;
                    return;
                }
                unsigned int fillable = std::min(best->quantity - best->filled_quantity, order.quantity - order.filled_quantity);
                order.filled_price = (order.filled_quantity * order.filled_price + fillable * best->price) / (order.filled_quantity + fillable);
                order.filled_quantity += fillable;
                best->filled_price = (best->filled_quantity * best->filled_price + fillable * best->price) / (best->filled_quantity + fillable);
                best->filled_quantity += fillable;
                current_price = best->price;
                if (best->filled_quantity >= best->quantity) {
                    buy_orders.erase(order_iterators[best->id]);
                    order_iterators.erase(best->id);
                }
            }
        }
    }
}

double OrderBook::getCurrentPrice() {
    return current_price;
}