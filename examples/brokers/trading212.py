from json import JSONDecodeError

import requests

from broker import Broker


class Trading212:
    def __init__(self, apiKey: str, mode: str = "live"):
        self.headers = {"Authorization": apiKey, "Content-Type": "application/json"}
        self.api_version = 0
        self.page_size = 20
        self.mode = mode

        self.market = self.get_instruments()
        print(f"Found {len(self.market)} stocks listed on Trading 212")

        self.portfolio = self.get_open_positions()
        print(f"Holding {len(self.portfolio)} Positions")

        # want shortName from market where ticker is in portfolio, for yfinance
        owned = [s["ticker"] for s in self.portfolio]
        self.tracked_market = [
            stock for stock in self.market if stock["ticker"] in owned
        ]

    def get_tracked_symbols(self):
        return [stock["shortName"] for stock in self.tracked_market]

    def get_tracked_instrument(self, symbol):
        return list(
            filter(lambda stock: stock["shortName"] is symbol, self.tracked_market)
        )

    #
    # REST API methods
    #

    class TokenException(Exception):
        pass

    class UnauthorizedException(Exception):
        pass

    class RateLimitException(Exception):
        pass

    def __check_response(self, response):
        if response.status_code == 401:
            raise self.TokenException(
                f"[{response.status_code}] {response.reason}: Bad Token"
            )
        if response.status_code == 403:
            raise self.UnauthorizedException(
                f"[{response.status_code}] {response.reason}: Scope missing for Token"
            )
        if response.status_code == 408:
            raise self.UnauthorizedException(
                f"[{response.status_code}] {response.reason}: Timeout"
            )
        if response.status_code == 429:
            raise self.RateLimitException(
                f"[{response.status_code}] {response.reason}: Limited 1/30s"
            )

    def __api_get(self, url, query):
        data = None
        try:
            response = requests.get(url=url, params=query, headers=self.headers)
            self.__check_response(response)
            data = response.json()
        except JSONDecodeError as e:
            print("Response could not be serialized")
            print(e)
        except Exception as e:
            print(e)
        return data

    def __api_post(self, url, json, query):
        data = None
        try:
            response = requests.post(
                url=url, json=json, params=query, headers=self.headers
            )
            self.__check_response(response)
            data = response.json()
        except JSONDecodeError as e:
            print("Response could not be serialized")
            print(e)
        except Exception as e:
            print(e)
        return data

    #
    # REST API
    #

    def get_account(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/account/info"
        return self.__api_get(url, None)

    def get_report(self, start, end):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/history/exports"
        payload = {
            "dataIncluded": {
                "includeDividends": True,
                "includeInterest": True,
                "includeOrders": True,
                "includeTransactions": True,
            },
            "timeFrom": start,
            "timeTo": end,
        }
        return self.__api_post(url, json=payload)

    def get_pies(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/pies"
        return self.__api_get(url, None)

    def get_pie(self, id):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/pies/{id}"
        return self.__api_get(url, None)

    def get_instruments(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/metadata/instruments"
        return self.__api_get(url, None)

    def get_position(self, ticker):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/portfolio/{ticker}"
        return self.__api_get(url, None)

    def get_open_positions(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/portfolio"
        return self.__api_get(url, None)

    def get_transactions(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/history/transactions"
        query = {"cursor": "string", "limit": f"{self.page_size}"}
        return self.__api_get(url, query)

    def get_orders(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/equity/history/orders"
        query = {"cursor": "0", "ticker": "string", "limit": f"{self.page_size}"}
        return self.__api_get(url, query)

    def get_dividends(self):
        url = f"https://{self.mode}.trading212.com/api/v{self.api_version}/history/dividends"
        query = {"cursor": "0", "ticker": "string", "limit": f"{self.page_size}"}
        return self.__api_get(url, query)


class Trading212Broker(Trading212, Broker):
    """Broker implementation backed by the Trading 212 API."""

    def __init__(self, apiKey: str, mode: str = "live"):
        Trading212.__init__(self, apiKey=apiKey, mode=mode)

    def capital(self) -> float:
        account = self.get_account()
        return float(account.get("cash", 0.0)) if account else 0.0

    def investments(self) -> float:
        account = self.get_account()
        return float(account.get("invested", 0.0)) if account else 0.0

    def position(self, symbol: str) -> float:
        pos = self.get_position(symbol)
        return float(pos.get("quantity", 0.0)) if pos else 0.0

    def price(self, symbol: str) -> float:
        pos = self.get_position(symbol)
        return float(pos.get("currentPrice", 0.0)) if pos else 0.0

    def stamp_duty(self, symbol: str) -> float:
        return 0.0

    def fees(self, symbol: str) -> float:
        return 0.0

    def buy(self, symbol: str, amount: float) -> float:
        # TODO: implement via Trading 212 order API
        return 0.0

    def sell(self, symbol: str, amount: float) -> float:
        # TODO: implement via Trading 212 order API
        return 0.0
