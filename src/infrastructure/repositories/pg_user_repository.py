from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.database.models import UserModel


class PostgreSQLUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, email: str, hashed_password: str) -> UserModel:
        user = UserModel(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> UserModel:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
