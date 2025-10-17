from app.database.models import async_session, User, Admin, Oper, Tip
from sqlalchemy import select, delete, update
from random import choice
from bot.config import TG_ADMIN

#               Работа с User

# Создание нового юзера
async def create_user(tg_id, name, iin):
    async with async_session() as s:
        user = await s.scalar(select(User).where(tg_id == tg_id))
        if not user:
            s.add(User(tg_id=tg_id, name=name, iin=iin))
            await s.commit()
            return user




# достать юзера
async def get_user(tg_id):
    async with async_session() as s:
        user = await s.scalar(select(User).where(tg_id == tg_id))
        if user:
            return user
        else:
            return None

# Проверка зареган юзер или нет
async def check_user(tg_id):
    async with async_session() as s:
        user = await s.scalar(select(User).where(tg_id == tg_id))
        if user:
            return True
        else:
            return False
        


#               Работа с админом

#  проверка админ ли юзер
async def is_admin(tg_id):
    async with async_session() as s:
        admin = await s.scalar(select(Admin).where(tg_id==tg_id))

        if admin:
            return True
        else:
            return False

# добовляем админа 
async def add_admin():
    async with async_session() as s:
        s.add(Admin(tg_id = TG_ADMIN))
        await s.commit()
        return True
#              Запросы Операторы

# добовляем оператора
async def add_oper_req(tg_id):
    async with async_session() as s:    
        oper = await s.scalar(select(Oper).where(tg_id == tg_id))

        if not oper:
            s.add(Oper(tg_id=tg_id))
            await s.commit()

#  проверка оператор или нет
async def is_oper(tg_id):
    async with async_session() as s:
        oper = await s.scalar(select(Oper).where(Oper.tg_id==tg_id))

        if oper:
            return True
        else:
            return False
        
# получаем всех оператаров
async def get_opers():
    async with async_session() as s:
        return await s.scalars(select(Oper))


async def create_tip():
    async with async_session() as s:
        tips = await s.scalar(select(Tip))
        if not tips:
            tips_obj = Tip()
            s.add(tips_obj)
            await s.commit()
            await s.refresh(tips_obj)
        return True

# получить совет
async def get_tip_req():
    async with async_session() as s:
        tips = await  s.scalar(select(Tip))
        if not tips:
            tips_obj = Tip()
            s.add(tips_obj)
            await s.commit()
            await s.refresh(tips_obj)
        tip = tips.tips.get('tips')

        return choice(tip)



# Добавить Совет (только для оперов)
async def add_tip_req(tip):
    async with async_session() as s:
        tips_obj =  await s.scalar(select(Tip).where(Tip.id == 1))
        if not tips_obj:
            tips_obj = s.add(Tip())
            await s.commit()

        tips_obj.tips = {"tips": tips_obj.tips["tips"] + [tip]}
        await s.commit()

        return True
        
