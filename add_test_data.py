from src.auth.models import User, UserType
from src.database import engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async def main():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        user = User(
            username="admin",
            key="admin",
            type=UserType.admin,
            max_accounts_count=10000
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(user)
        
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())