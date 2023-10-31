import asyncio
import json
import os
import websockets

from dotenv import load_dotenv
load_dotenv()

WEBSOCKET_CLIENT_PASSWORD = os.getenv('WEBSOCKET_CLIENT_PASSWORD')
WEBSOCKET_SERVER_IP_ADDRESS = os.getenv('WEBSOCKET_SERVER_IP_ADDRESS')
WEBSOCKET_SERVER_PORT = os.getenv('WEBSOCKET_SERVER_PORT')
CLIENT_NAME = 'Client 2'


async def connect_to_websocket_server():
    """Send Message to Websocket Server.
    """
    uri = f"ws://{WEBSOCKET_SERVER_IP_ADDRESS}:{WEBSOCKET_SERVER_PORT}/ws"
    async with websockets.connect(uri) as websocket:
        message = {
            'type': 'message',
            'auth': WEBSOCKET_CLIENT_PASSWORD,
            'name': CLIENT_NAME,
            'content': f'Hello World from {CLIENT_NAME}',
        }
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Sent: {message}")
        print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(connect_to_websocket_server())
