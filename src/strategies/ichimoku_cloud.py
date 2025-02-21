import backtrader as bt

class IchimokuIndicator(bt.Indicator):

    lines = (
        'tenkan',  
        'kijun',   
        'spanA',   
        'spanB',   
        'chikou',  
    )
    params = (
        ('tenkan_period', 9),
        ('kijun_period', 26),
        ('senkou_b_period', 52),
        ('shift', 26),
    )

    def __init__(self):
        self.l.tenkan = (
            bt.indicators.Highest(self.data.high, period=self.p.tenkan_period) + 
            bt.indicators.Lowest(self.data.low, period=self.p.tenkan_period)
        ) / 2.0

        self.l.kijun = (
            bt.indicators.Highest(self.data.high, period=self.p.kijun_period) + 
            bt.indicators.Lowest(self.data.low, period=self.p.kijun_period)
        ) / 2.0

        self.l.spanA = (self.l.tenkan + self.l.kijun) / 2.0

        self.l.spanB = (
            bt.indicators.Highest(self.data.high, period=self.p.senkou_b_period) + 
            bt.indicators.Lowest(self.data.low, period=self.p.senkou_b_period)
        ) / 2.0

        self.l.chikou = self.data.close(-self.p.shift)

    def next(self):
        pass


class IchimokuStrategy(bt.Strategy):
    """
    *Go LONG if price is above both Span A and Span B (the 'cloud'), and Tenkan crosses above Kijun (bullish signal).
    *Exit if price falls back into or below the cloud, or Tenkan crosses below Kijun (bearish signal).
    """

    params = (
        ('tenkan_period', 9),
        ('kijun_period', 26),
        ('senkou_b_period', 52),
        ('shift', 26),
    )

    def __init__(self):
        self.ichimoku = IchimokuIndicator(
            self.datas[0],
            tenkan_period=self.p.tenkan_period,
            kijun_period=self.p.kijun_period,
            senkou_b_period=self.p.senkou_b_period,
            shift=self.p.shift
        )
        self.log_enabled = True

    def log(self, txt):
        if self.log_enabled:
            dt = self.datas[0].datetime.datetime(0)
            print(f'{dt} | {txt}')

    def next(self):
        close_price = self.data.close[0]
        tenkan = self.ichimoku.tenkan[0]
        kijun = self.ichimoku.kijun[0]
        spanA = self.ichimoku.spanA[0]
        spanB = self.ichimoku.spanB[0]
 
        cloud_top = max(spanA, spanB)
        cloud_bottom = min(spanA, spanB)

        self.log(f"Close={close_price:.4f} | Tenkan={tenkan:.4f} | Kijun={kijun:.4f} "
                 f"| SpanA={spanA:.4f} | SpanB={spanB:.4f} | Position={self.position.size}")

        above_cloud = close_price > cloud_top
        below_cloud = close_price < cloud_bottom

        # Tenkan / Kijun cross
        bullish_cross = (tenkan > kijun and self.ichimoku.tenkan[-1] <= self.ichimoku.kijun[-1])
        bearish_cross = (tenkan < kijun and self.ichimoku.tenkan[-1] >= self.ichimoku.kijun[-1])

        if not self.position:
            if above_cloud and bullish_cross:
                self.log(">>> BUY SIGNAL (Above cloud + Tenkan/Kijun cross up)")
                self.buy()
        else:
            if (not above_cloud) or bearish_cross:
                self.log(">>> SELL SIGNAL (Price not above cloud or T/K cross down)")
                self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.4f}, '
                         f'Cost: {order.executed.value:.4f}, '
                         f'Comm: {order.executed.comm:.4f}')
            else:
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.4f}, '
                         f'Cost: {order.executed.value:.4f}, '
                         f'Comm: {order.executed.comm:.4f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Failed')
