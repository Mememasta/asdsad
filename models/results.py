import asyncpgsa

from datetime import datetime
from models.db import results
from models.db import users
from models.db import projects

from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from sqlalchemy import (
            MetaData, Table, Column, ForeignKey,
                Integer, String, DateTime, Date, VARCHAR, desc
        )


class Result:

    @staticmethod
    async def create_result(db, score, gift):
        user_result = results.insert().values(score = score, gift = gift)
        await db.execute(user_result)

    @staticmethod
    async def get_all_result(db):
        all_result = await db.fetch(
            results.select()
        )
        return all_result
