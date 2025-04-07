# manager.py
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.database import engine
from src.manage_accounts.models import Account, AccountStatus
from src.service.logger import logger
from src.service.grid_worker import run_grid_bot_for_account, cancel_all_orders_for_account

async_session = async_sessionmaker(engine, expire_on_commit=False)

class AccountManager:
    def __init__(self):
        self.tasks = {}  # id: asyncio.Task

    async def run(self):
        while True:
            async with async_session() as session:
                result = await session.execute(select(Account))
                accounts = result.scalars().all()
                logger.info(f"Found {len(accounts)} accounts")
                running_ids = []
                for acc in accounts:
                    if acc.status == AccountStatus.running:
                        running_ids.append(acc.id)
                        if acc.id not in self.tasks:
                            logger.info(f"{acc.name}(id={acc.id}): start bot")
                            self.tasks[acc.id] = asyncio.create_task(run_grid_bot_for_account(acc))

                    elif acc.status == AccountStatus.stopped:
                        if acc.id in self.tasks:
                            logger.info(f"{acc.name}(id={acc.id}): stop bot")
                            self.tasks[acc.id].cancel()
                            del self.tasks[acc.id]
                            await cancel_all_orders_for_account(acc)

                    elif acc.status == AccountStatus.deleted:
                        if acc.id in self.tasks:
                            logger.info(f"{acc.name}(id={acc.id}): delete bot")
                            self.tasks[acc.id].cancel()
                            del self.tasks[acc.id]
                            # Не отменяем ордера

                # Убираем завершённые задачи, если аккаунт больше не running
                for acc_id in list(self.tasks):
                    if acc_id not in running_ids:
                        logger.info(f"{acc.name}(id={acc.id}): delete task")
                        self.tasks[acc_id].cancel()
                        del self.tasks[acc_id]

            await asyncio.sleep(10)
