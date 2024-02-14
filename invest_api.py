from functools import lru_cache
from json import loads
import requests
import tinkoff.invest
from tinkoff.invest import Client
import time
url = 'https://newsapi.org/v2/everything?q={0}&apiKey=5c4242a5d3fe4cdfa368bb9a8e3bf295'
class InvestSession(object):
    def __init__(self, news_token):
        self._token = news_token
    @lru_cache(maxsize=1000)
    def find_account(self, token):
        try:
            with Client(token) as client:
                account, *dt = client.users.get_accounts().accounts
                while dt and (account.status != tinkoff.invest.AccountStatus.ACCOUNT_STATUS_OPEN):
                    account, *dt = dt
                if account.status == tinkoff.invest.AccountStatus.ACCOUNT_STATUS_OPEN:
                    return account.id
        finally:
            pass
        return 0
    def check_portfolio(self, token):
        with Client(token) as client:
            ai = self.find_account(token)
            resp = client.operations.get_portfolio(account_id=ai)
            total = resp.total_amount_portfolio
            total = float(str(total.units)+'.'+str(total.nano))
            result_dict = dict()
            for i in resp.positions:
                curr = float(str(i.current_price.units)+'.'+str(i.current_price.nano)) * \
                       float(str(i.quantity_lots.units)+'.'+str(i.quantity_lots.nano))
                t = client.instruments.get_instrument_by(id_type=tinkoff.invest.InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=i.figi).instrument
                result_dict[t.name.replace(" ", "%20")] = result_dict.get(t.name, 0) + curr/total
            result_dict = dict(sorted(result_dict.items(), key=lambda item: item[1]))
            return list(result_dict.keys())[-20:]
    def find_news(self, token):
        urls = []
        for i in self.check_portfolio(token):
            with requests.get(url.format(i)) as q:
                d = loads(q.text)['articles']
                for j in range(min(5, len(d))):
                    t = d[j]
                    urls.append((t['title'], t['url']))
        return urls[::-1]
