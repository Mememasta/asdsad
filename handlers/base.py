import aiohttp_jinja2
import hashlib
import json
import os

from aiohttp import web
from aiohttp_session import get_session
from config.common import BaseConfig
from datetime import datetime
from security import check_password_hash
from models.user import User
from models.projects import Project
from models.group import Group
from models.results import Result

class Index(web.View):

    @aiohttp_jinja2.template('base.html')
    async def get(self):
        # Рендеринг главной страницы
        conf = self.app['config']
        session = await get_session(self)
        user = {}
        if 'user' in session:
            user = session['user']
        projects = await Project.get_top3_projects(self.app['db'])
        return dict(user = user, conf = conf, projects = projects)

class Login(web.View):

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        # Рендеринг страницы авторизации
        session = await get_session(self)
        context = {}
        if 'user' in session:
            location = self.app.router['index'].url_for()

            return web.HTTPFound(location = location)
        return dict()

    async def post(self):
        # Создание сессии
        data = await self.post()
        session = await get_session(self)
        location = self.app.router['login'].url_for()
        email = data['email']
        password = data['password']
        user = await User.get_user_by_email(self.app['db'], email)


        if user and check_password_hash(password, user['password']):
            session['user'] = dict(user)

            location = self.app.router['index'].url_for()

        return web.HTTPFound(location=location)


class Signup:

    @aiohttp_jinja2.template('sigup.html')
    async def get(self):
        # Рендеринг страницы регистрации
        session = await get_session(self)
        user = {}
        context = {}
        if 'user' in session:
            location = self.app.router['index'].url_for()

            return web.HTTPFound(location = location)
        return dict()

    async def post(self):
        # Создание нового пользователя
        data = await self.post()
        location = self.app.router['signup'].url_for()

        email = data['email']
        name = data['name']
        secondname = data['secondname']
        birthday = data['date']
        phone = data['phone']
        occupation = data['occupation']
        city = data['city']
        password = data['password']
        user_photo = data['user_photo']


        user_by_email = await User.check_email(self.app['db'], email)

        if name and secondname and email and password and not user_by_email:

            if user_photo:

                with open(os.path.join(BaseConfig.static_dir + '/photo/', user_photo.filename), 'wb') as f:
                    avatar = user_photo.file.read()
                    f.write(avatar)

                user_photo = '/photo/{}'.format(user_photo.filename)
            else:
                user_photo = None

            if phone:
                phone = int(phone)
            else:
                phone = None

            data = dict(data)
            data['password'] = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
            password = data['password']

            result = await User.create_user(self.app['db'], name, secondname, email, phone, birthday, occupation, city, password, user_photo)
            location = self.app.router['login'].url_for()
            return web.HTTPFound(location=location)
        else:
            return dict(error='Missing user data parameters')




class Logout:

    async def get(self):
        # Очистка сессии
        session = await get_session(self)

        if 'user' in session:
            try:
                del session['user']
            except:
                pass

        location = self.app.router['index'].url_for()

        return web.HTTPFound(location = location)



class Profile:

    @aiohttp_jinja2.template('lk.html')
    async def get(self):
        # Рендеринг страницы профиля
        session = await get_session(self)
        config = self.app['config']
        user = {}
        projects = {}
        project_that_user_created = {}
        dt = {}

        if 'user' in session:
            user = session['user']
            project_that_user_created = await Project.get_project_that_user_created(self.app['db'], user['id'])
            projects = await Project.get_project_by_userid(self.app['db'], user['id'])

        else:
            location = self.app.router['index'].url_for()

            return web.HTTPFound(location = location)

        for project in projects:
            if project['deadline']:
                dt = project['deadline']
                dt = datetime.strftime(dt, '%d %B %Y')

        for project in project_that_user_created:
            if project['deadline']:
                dt = project['deadline']
                dt = datetime.strftime(dt, '%d %B %Y')

        return dict(
                config=config,
                user=user,
                projects = projects,
                project_that_user_created = project_that_user_created
                   )




class SendAnswer:

    async def post(self):
        # Создание ответа пользователя
        session = await get_session(self)
        data = await self.post()

        if 'user' in session:
            user = session['user']
            projects_id = data['id']
            answer = data['answer']

            with open(os.path.join(BaseConfig.static_dir + '/answer/', answer.filename), 'wb') as f:
                file = answer.file.read()
                f.write(file)

            name = answer.filename
            answer = f"/answer/{name}"

            send_answer = await Project.create_answer(self.app['db'], user['id'], int(projects_id), answer)

        location = self.app.router['profile'].url_for()

        return web.HTTPFound(location)


class CreateProjects:

    @aiohttp_jinja2.template('create_project.html')
    async def get(self):
        # Рендеринг страницы с формой для создания проектов
        session = await get_session(self)
        config = self.app['config']
        user = {}

        if 'user' in session:
            user = session['user']
        else:
            location = self.app.router['index'].url_for()

            return web.HTTPFound(location = location)

        return dict(config = config, user = user)



    async def post(self):
        # Создание проекта
        data = await self.post()
        location = self.app.router['create_project'].url_for()

        name = data['name']
        company = data['company']
        author_id = data['author_id']
        description = data['description']
        presentation = data['presentation']
        deadline = data['deadline']
        member = 0
        gift = data['gift']
        video = data['video']

        dt = datetime.strptime(deadline, '%Y-%m-%d')
        print(name, company)
        print(dt)

        if name and company and author_id and description and presentation and deadline and gift:
            with open(os.path.join(BaseConfig.static_dir + '/presentation/', presentation.filename), 'wb') as f:
                file = presentation.file.read()
                f.write(file)

            if video:
                with open(os.path.join(BaseConfig.static_dir + '/video/', video.filename), 'wb') as f:
                    file = video.file.read()
                    f.write(file)

                presentation = '/presentation/{}'.format(presentation.filename)
                video = '/video/{}'.format(video.filename)
                result = await Project.create_project(self.app['db'], name, company, int(author_id), description, presentation, dt, member, gift, video)

            else:
                presentation = '/presentation/{}'.format(presentation.filename)
                video = ''
                result = await Project.create_project(self.app['db'], name, company, int(author_id), description, presentation, dt, member, gift, video)

            location = self.app.router['userprojects'].url_for()

        return web.HTTPFound(location)



class ViewProject:

    @aiohttp_jinja2.template('view_project.html')
    async def get(self):
        # Рендеринг страницы определенного проекта
        session = await get_session(self)
        config = self.app['config']
        params = self.rel_url.query
        user = {}
        project = {}
        user_in_project = {}
        answers = {}
        user_is_author = {}
        results = {}
        author_name = {}


        if 'user' in session:
            user = session['user']
            user_in_project = await Project.user_in_project(self.app['db'], user['id'], int(params['project_id']))

            user_is_author = await Project.user_is_author(self.app['db'], int(params["project_id"]), user['id'])
            if user_is_author:
                answers = await Project.get_all_answer(self.app['db'], int(params["project_id"]))
                results = await Result.get_all_result(self.app['db'])


        project = await Project.get_project_by_id(self.app['db'], int(params['project_id']))
        author_name = await User.get_user_by_id(self.app['db'], int(project['author_id']))

        if project['deadline']:
            dt = project['deadline']
            dt = datetime.strftime(dt, '%d %B %Y')

        print(project)

        return dict(user = user, project = project, author_name = author_name, dt=dt, user_in_project = user_in_project, user_is_author = user_is_author, answers = answers, results = results)

    async def post(self):
        # Участвовать/Покинуть проект
        data = await self.post()
        session = await get_session(self)

        user = session['user']
        project_id = data['project_id']
        project = await Project.get_project_by_id(self.app['db'], int(project_id))
        url = '/view?project_id={}'.format(project['id'])
        user_in_project = await Project.user_in_project(self.app['db'], user['id'], int(project['id']))
        user_is_author = await Project.user_is_author(self.app['db'], int(project['id']), user['id'])

        if not user_is_author:

            if user_in_project and 'user' in session:
                del_user_in_project = await Project.delete_user_in_project(self.app['db'], int(user_id), int(project['id']))

            else:
                add_user_in_project = await Project.create_user_in_project(self.app['db'], int(user_id), int(project['id']))

            new_member = await Project.add_members(self.app['db'], int(project_id))

        return web.HTTPFound(url)

class Results:

    @aiohttp_jinja2.template('results.html')
    async def get(self):
        # Рендеринг страницы с законченными проектами
        session = await get_session(self)
        user = {}
        total_projects = {}

        if 'user' in session:
            user = session['user']
            total_projects = await Project.get_total_project(self.app['db'])
        return dict(user = user, total_projects = total_projects)

    async def post(self):
        # Добавление проектов в список истекших
        session = await get_session(self)
        user = session['user']
        data = await self.post()
        location = self.app.router['viewproject'].url_for()
        user_is_author = await Project.user_is_author(self.app['db'], int(data['project_id']), user['id'])

        if data['project_id'] and user_is_author:
            project = await Project.get_projects_by_id(self.app['db'], int(data['project_id']))

            add_total = Project.add_total(self.app['db'], int(data['project_id']))
            location = self.app.router['results'].url_for()
            return web.HTTPFound(location = location)

        return web.HTTPFound(location = location)

class CreateResult:

    async def post(self):
        # Создание результатов по проекту
        data = await self.post()
        session = await get_session(self)
        score = data['score']
        gift = data['gift']
        location = self.app.router['view_project'].url_for()

        if score and gift:
            result = Result.create_result(self.app['db'], int(score), gift)
            return web.HTTPFound(location = location)


        return web.HTTPFound(location = location)

class Projects:

    @aiohttp_jinja2.template('projects.html')
    # Рендеринг страницы со всеми проектами
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        user = {}
        project = {}

        if 'user' in session:
            user = session['user']

        project = await Project.get_all_projects(self.app['db'])

        return dict(config=config, user=user, project = project)
class About:

    @aiohttp_jinja2.template('about_site.html')
    async def get(self):
        # Рендеринг страницы описания о сайте
        session = await get_session(self)
        config = self.app['config']
        user = {}

        if 'user' in session:
            user = session['user']

        return dict(config=config, user=user)

class Contacts:

    @aiohttp_jinja2.template('contact.html')
    async def get(self):
        # Рендеринг страницы с контактами
        session = await get_session(self)
        config = self.app['db']
        user = {}

        if 'user' in session:
            user = session['user']

        return dict(config=config, user=user)
