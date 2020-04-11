import hashlib
import aiohttp_jinja2
import json
import os

from datetime import datetime

from aiohttp import web
from aiohttp_session import get_session
from config.common import BaseConfig


from models.user import User
from models.projects import Project
from models.group import Group


async def get_user(request):
    session = await get_session(request)

    try:
        user = await User.get_user_by_id(request.app['db'], session['user'])
        user = dict(user)
        user.pop('password')
        data = {'status': 200, 'response': []}
        data['response'].append(user)
    except Exception as e:
        data = {'status': 'failed', 'error': str(e)}
        

    return web.json_response(data)

async def get_project_by_id(request):
    data = await request.post()
    
    project_id = data['text']
    data = data
    print(data)

    try:
        project = await Project.get_project_by_id(request.app['db'], int(project_id))
        project = dict(project)
        project['deadline'] = str(project['deadline'])
        data = {
	
                "blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
                                "text": "Название: " + project['name']
			}
		},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Компания: " + project['company']

                    }
                },
		{
			"type": "section",
			"block_id": "section567",
			"text": {
				"type": "mrkdwn",
                                "text": "<https://dilabmining.ru/view?project_id=" + str(project['id']) + "|project_id: " + str(project['id']) +"> \n" + "Описание: " + project['description']
			}
                },
		{
		    "type": "section",
		    "text": {
                        "type": "mrkdwn",
                        "text": "https://dilabmining.ru/static" + project['video']
                    }
                },
		
                {	
                    "type": "section",
		    "block_id": "section789",
			"fields": [
				{
					"type": "mrkdwn",
                                        "text": "Members: " + str(project['member'])
				}
			]
		}
	    ]
	}

    except Exception as e:
        data = {'status': 'failed', 'error': str(e)}

    return web.json_response(data)


async def get_all_project(request):
    
    try:
        projects = await Project.get_all_projects(request.app['db'])
        data = {}
        data['response'] = []
        for project in projects:
            
            project = dict(project)
            project['deadline'] = str(project['deadline'])

            data['response'].append(project)

    except Exception as e:
        data = {'status': 'failed', 'error': str(e)}

    return web.json_response(data)

async def get_text(request):
    payload = {'text': 'Slack slash command is successful!'}
    return web.json_response(payload)

