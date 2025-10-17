from sqlalchemy import BigInteger, String, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase , Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker , create_async_engine
from bot.config import tips

engine = create_async_engine(url='sqlite+aiosqlite:///bot_db.sqlite3')

async_session = async_sessionmaker(engine)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)



class Oper(Base):
    __tablename__ = 'operators'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)   
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(50))
    iin: Mapped[int] = mapped_column()


class Tip(Base):
    __tablename__ = 'tips'
    id: Mapped[int] = mapped_column(primary_key=True)
    tips: Mapped[dict] = mapped_column(JSON,default= tips)

                                       






async def asyn_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)