import asyncpgsa

from models.db import users
from sqlalchemy import (
            MetaData, Table, Column, ForeignKey,
                Integer, String, DateTime, Date, VARCHAR

        )
from sqlalchemy.sql import select


class User:

    @staticmethod
    async def get_all_users(db):
        # Вернет всех пользователей
        records = await db.fetch(
            users.select()
        )
        return records

    @staticmethod
    async def get_user_by_email(db, email):
        # Вернет пользователя по его почте
        user = await db.fetchrow(
            users.select().where(users.c.email == email)
        )
        if user:

            return user


    @staticmethod
    async def check_email(db, email):
        # Проверяет существует ли пользователь с такой почтой
        user = db.fetchrow(
            users.select().where(users.c.email == email)
        )
        if not user:
            return user

    @staticmethod
    async def get_user_by_id(db, user_id):
        # Вернет пользователя по id
        user = await db.fetchrow(
            users.select().where(users.c.id == user_id)
        )
        return user

    @staticmethod
    async def create_user(db, name, secondname, email, phone, birthday, occupation, city, password, user_photo):
        # Создаст пользователя
        new_user = users.insert().values(name = name, secondname = secondname, email = email, phone = phone, birthday = birthday, occupation = occupation, city = city, password = password, user_photo = user_photo)
        await db.execute(new_user)
