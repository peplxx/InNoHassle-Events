import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, settings as config_settings
from src.repositories.event_groups import AbstractEventGroupRepository, SqlEventGroupRepository
from src.repositories.users import AbstractUserRepository, SqlUserRepository
from src.storages.sql import AbstractSQLAlchemyStorage, SQLAlchemyStorage


@pytest.fixture(scope="package")
def user_repository(storage) -> "AbstractUserRepository":
    return SqlUserRepository(storage)


@pytest.fixture(scope="package")
def storage(settings: "Settings") -> "AbstractSQLAlchemyStorage":
    _storage = SQLAlchemyStorage.from_url(settings.DB_URL.get_secret_value())
    return _storage


@pytest.fixture(scope="package")
def event_group_repository(storage) -> "AbstractEventGroupRepository":
    return SqlEventGroupRepository(storage)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_storage(storage: "AbstractSQLAlchemyStorage"):
    # Create the necessary tables before each test
    async with storage.create_session() as session:
        await _init_models(session)
        await session.commit()
    yield

    # Close the database connection after each test
    async with storage.create_session() as session:
        await _restore_session(session)
        await session.commit()
    await storage.close_connection()


async def _init_models(session: AsyncSession):
    from src.storages.sql.models.base import Base

    async with session.bind.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _restore_session(session: AsyncSession):
    from src.storages.sql.models.base import Base

    async with session.begin():
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())


@pytest.fixture(scope="package")
def settings() -> "Settings":
    return config_settings