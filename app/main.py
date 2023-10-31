import json
import logging
import os
from bson import ObjectId


from fastapi import FastAPI, Request, WebSocket
from starlette.websockets import WebSocketDisconnect

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from motor.motor_asyncio import AsyncIOMotorClient


_logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='/code/app/templates')

# Retrieve MongoDB credentials from environment variables
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_DB = os.getenv("MONGO_DB")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# MongoDB connection settings
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
DATABASE = MONGO_DB

# Connect to the MongoDB database
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE]

# create two collections: messages and clients
messages_collection = db['messages']
clients_collection = db['clients']

# Maintain a list of connected clients
frontend_clients = {}

# Password to authenticate the clients
WEBSOCKET_CLIENT_PASSWORD = os.getenv("WEBSOCKET_CLIENT_PASSWORD")


@app.get("/")
@app.get("/messages")
async def root(request: Request):
    clients = []
    for client in await clients_collection.find().to_list(None):
        message_count = await messages_collection.count_documents({
            'client': str(client['_id']),
        })
        clients.append({
            'id': str(client['_id']),
            'name': client['name'],
            'message_count': message_count,
        })
    return templates.TemplateResponse(
        'clients.html', {
            'request': request,
            'active_messages': True,
            'clients': clients,
        },
    )


@app.delete("/messages/{client_id}")
async def delete_messages(client_id: str):
    client_id = ObjectId(client_id)
    await messages_collection.delete_many({
        'client': str(client_id),
    })
    return {
        'status': 'OK',
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            # differentiate between frontend and backend clients
            if data.get('type', '') == 'ui-client':
                frontend_clients[data['uuid']] = websocket
            elif (
                data.get('type', '') == 'message'
                and data.get('auth', '') == WEBSOCKET_CLIENT_PASSWORD
                and data.get('name')
            ):
                # check if client names exists in the database
                client = await clients_collection.find_one({
                    'name': data['name'],
                })
                if client is None:
                    # create new client in database
                    result = await clients_collection.insert_one({
                        'name': data['name'],
                    })
                    client_id = result.inserted_id
                    # notify frontend clients to refresh page
                    for client in frontend_clients.values():
                        await client.send_text(json.dumps({
                            'type': 'refresh',
                        }))
                else:
                    client_id = client['_id']

                data.update({
                    'client_uuid': str(client_id),
                })

                # notify frontend clients
                for client in frontend_clients.values():
                    await client.send_text(json.dumps(data))

                # save data in database
                await messages_collection.insert_one({
                    'content': data['content'],
                    'client': str(client_id),
                })

                # notify back the sender
                await websocket.send_text(json.dumps({
                    'content': 'OK',
                }))
    except WebSocketDisconnect:
        _logger.info('...... Socket Connection closed.')
    except Exception as e:
        _logger.error('...... Internal Error: %s', e)


@app.get("/client/{client_id}/details")
async def client_details(client_id: str, request: Request):
    client_id = ObjectId(client_id)
    client_id = await clients_collection.find_one({
        '_id': client_id,
    })
    messages = await messages_collection.find({
        'client': str(client_id['_id']),
    }).to_list(None)
    return templates.TemplateResponse(
        'messages.html', {
            'request': request,
            'active_messages': True,
            'messages': messages,
            'client_id': client_id['_id'],
        },
    )
