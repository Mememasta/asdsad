import hashlib
import aiohttp_jinja2
import json
import os

from aiohttp import web
from aiohttp_session import get_session
from config.common import BaseConfig


from models.user import User
from models.projects import Project
from models.group import Group


class Index(web.View):

    @aiohttp_jinja2.template('base.html')
    async def get(self):
        conf = self.app['config']
        session = await get_session(self)
        user = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        return dict(user=user, conf=conf)

class Login(web.View):

    @aiohttp_jinja2.template('login.html')
    async def get(self):
        session = await get_session(self)
        user = {}
        conf = self.app['config']
        if 'user' in session:
            user = session['user']
            return dict(user = user, conf= conf)
        return dict(user = user, conf=conf)

    async def post(self):
        data = await self.post()
        session = await get_session(self)
        location = self.app.router['login'].url_for()
        email = data['email']
        password = data['password']
        user = await User.get_user_by_email(self.app['db'], email)
        print(user)
        print(password)
        if user['password'] == hashlib.sha256(password.encode('utf-8')).hexdigest():
            session['user'] = user['id']

            location = self.app.router['index'].url_for()

            return web.HTTPFound(location=location)

        return web.HTTPFound(location=location)


class Signup:

    @aiohttp_jinja2.template('sigup.html')
    async def get(self):
        session = await get_session(self)
        user = {}
        if 'user' in session:
            user = session['user']
        return dict(user=user)

    async def post(self):
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

        with open(os.path.join(BaseConfig.static_dir + '/photo/', user_photo.filename), 'wb') as f:
            avatar = user_photo.file.read()
            f.write(avatar)


        user_by_email = await User.get_user_by_email(self.app['db'], email)
        if user_by_email:
            return web.HTTPFound(location = location)

        if name and secondname and birthday and phone and occupation and city and password:
            data = dict(data)
            data['password'] = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
            user_photo = '/photo/{}'.format(user_photo.filename)
            password = data['password']

            result = await User.create_user(self.app['db'], name, secondname, email, int(phone), birthday, occupation, city, password, user_photo)
            location = self.app.router['login'].url_for()
            return web.HTTPFound(location=location)
        else:
            return dict(error='Missing user data parameters')

        


class Logout:

    async def get(self):
        session = await get_session(self)
        try:
            del session['user']
        except:
            pass
        location = self.app.router['index'].url_for()

        return web.HTTPFound(location = location)


class Profile:
    
    @aiohttp_jinja2.template('lk.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        user = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        return dict(config=config, user=user)

class UserProjects:

    @aiohttp_jinja2.template('myprojects.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        user = {}
        project = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
            project = await Project.get_project_by_userid(self.app['db'], user_id)
            
        return dict(config=config, user=user, project=project)
    
    async def post(self):
        pass

class CreateProjects:

    @aiohttp_jinja2.template('create_project.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        user = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        return dict(config = config, user = user)
    
    async def post(self):
        data = await self.post()
        location = self.app.router['create_project'].url_for()
        
        project_id = data['name']
        name = data['name']
        company = data['company']
        author_id = data['author_id']
        description = data['description']
        presentation = data['presentation']
        deadline = data['deadline']
        gift = data['gift']
        video = data['video']



        if name and company and author_id and description and presentation and deadline and gift and video:
    
                 
            with open(os.path.join(BaseConfig.static_dir + '/presentation/',  presentation.filename), 'wb') as f:
                file = presentation.file.read()
                f.write(file)
        
            with open(os.path.join(BaseConfig.static_dir + '/video/', video.filename), 'wb') as f:
                file = video.file.read()
                f.write(file)

            presentation = '/presentation/{}'.format(presentation.filename)
            video = '/video/{}'.format(video.filename)
            result = await Project.create_project(self.app['db'], name, company, int(author_id), description, presentation, deadline, gift, video)
            location = self.app.router['userprojects'].url_for()


        return web.HTTPFound(location)
        

class ViewProject:

    @aiohttp_jinja2.template('view_project.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        params = self.rel_url.query
        user = {}
        project = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        project = await Project.get_project_by_id(self.app['db'], int(params['project_id']))
        return dict(user = user, project = project)
    
    async def post(self):
        data = await self.post()
        
     
        user_id = data['user_id']
        project_id = data['project_id']
        project = await Project.get_project_by_id(self.app['db'], int(project_id))
        member = int(project['member']) + 1
        print('-------------------------------')
        print(member)
        url = '/view?project_id={}'.format(project_id)
        result = await Project.add_members(self.app['db'], member)

        return web.HTTPFound(url)
        

class Projects:

    @aiohttp_jinja2.template('projects.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        user = {}
        project = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        project = await Project.get_all_projects(self.app['db'])
        return dict(config=config, user=user, project = project)

class About:

    @aiohttp_jinja2.template('about_site.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['config']
        user = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        return dict(config=config, user=user)


class Contacts:

    @aiohttp_jinja2.template('contact.html')
    async def get(self):
        session = await get_session(self)
        config = self.app['db']
        user = {}
        if 'user' in session:
            user_id = session['user']
            user = await User.get_user_by_id(self.app['db'], user_id)
        return dict(config=config, user=user)

