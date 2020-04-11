import asyncpgsa
from sqlalchemy import (
            MetaData, Table, Column, ForeignKey,
                Integer, String, DateTime, Date, VARCHAR, desc
                
        )
from sqlalchemy.sql import select
from models.user import users
from datetime import datetime

metadata = MetaData()

projects = Table(
    'projects', metadata,

    Column('id', Integer, primary_key=True),
    Column('name', VARCHAR(255)),
    Column('company', VARCHAR(255)),
    Column('author_id', Integer),
    Column('description', VARCHAR(255)),
    Column('presentation', VARCHAR(255)),
    Column('deadline', DateTime(timezone=True), default=datetime.utcnow), 
    Column('member', Integer),
    Column('gift', VARCHAR(255)),
    Column('video', VARCHAR(255)),

)

projects_user = Table(
    'projects_user', metadata,

    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

class Project:

    @staticmethod
    async def get_all_projects(db):
        project = await db.fetch(
            projects.select().order_by(desc('member'))
        )
        return project

    @staticmethod
    async def get_top3_projects(db):
        project = await db.fetch(
            projects.select().order_by(desc('member')).limit(3)
        )
        return project

    @staticmethod
    async def get_project_by_id(db, project_id):
        project = await db.fetchrow(
           projects.select().where(projects.c.id == project_id)
        )
        return project
    
    @staticmethod
    async def get_project_that_user_created(db, user_id):
        project = await db.fetch(
            projects.select().where(projects.c.author_id == user_id)
        )
        return project

    @staticmethod
    async def get_project_by_userid(db, user_id):
        project = await db.fetch(
            "SELECT * FROM projects as p left join projects_user as pu ON p.id = pu.project_id WHERE pu.user_id = $1", user_id
        )
        return project

    @staticmethod
    async def create_project(db, name, company, author_id, description, presentation, deadline, member, gift, video):
        new_project = projects.insert().values(name = name, company = company, author_id = author_id, description = description, presentation = presentation, deadline = deadline, member = member, gift = gift, video = video)
        await db.execute(new_project)

    @staticmethod
    async def create_user_in_project(db, user_id, project_id):
        user_in_project = projects_user.insert().values(user_id = user_id, project_id = project_id)
        await db.execute(user_in_project)

    @staticmethod
    async def delete_user_in_project(db, user_id, project_id):
        user_in_project = projects_user.delete().values(user_id = user_id, project_id = project_id)

    @staticmethod
    async def user_in_project(db, user_id, project_id):
        user_in_project = await db.fetchrow(
                projects_user.select().where(projects_user.c.project_id == project_id, projects_user.c.user_id == user_id)
        )

        if user_in_project:
            return true

    @staticmethod
    async def add_members(db, member, project_id):
        await db.execute('UPDATE projects SET member = $1 where id = $2', member, project_id)

    @staticmethod
    async def del_members(db, member):
        await db.execute('UPDATE projects SET member = $1 where id = $2', member, project_id)
