#include "Stock.hpp"
#include <iostream>
#include <fstream>
#include <algorithm>

using namespace std;

int main() {
    Stock stock(100.0, 100.0);
    while (true) {
        string command;
        cin >> command;
        if (command == "add") {
            unsigned int quantity;
            string direction;
            string type;
            double price;
            cin >> quantity >> direction >> type >> price;
            OrderDirection dir = direction == "Buy" ? OrderDirection::Buy : OrderDirection::Sell;
            OrderType t = type == "Limit" ? OrderType::Limit : OrderType::Market;
            stock.orderbook.addOrder(quantity, dir, t, price);
        } else if (command == "cancel") {
            unsigned int id;
            cin >> id;
            stock.orderbook.cancelOrder(id);
        } else if (command == "get") {
            unsigned int id;
            cin >> id;
            OrderResult result = stock.orderbook.getOrder(id);
            if (result.status == OrderStatus::None) {
                cout << "Order not found" << endl;
            } else if (result.status == OrderStatus::Pending) {
                cout << "Order is pending" << endl;
            } else if (result.status == OrderStatus::partlyFilled) {
                cout << "Order is partly filled: " << result.filled_quantity << " at " << result.filled_price << endl;
            } else if (result.status == OrderStatus::fullyFilled) {
                cout << "Order is fully filled: " << result.filled_quantity << " at " << result.filled_price << endl;
            }
        } else if (command == "current") {
            cout << "Current price: " << stock.orderbook.getCurrentPrice() << endl;
        } else if (command == "buy") {
            cout << "Best buy price: " << stock.orderbook.getBuyPrice() << endl;
        } else if (command == "sell") {
            cout << "Best sell price: " << stock.orderbook.getSellPrice() << endl;
        } else if (command == "buy_volume") {
            cout << "Total buy volume: " << stock.orderbook.getBuyVolume() << endl;
        } else if (command == "sell_volume") {
            cout << "Total sell volume: " << stock.orderbook.getSellVolume() << endl;
        } else if (command == "reset") {
            stock.orderbook.resetAll();
        } else if (command == "print") {
            stock.orderbook.__printOrderBook__();
        } else if (command == "exit") {
            break;
        }
    }

    return 0;
}