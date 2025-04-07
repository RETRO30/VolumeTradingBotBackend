# bybit_client.py
import aiohttp
import time
import hmac
import hashlib
from urllib.parse import urlencode

class AsyncBybitClient:
    def __init__(self, api_key, api_secret, endpoint="https://api.bybit.com"):
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')
        self.endpoint = endpoint
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    def _sign(self, params):
        # Сортируем параметры и формируем query string для подписи
        query_string = urlencode(sorted(params.items()))
        signature = hmac.new(self.api_secret, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    async def _request(self, method, path, params=None):
        if params is None:
            params = {}
        # Добавляем параметры аутентификации
        params["api_key"] = self.api_key
        params["timestamp"] = int(time.time() * 1000)
        params["recv_window"] = 5000
        params["sign"] = self._sign(params)

        url = self.endpoint + path

        if method.upper() == "GET":
            async with self.session.get(url, params=params) as response:
                return await response.json()
        elif method.upper() == "POST":
            async with self.session.post(url, data=params) as response:
                return await response.json()
        else:
            raise ValueError("Unsupported HTTP method")

    async def latest_information_for_symbol(self, symbol):
        """
        Получает информацию по тикеру для указанного символа.
        """
        path = "/v2/public/tickers"
        params = {"symbol": symbol}
        return await self._request("GET", path, params)

    async def place_active_order(self, symbol, side, order_type, qty, price=None, time_in_force="GoodTillCancel"):
        """
        Выставляет активный (лимитный или рыночный) ордер.
        """
        path = "/v2/private/order/create"
        params = {
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "qty": qty,
            "time_in_force": time_in_force,
        }
        if price is not None:
            params["price"] = price
        return await self._request("POST", path, params)

    async def get_active_order(self, symbol, order_id=None):
        """
        Получает информацию об активном ордере. Если order_id не указан, возвращает все активные ордера для символа.
        """
        path = "/v2/private/order"
        params = {"symbol": symbol}
        if order_id:
            params["order_id"] = order_id
        return await self._request("GET", path, params)

    async def cancel_active_order(self, symbol, order_id):
        """
        Отменяет активный ордер по order_id.
        """
        path = "/v2/private/order/cancel"
        params = {"symbol": symbol, "order_id": order_id}
        return await self._request("POST", path, params)
