#include <set>
#include <unordered_map>

enum OrderStatus {
    Pending,
    partlyFilled,
    fullyFilled,
    Canceled,
    None
};

enum OrderDirection {
    Buy,
    Sell
};

enum OrderType {
    Limit,
    Market
};

struct OrderResult {
    OrderStatus status;
    unsigned int filled_quantity;
    double filled_price;
};

struct Order {
    unsigned int id;
    unsigned int quantity;
    OrderDirection direction;
    OrderType type;
    double price;
    //change:
    unsigned int filled_quantity;
    double filled_price;
};

class OrderBook {
    public:
        OrderBook(double start_price=100.0) {}
        unsigned int addOrder(unsigned int quantity, OrderDirection direction, OrderType type=Market, double price=0.0);
        void cancelOrder(unsigned int order_id);
        OrderResult getOrder(unsigned int order_id);
        double getCurrentPrice();
        double getBuyPrice();
        double getSellPrice();
        unsigned int getBuyVolume();
        unsigned int getSellVolume();
    private:
        unsigned int totalBuyVolume;
        unsigned int totalSellVolume;
        unsigned int next_id;
        double current_price;
        std::unordered_map<unsigned int, Order> orders;
        std::unordered_map<unsigned int, std::multiset<Order*>::iterator> order_iterators;
        struct BuyComparator {
            bool operator()(const Order* a, const Order* b) const {
                return (a->price > b->price) || 
                      ((a->price == b->price) && (a->id < b->id));
            }
        };
        struct SellComparator {
            bool operator()(const Order* a, const Order* b) const {
                return (a->price < b->price) || 
                      ((a->price == b->price) && (a->id < b->id));
            }
        };
        std::multiset<Order*, BuyComparator> buy_orders;
        std::multiset<Order*, SellComparator> sell_orders;
        void matchOrders(Order& order);
};