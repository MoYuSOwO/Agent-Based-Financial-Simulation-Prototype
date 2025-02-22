from datetime import datetime, timedelta
from market import Node
from trader import RandomTrader, TrendTrader, ValueTrader
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

DAY_TICK = 14400

def draw_day_price(tick_price_history: list):
    tick_price_history = tick_price_history[100:150]
    time_seconds = list(range(len(tick_price_history)))
    plt.figure(figsize=(12, 6))
    plt.plot(time_seconds, tick_price_history, 
         color='steelblue',  # 线条颜色
         linewidth=1.5,      # 线宽
         label='Node Price')    # 图例名称
    plt.title('Node Price', fontsize=14, pad=20)
    plt.xlabel('time(second)', fontsize=12)
    plt.ylabel('price', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
def draw_day_advance_kline(tick_price_history: list, name: str):
    trading_hours = [
        (pd.Timestamp("09:30:00"), pd.Timestamp("11:29:59")),
        (pd.Timestamp("13:00:00"), pd.Timestamp("14:59:58"))
    ]
    timestamps = pd.DatetimeIndex([])
    for start, end in trading_hours:
        timestamps = timestamps.union(pd.date_range(start, end, freq="s"))
    df = pd.DataFrame({
        'timestamp': timestamps,
        'price': tick_price_history[0:14399]
    })
    kline_df = df.resample('2min', on='timestamp', origin='start').agg({
        'price': ['first', 'last', 'max', 'min']
    })
    kline_df.columns = ['open', 'close', 'high', 'low']
    kline_df = kline_df.between_time("09:30", "15:00").dropna()
    # 创建交互式K线图
    fig = go.Figure(data=[go.Candlestick(
        x=kline_df.index,  # 时间轴
        open=kline_df['open'],
        high=kline_df['high'],
        low=kline_df['low'],
        close=kline_df['close'],
        increasing_line_color='red',  # 上涨颜色
        decreasing_line_color='green' # 下跌颜色
    )])
    # 设置专业图表参数
    fig.update_layout(
        title='可交互式K线图（5秒周期）',
        xaxis_title='时间',
        yaxis_title='价格',
        xaxis_rangeslider_visible=False,  # 底部滑动条（可设置为True）
        dragmode='pan',  # 拖动模式：'pan'平移 / 'zoom'缩放
        hovermode='x unified',  # 显示十字光标
        template='plotly_white'  # 主题：白色背景
    )
    # 添加控制按钮
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(label="线性坐标", method="relayout", args=[{"yaxis.type": "linear"}]),
                    dict(label="对数坐标", method="relayout", args=[{"yaxis.type": "log"}]),
                    dict(label="重置缩放", method="relayout", args=[{"xaxis.autorange": True, "yaxis.autorange": True}])
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )
    # 显示图表（自动打开浏览器）
    # fig.show()
    fig.write_html('day' + name + '.html')

def draw_month_advance_kline(day_price_history: list, name: str):
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(len(day_price_history['high']))]
    df = pd.DataFrame(day_price_history, index=dates)
    df = df.dropna()
    candlestick = go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='red',  # 阳线颜色
        decreasing_line_color='green',# 阴线颜色
        name='日K线'
    )
    layout = go.Layout(
        title='多日K线走势分析',
        xaxis=dict(
            type='date',
            tickformat='%Y-%m-%d',  # 显示完整日期
            rangeslider=dict(visible=False)  # 隐藏底部滑动条
        ),
        yaxis=dict(title='价格'),
        hovermode='x unified',  # 显示十字准星
        template='plotly_white',  # 白色主题
        height=600
    )
    fig = go.Figure(data=[candlestick], layout=layout)
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(label="日线",
                        method="update",
                        args=[{"visible": [True, False]}]),
                    dict(label="周线",
                        method="restyle",
                        args=[{"x": [df.resample('W').agg({'open':'first','high':'max','low':'min','close':'last'}).index]}])
                ]
            )
        ]
    )
    # 显示图表（自动打开浏览器）
    # fig.show()
    fig.write_html('month' + name + '.html')

if __name__ == "__main__":
    node = Node()
    random_trader: RandomTrader = []
    trend_trader: TrendTrader = []
    value_trader: ValueTrader = []
    for i in range(0, 500):
        random_trader.append(RandomTrader())
    for i in range(0, 200):
        trend_trader.append(TrendTrader())
    for i in range(0, 300):
        value_trader.append(ValueTrader())
    for tick in range(1, DAY_TICK * 30 + 1):
        if tick % (DAY_TICK * 30) == 0:
            day_price_history = node.get_day_price_history()
            draw_month_advance_kline(day_price_history, str(tick // (DAY_TICK * 30)))
        if tick % DAY_TICK == 0:
            tick_price_history = node.get_tick_price_history()
            # draw_day_price(tick_price_history)
            draw_day_advance_kline(tick_price_history, str(tick // DAY_TICK))
            node.day_update()
        current_price = node.get_current_price()
        day_price_history = node.get_day_price_history()
        depth = node.get_market_depth()
        for trader in random_trader:
            position_change = trader.tick_decision(current_price, depth)
            node.clinch(position_change)
        for trader in trend_trader:
            position_change = trader.tick_decision(current_price, node.get_1080ticks_history(), depth)
            node.clinch(position_change)
        for trader in value_trader:
            position_change = trader.tick_decision(current_price, node.get_basic_value(), depth)
            node.clinch(position_change)
        node.tick_update(tick)
    