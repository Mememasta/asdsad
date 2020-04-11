from handlers.base import Index, Login, Signup, Logout, Profile, Projects, About, Contacts, CreateProjects, ViewProject, ViewGroup, WebSocket

from config.common import BaseConfig

from handlers.api import get_user, get_all_project, get_project_by_id, get_text

def setup_routes(app):
    app.router.add_get('/', Index.get, name='index')
    app.router.add_get('/login', Login.get, name='login')
    app.router.add_post('/login', Login.post)
    app.router.add_get('/signup', Signup.get, name='signup')
    app.router.add_post('/signup', Signup.post)
    app.router.add_get('/logout', Logout.get, name='logout')
    app.router.add_get('/profile', Profile.get, name='profile')
    app.router.add_get('/projects', Projects.get, name='userprojects')
    app.router.add_get('/ws', WebSocket.get, name='ws')
    app.router.add_get('/create_project', CreateProjects.get, name='create_project')
    app.router.add_post('/create_project', CreateProjects.post)
    app.router.add_get('/view', ViewProject.get, name='viewproject')
    app.router.add_post('/view', ViewProject.post)
    app.router.add_get('/view_group', ViewGroup.get, name='view_group')
    app.router.add_get('/about', About.get, name='about')
    app.router.add_get('/contacts', Contacts.get, name='contacts')

    app.router.add_get('/api/get_user', get_user, name='get_user')
    app.router.add_post('/api/get_project', get_project_by_id, name='get_project_by_id')
    app.router.add_get('/api/get_all_project', get_all_project, name='get_project')
    app.router.add_post('/api/get_text', get_text, name='get_text')
    

def setup_static_routes(app):
    app.router.add_static('/static/', path=BaseConfig.static_dir, name='static')
