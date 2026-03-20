from app.core.config import settings
from app.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.security import get_password_hash
from app.modules.user.crud import UserCrud

async def create_default_user(session: AsyncSession):
    user_crud = UserCrud(session)
    db_user =  await user_crud.get_by_email(settings.DEFAULT_USER_NAME)
    if db_user:
        return

    user = User(
        email=settings.DEFAULT_USER_NAME,
        hashed_password=get_password_hash(settings.DEFAULT_USER_PASSWORD),
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )
    await user_crud.create(user.model_dump())