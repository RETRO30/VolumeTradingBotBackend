# grid_worker.py
import asyncio
from src.service.bybit_client import AsyncBybitClient
from src.service.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import engine
from src.manage_accounts.models import Account, Trade, TradeStatus

# Функция для создания асинхронного клиента Bybit
async def create_client(account: Account):
    client = AsyncBybitClient(
        api_key=account.api_key,
        api_secret=account.secret_key
    )
    return client

# Получение текущей цены по инструменту
async def get_current_price(account: Account):
    client = await create_client(account)
    response = await client.latest_information_for_symbol(symbol=account.symbol)
    price = response['result'][0]['last_price']
    return float(price)

# Сохранение сделки (ордера) в БД
async def record_trade(account: Account, order_info):
    async with AsyncSession(engine) as session:
        trade = Trade(
            symbol=account.symbol,
            side=order_info['side'],
            price=order_info['price'],
            quantity=order_info['quantity'],
            status=TradeStatus.open
        )
        trade.account_id = account.id
        session.add(trade)
        await session.commit()
        logger.info(f"{account.name}({account.id}): Recorded trade {trade}")

# Выставление лимитного ордера
async def place_limit_order(account: Account, symbol: str, side: str, price: float, quantity: float):
    client = await create_client(account)
    order = await client.place_active_order(
        symbol=symbol,
        side=side,
        order_type="Limit",
        qty=quantity,
        price=price,
        time_in_force="GoodTillCancel"
    )
    logger.info(f"{account.name}({account.id}): Placed limit {side} order at {price} with quantity {quantity}")
    # Дублируем ордер в БД
    await record_trade(account, {"side": side.lower(), "price": price, "quantity": quantity})
    # Добавляем поле side для дальнейшей обработки
    order['side'] = side.lower()
    return order

# Проверка исполнения ордера
async def check_order_executed(account: Account, order: dict):
    client = await create_client(account)
    response = await client.get_active_order(symbol=account.symbol, order_id=order['order_id'])
    order_status = response['result']['order_status']
    return order_status == "Filled"

# Отмена отдельного ордера
async def cancel_order(account: Account, order: dict):
    client = await create_client(account)
    await client.cancel_active_order(symbol=account.symbol, order_id=order['order_id'])
    logger.info(f"{account.name}({account.id}): Cancelled order {order['order_id']} at price {order['price']}")

# Метод для отмены всех активных ордеров на аккаунте
async def cancel_all_orders_for_account(account: Account):
    client = await create_client(account)
    try:
        response = await client.get_active_order(symbol=account.symbol)
        orders = response.get('result', [])
        if orders:
            for order in orders:
                await client.cancel_active_order(symbol=account.symbol, order_id=order['order_id'])
                logger.info(f"{account.name}({account.id}): Cancelled order {order['order_id']} at price {order.get('price')}")
        else:
            logger.info(f"{account.name}({account.id}): No active orders to cancel.")
    except Exception as e:
        logger.error(f"{account.name}({account.id}): Failed to cancel all orders: {e}")

# Выставление рыночного ордера на продажу (для stoploss)
async def place_market_sell(account, symbol, quantity):
    client = await create_client(account)
    order = await client.place_active_order(
        symbol=symbol,
        side="Sell",
        order_type="Market",
        qty=quantity,
        time_in_force="ImmediateOrCancel"
    )
    logger.info(f"{account.name}({account.id}): Placed market sell order with quantity {quantity}")
    await record_trade(account, {"side": "sell", "price": order.get('price', 0), "quantity": quantity})
    return order

# Простейший расчёт количества для ордера
def compute_quantity(account, price, side):
    quantity = account.deposit / account.grid_count / price
    return round(quantity, 4)

# Проверка условия стоплосса для ордеров на продажу
async def check_stop_loss(account, current_price, orders):
    if current_price < account.stop_loss:
        for level, order in list(orders.items()):
            if order['side'] == 'sell':
                await cancel_order(account, order)
                logger.info(f"{account.name}({account.id}): Stoploss triggered at level {level}")
                market_order = await place_market_sell(account, account.symbol, order['quantity'])
                orders.pop(level, None)

# Основная функция грид-бота для аккаунта
async def run_grid_bot_for_account(account):
    # Вычисляем шаг и уровни сетки
    step = (account.end_price - account.start_price) / account.grid_count
    buy_levels = [round(account.start_price + i * step, 2) for i in range(account.grid_count)]
    sell_levels = [round(account.start_price + i * step, 2) for i in range(1, account.grid_count + 1)]
    
    orders = {}  # Отслеживаем ордера: {level: order}
    logger.info(f"{account.name}({account.id}): Starting grid bot with buy levels {buy_levels} and sell levels {sell_levels}")
    
    while True:
        try:
            current_price = await get_current_price(account)
            logger.info(f"{account.name}({account.id}): Current market price is {current_price}")
            
            # Проверка стоплосса для активных ордеров на продажу
            await check_stop_loss(account, current_price, orders)
            
            # Выставляем лимитные ордера на покупку, если их ещё нет
            for level in buy_levels:
                if level not in orders:
                    quantity = compute_quantity(account, level, "buy")
                    order = await place_limit_order(account, account.symbol, "Buy", level, quantity)
                    orders[level] = order

            # Выставляем лимитные ордера на продажу, если их ещё нет
            for level in sell_levels:
                if level not in orders:
                    quantity = compute_quantity(account, level, "sell")
                    order = await place_limit_order(account, account.symbol, "Sell", level, quantity)
                    orders[level] = order
            
            # Проверяем исполнение ордеров и, если ордер исполнен, выставляем ордер противоположной стороны
            for level, order in list(orders.items()):
                executed = await check_order_executed(account, order)
                if executed:
                    logger.info(f"{account.name}({account.id}): Order at level {level} executed, side: {order['side']}")
                    orders.pop(level, None)
                    # Выставляем ордер противоположной стороны
                    opposite_side = "Sell" if order['side'] == "buy" else "Buy"
                    quantity = order['quantity']
                    new_order = await place_limit_order(account, account.symbol, opposite_side, level, quantity)
                    orders[level] = new_order
            
            await asyncio.sleep(5)
        
        except asyncio.CancelledError:
            logger.info(f"{account.name}({account.id}): Grid bot cancelled.")
            break
        except Exception as e:
            logger.error(f"{account.name}({account.id}): Error in grid bot: {e}")
            await asyncio.sleep(5)
