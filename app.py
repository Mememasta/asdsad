from aiohttp import web 
import argparse
import asyncio
import base64
import logging
import aiohttp_jinja2
import jinja2
import asyncpgsa

import aioredis
import aioreloader
import uvloop

from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from routes.base import setup_routes, setup_static_routes
from config.common import BaseConfig

from models.user import User

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
parser = argparse.ArgumentParser(description='project')
parser.add_argument('--host', help='Host to listen', default='0.0.0.0')
parser.add_argument('--port', help='Port to accept connections', default=8080)
parser.add_argument('--reload', action="store_true", help="AutoReload code on change")

parser.add_argument('-c', '--config', type=argparse.FileType('r'), help="path to configuration file")

args = parser.parse_args()

async def current_user_ctx_proccessor(request):
    session = await get_session(request)
    user = None
    is_anonym = True
    if 'user' in session:
        user_id = session['user']
        user = await User.get_user_by_id(request.app['db'], user_id)
        if user:
            is_anonym = not bool(user)
    return dict(current_user = user, is_anonym = is_anonym)
        
async def init_app():
    
    app = web.Application(client_max_size=1024**5)
    secret_key = base64.urlsafe_b64decode(BaseConfig.secret_key)
    setup(app, EncryptedCookieStorage(secret_key))

    aiohttp_jinja2.setup(
            app,
            loader=jinja2.PackageLoader(package_name='app', package_path='templates'),
                context_processors=[current_user_ctx_proccessor]
            
            )

    setup_routes(app)
    setup_static_routes(app)

    config = BaseConfig.load_config(args.config)
    app['config'] = config 

    if args.reload:
        print()
        print('-------------------------------------------------')
        print("Start with code reload")
        aioreloader.start()

    app.on_startup.append(on_start)   
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    config = app['config']
    app['db'] = await asyncpgsa.create_pool(dsn=config['database_url'])

async def on_shutdown(app):
    await app['db'].close()


def main():
    app = init_app()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
