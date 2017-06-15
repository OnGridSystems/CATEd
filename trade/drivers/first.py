# import poloniex_driver
# from trade.drivers.btce_trader import BtceTrader
# from bittrex_trader import BittrexTrader

# p = poloniex_driver.poloniex(APIKey='6Y7O547J-HMDU8LWR-CJLV7CCF-4ARNQZ6N', Secret='db062a08e7c05f878b0955648ba8371808cf4eff273decbd5fcc5a19eaa76fe816052255e880c8762f3786a43768162a26ac25a4d30859df9c7a7874493af952')
# ticker = p.returnCompleteBalances()

# b = BtceTrader(key='V3PWX200-RCVDH3MW-BX5O44QC-J67V0OUP-F8Q4MTM3', secret='f0a37d7e190488c9ccf7c07c5daef10e7ca8251c9fa74924d6e587402f566c3b')

# b = BittrexTrader(key='ecd09df9ef234b589ebb408dc4b42547', secret='97b4b1fcafc24bd793adccba7d0b3c85')

# b.pull_exchanges()
# b.pull_orders()
# b.pull_balances()
# b

from trade.drivers.bittrex_driver import Bittrex

b = Bittrex(api_key='ecd09df9ef234b589ebb408dc4b42547', api_secret='97b4b1fcafc24bd793adccba7d0b3c85')
res = b.get_balances()
res