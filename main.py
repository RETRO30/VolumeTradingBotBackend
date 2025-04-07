import asyncio
import uvicorn
from types import CoroutineType
from typing import List
from fastapi import FastAPI
from src.config import Config
from src.middlewares import SQLAlchemySessionMiddleware
from src.admin.middlewares import AdminMiddleware
from src.auth.middlewares import AuthMiddleware
from src.admin.routes import admin_router
from src.auth.routes import auth_router
from src.manage_accounts.routes import accounts_router

from src.service.manager import AccountManager

protected_app = FastAPI()
protected_app.add_middleware(AdminMiddleware)
protected_app.include_router(admin_router)

client_app = FastAPI()
client_app.add_middleware(AuthMiddleware)
client_app.include_router(accounts_router)


not_protected_app = FastAPI()
not_protected_app.include_router(auth_router)

app = FastAPI()
app.add_middleware(SQLAlchemySessionMiddleware)
app.mount("/protected", protected_app)
app.mount("/auth", not_protected_app)
app.mount("/client", client_app)


async def run_account_manager():
    manager = AccountManager()
    await manager.run()
    
async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
    


async def main():
    callable_tasks: List[CoroutineType] = [
        run_account_manager(),
        run_server()
    ]
    
    tasks = []
    for callable_task in callable_tasks:
        tasks.append(
            asyncio.create_task(callable_task)
        )
        
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())