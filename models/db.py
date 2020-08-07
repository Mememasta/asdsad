import asyncpgsa

from config.common import BaseConfig
from datetime import datetime

from sqlalchemy import (
        MetaData, VARCHAR, Table, Column, ForeignKey,
        Integer, String, DateTime, Boolean
        )
from sqlalchemy import select

metadata = MetaData()

users = Table(
    'users', metadata,

    Column('id', Integer, primary_key=True),
    Column('name', VARCHAR(255), nullable=False),
    Column('secondname', VARCHAR(255), nullable=False),
    Column('email', VARCHAR(255), unique=True, nullable=False),
    Column('phone', VARCHAR(255), unique=True, nullable=True),
    Column('birthday', VARCHAR(255), nullable=True),
    Column('occupation', VARCHAR(255), nullable=True),
    Column('city', VARCHAR(40), nullable=True),
    Column('password', VARCHAR(2048), nullable=False),
    Column('user_photo', VARCHAR(255), nullable=True)
)

projects = Table(
    'projects', metadata,

    Column('id', Integer, primary_key=True),
    Column('name', VARCHAR(255)),
    Column('company', VARCHAR(255)),
    Column('author_id', Integer, ForeignKey('users.id')),
    Column('description', VARCHAR(255)),
    Column('presentation', VARCHAR(255)),
    Column('deadline', DateTime(timezone=True), default=datetime.utcnow),
    Column('member', Integer),
    Column('gift', VARCHAR(255)),
    Column('video', VARCHAR(255)),
    Column('total', Boolean, default=False)

)

projects_user = Table(
    'projects_user', metadata,

    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

answer_user = Table(
    'answer_user', metadata,

    Column('answer_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('projects_id', Integer, ForeignKey('projects.id')),
    Column('answer', VARCHAR(2048)),

)

results = Table(
    'results', metadata,

    Column('result_id', Integer, primary_key=True),
    Column('answer_id', Integer, ForeignKey('answer_user.answer_id')),
    Column('score', Integer),
    Column('gift', VARCHAR(2048)),
)

async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = await asyncpgsa.create_pool(dsn = dsn)
    app['db'] = pool
    return pool

def construct_db_url(config):
    DSN = "postgresql://{host}:{port}/{datebase}?user={user}&password={password}"
    return DSN.format(
            user = config['DB_USER'],
            password = config['DB_PASS'],
            datebase = config['DB_NAME'],
            host = config['DB_HOST'],
            port = config['DB_PORT']
            )
