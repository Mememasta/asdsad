import asyncio
import aioreloader
import argparse
import aiohttp_jinja2
import asyncpgsa
import base64
import logging
import jinja2
import uvloop

from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from routes.base import setup_routes, setup_static_routes
from config.common import BaseConfig
from models.user import User
from models.db import init_db


log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='crowdsourcing project')
parser.add_argument('--host', help='Host to listen', default='0.0.0.0')
parser.add_argument('--port', help='Port to accept connections', default=8080)
parser.add_argument('--reload', action="store_true", help="AutoReload code on change")

parser.add_argument('-c', '--config', help="path to configuration file")

args = parser.parse_args()

async def current_user_ctx_proccessor(request):
    session = await get_session(request)
    user = None
    is_anonym = True
    if 'user' in session:
        user = session['user']
        user = await User.get_user_by_id(request.app['db'], user['id'])
        if user:
            is_anonym = not bool(user)
    return dict(current_user = user, is_anonym = is_anonym)

async def init_app():
    app = web.Application(debug=True, client_max_size=1024**5)
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

    db_pool = await init_db(app)

    log.debug(app['config'])

    if args.reload:
        print()
        print('-------------------------------------------------')
        print("Start with code reload")
        aioreloader.start()

    # app.on_startup.append(on_start)
    # app.on_cleanup.append(on_shutdown)
    return app


# async def on_start(app):
#     config = app['config']
#     app['db'] = await asyncpgsa.create_pool(dsn=config['database_url'])

# async def on_shutdown(app):
#     await app['db'].close()




#@sio.on('message', namespace='/projects')
#async def test_get(sid, message):
#    await sio.emit('response', {'projects': 'Left room: ' + message['room']})

def main():
    app = init_app()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, host=args.host, port=args.port)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
