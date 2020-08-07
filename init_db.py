import argparse

from config.common import BaseConfig
from datetime import datetime
from models.db import (
        users, projects, projects_user, results, answer_user, construct_db_url
        )
from sqlalchemy import create_engine, MetaData
from security import generate_password_hash

def setup_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']
    db_pass = target_config['DB_PASS']

    with engine.connect() as conn:
        teardown_db(executor_config = executor_config,
                     target_config = target_config)

        conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                      (db_name, db_user))

def get_engine(db_config):
    db_url = construct_db_url(db_config)
    engine = create_engine(db_url, isolation_level = "AUTOCOMMIT")
    return engine

def teardown_db(executor_config = None, target_config = None):
    engine = get_engine(executor_config)
    print(engine.connect())

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']

    with engine.connect() as conn:
        conn.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '%s'
              AND pid <> pg_backend_pid();""" % db_name)
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP ROLE IF EXISTS %s" % db_user)

def create_tables(target_config = None):
    engine = get_engine(target_config)

    metadata = MetaData()
    metadata.create_all(bind = engine, tables = [users, projects, projects_user, answer_user, results])

def create_sample_data(target_config=None):
    engine = get_engine(target_config)

    with engine.connect() as conn:
        conn.execute(users.insert(), [
            {
                'name': 'Nikita',
                'secondname': 'Russkih',
                'email': 'user@gmail.com',
                'phone': '89999999999',
                'birthday': '22.10.1999',
                'occupation': 'student',
                'city': 'SP',
                'password': generate_password_hash('8888')
            },
            {
                'name': 'Marat',
                'secondname': 'Chuchalov',
                'email': 'admin@gmail.com',
                'phone': '89999999990',
                'birthday': '13.04.1999',
                'occupation': 'stud',
                'city': 'Kazan',
                'password': generate_password_hash('123')
            }
        ])

        conn.execute(projects.insert(), [
            {
                'name': 'Двигатели',
                'company': 'Lada',
                'author_id': 1,
                'description': 'Создание машин',
                'presentation': 'None',
                'deadline': datetime.utcnow(),
                'member': 0,
                'gift': '100000',
                'total': False
            },
            {
                'name': 'Лодки',
                'company': 'BMW',
                'author_id': 2,
                'description': 'Создание лодок',
                'presentation': 'None',
                'deadline': datetime.utcnow(),
                'member': 0,
                'gift': '1000000',
                'total': False
            },
        ])

        conn.execute(projects_user.insert(), [
            {
                'user_id': 1,
                'project_id': 2
            },

            {
                'user_id': 2,
                'project_id': 1
            }
        ])

        conn.execute(answer_user.insert(), [
            {
                'user_id': 1,
                'project_id': 2,
                'answer': 'None'
            },

            {
                'user_id': 2,
                'project_id': 1,
                'answer': 'None'
            }
        ])

        conn.execute(results.insert(), [
            {
                'answer_id': 1,
                'score': 5,
                'gift': '0'
            },

            {
                'answer_id': 2,
                'score': 100,
                'gift': '10000000'
            }
        ])



def drop_tables(target_config = None):
    engine = get_engine(target_config)

    metadata = MetaData()
    metadata.drop_all(bind = engine, tables = [users, projects, projects_user, answer_user, results])

if __name__ == "__main__":
    user_db_config = BaseConfig.load_config('config/cloud_config.toml')['database']
    admin_db_config = BaseConfig.load_config('config/admin_config.toml')['database']
    print(user_db_config)
    print(admin_db_config)

    parser = argparse.ArgumentParser(description = "Ключи для работы с БД")
    parser.add_argument('-c', '--create', help = "Создать пустую бд и пользователя", action = 'store_true')
    parser.add_argument('-d', '--drop', help = "Удалить бд и роль пользователя", action = 'store_true')
    parser.add_argument('-r', '--recreate', help = "Удалить и пересоздать бд и пользователя", action = 'store_true')
    parser.add_argument('-a', '--all', help = "Создать образец", action = 'store_true')
    parser.add_argument('-v', '--virtual', help = "Заполнить виртуальный сервер данными", action='store_true')
    args = parser.parse_args()

    if args.create:
        setup_db(executor_config = admin_db_config,
                 target_config = user_db_config)
    elif args.drop:
        teardown_db(executor_config = admin_db_config,
                    target_config = user_db_config)
    elif args.recreate:
        teardown_db(executor_config = admin_db_config,
                    target_config = user_db_config)
        setup_db(executor_config = admin_db_config,
                 target_config = user_db_config)
    elif args.all:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
        create_tables(target_config=user_db_config)
        create_sample_data(target_config=user_db_config)
    elif args.virtual:
        create_tables(target_config=user_db_config)
        create_sample_data(target_config=user_db_config)
    else:
        parser.print_help()
