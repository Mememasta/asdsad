import asyncpgsa
from sqlalchemy import (
            MetaData, Table, Column, ForeignKey,
                Integer, String, DateTime, Date, VARCHAR
                
        )
from sqlalchemy.sql import select

metadata = MetaData()



groups = Table(
    'groups', metadata,
     
    Column('id', Integer, primary_key=True),
    Column('name', VARCHAR(255)),
    Column('author_id', Integer),
    Column('commander', Integer)
)

class Group:

    @staticmethod
    async def get_all_groups(db):
        group = await db.fetch(
            groups.select()
        )
        return group
    
    @staticmethod
    async def get_groups_by_id(db, groups_id):
        group = await db.fetchrow(
            groups.select().where(groups.c.id == groups_id)
        )
        return group

    @staticmethod
    async def create_group(db, author_id, commander):
        result = groups.insert().values(
            author_id = author_id, commander = author_id
        )
        await db.execute(result)
