import asyncpgsa


from datetime import datetime
from models.db import projects, projects_user, answer_user
from models.user import users
from sqlalchemy import (
            MetaData, Table, Column, ForeignKey,
                Integer, String, DateTime, Date, VARCHAR, desc, Boolean, update

        )
from sqlalchemy.sql import select
from sqlalchemy.orm import relationship


class Project:

    @staticmethod
    async def get_all_projects(db):
        # Вернуть все проекты
        project = await db.fetch(
            projects.select().where(projects.c.deadline > datetime.utcnow()).where(projects.c.total == False).order_by(desc('member'))
            # "SELECT * FROM projects as p LEFT JOIN projects_summary as p_s ON p_s.project_id = p.id WHERE p.deadline > $1 AND p_s.total = False ORDER BY member", datetime.utcnow()
        )
        return project

    @staticmethod
    async def get_total_project(db):
        # Вернуть все законченные проекты
        project = await db.fetch(
            projects.select().where(projects.c.deadline < datetime.utcnow()).where(projects.c.total == True).order_by(desc('member'))
        )
        return project

    @staticmethod
    async def add_total(db, project_id):
        # Изменить проект, сделав его оконченным
        # total = projects.update().where(projects.c.id == project_id).values(total = 'True')
        await db.execute('UPDATE projects SET total = True WHERE id = $1', project_id)

    @staticmethod
    async def get_projects_by_id(db, project_id):
        # Вернуть проект по id, которые валидны по времени
        project = await db.fetchrow(
            projects.select().where(projects.c.deadline > datetime.utcnow()).where(projects.c.id == project_id)
        )
        return project

    @staticmethod
    async def get_top3_projects(db):
        # Вернуть 3 проекта по количеству участников
        project = await db.fetch(
            projects.select().order_by(desc('member')).limit(3)
        )
        return project

    @staticmethod
    async def get_project_by_id(db, project_id):
        # Вернуть проект с пользователем, который его создал по id проекта
        project = await db.fetchrow(
           #projects.select().join(users).filter(users.id == projects.author_id).where(projects.c.id == project_id)
           "SELECT p.*, u.name user_id FROM projects as p left join users as u ON p.author_id = u.id where p.id = $1", project_id
        )
        return project

    @staticmethod
    async def get_project_that_user_created(db, user_id):
        # Вернуть проект по его автору
        project = await db.fetch(
            projects.select().where(projects.c.author_id == user_id)
        )
        return project

    @staticmethod
    async def get_project_by_userid(db, user_id):
        # Вернуть проект по id пользователя
        project = await db.fetch(
            "SELECT * FROM projects as p left join projects_user as pu ON p.id = pu.project_id left join answer_user as au ON pu.project_id = au.projects_id WHERE pu.user_id = $1 AND p.deadline > $2",
            user_id,
            datetime.utcnow()
        )
        return project

    @staticmethod
    async def create_project(db, name, company, author_id, description, presentation, deadline, member, gift, video):
        # Создать проект
        new_project = projects.insert().values(name = name, company = company, author_id = author_id, description = description, presentation = presentation, deadline = deadline, member = member, gift = gift, video = video)
        await db.execute(new_project)

    @staticmethod
    async def create_user_in_project(db, user_id, project_id):
        # Добавить участника в проект
        user_in_project = projects_user.insert().values(user_id = user_id, project_id = project_id)
        await db.execute(user_in_project)

    @staticmethod
    async def delete_user_in_project(db, user_id, project_id):
        # Удалить участника из проекта
        user_in_project = projects_user.delete().where(projects_user.c.user_id == user_id).where(projects_user.c.project_id == project_id)
        await db.execute(user_in_project)

    @staticmethod
    async def user_in_project(db, user_id, project_id):
        # Вернуть True, если пользователь участвует в проекте
        user_in_project = await db.fetchrow(
                projects_user.select().where(projects_user.c.project_id == project_id).where(projects_user.c.user_id == user_id)
        )

        if user_in_project:
            return True

    @staticmethod
    async def user_send_answer(db, user_id, project_id):
        # Вернуть True, если пользователь отправил ответ на проект
        user = await db.fetchrow(
                answer_user.select().where(answer_user.c.projects_id == project_id).where(answer_user.c.user_id == user_id)
        )
        if user:
            return True

    @staticmethod
    async def user_is_author(db, project_id, user_id):
        # Вернуть True если пользователь автор проекта
        user_is_author = await db.fetchrow(
                projects.select().where(projects.c.id == project_id).where(projects.c.author_id == user_id)
        )

        if user_is_author:
            return True

    @staticmethod
    async def add_members(db, project_id):
        # Добавить одного участника проекта
        member = len(await db.fetch(
            projects_user.select().where(projects_user.c.project_id == project_id)
            ))
        await db.execute('UPDATE projects SET member = $1 where id = $2', member, project_id)

    @staticmethod
    async def del_members(db, member):
        # Удалить участника из проектов
        await db.execute('UPDATE projects SET member = $1 where id = $2', member, project_id)

    @staticmethod
    async def create_answer(db, user_id, projects_id, answer):
        # Создаст ответ на проект по его id
        user_answer = answer_user.insert().values(user_id = user_id, projects_id = projects_id, answer = answer)
        await db.execute(user_answer)

    @staticmethod
    async def get_all_answer(db, project_id):
        # Вернет все ответы на проект по его id
        all_answer = await db.fetch(
            #answer_user.select().where(answer_user.c.projects_id == project_id)
            "SELECT a_u.*, u.name, u.secondname FROM users as u LEFT JOIN answer_user as a_u ON a_u.user_id = u.id WHERE a_u.projects_id = $1", project_id
        )
        return all_answer
