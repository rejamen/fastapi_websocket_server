# Websocket Server based on FastApi

This project is a simple WebSocket server built with [FastAPI](https://fastapi.tiangolo.com/), a high-performance web framework designed for creating APIs in Python; and [MongoDB](https://www.mongodb.com/), a versatile, document-based database designed to meet the needs of modern application development and cloud-native architectures. 

The project is containerized using [Docker](https://www.docker.com/what-docker), which allows for the isolation of applications and their dependencies within lightweight containers, ensuring consistency and reproducibility across various environments.

## Installation

Set the IP_ADDRESS and PORT where your FastAPI app is running, in the file `/fastapi_websocket_server/app/templates/clients.html`
```bash
function setupWebSocket() {
            const serverIP = 'fastapi_ip_address';
            const serverPort = 'fastapi_port';
            ...
            
```

Change it to something like:
```bash
function setupWebSocket() {
            const serverIP = '192.168.2.23';
            const serverPort = '8000';
            ...
```
**Note:** You can find a better way to set these parameters, but for the purpose of this project, we will leave it like this. 

Create a `.env` file in the root directory and add the following environment variables:
```bash
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=socket-server
MONGO_USER=root
MONGO_PASSWORD=root-password
WEBSOCKET_CLIENT_PASSWORD=123456
WEBSOCKET_SERVER_IP_ADDRESS=<fastapi_ip_address>
WEBSOCKET_SERVER_PORT=8000
```
On the previous file, set the the WEBSOCKET_SERVER_IP_ADDRESS variable to your local IP address; where the FastApi app will be running. For example: `WEBSOCKET_SERVER_IP_ADDRESS=192.168.2.23`.

The WEBSOCKET_CLIENT_PASSWORD variable is used to ensure that the received messages include this password, otherwise the message will be rejected. It is recommended to use a strong password or to implement a more robust authentication mechanism. [Some documentation here](https://websockets.readthedocs.io/en/stable/topics/authentication.html).


After the `.env` file is created, run the following command to build the docker images and run the containers:
```bash
docker compose up
```

## Usage and Test
After the previous step, you can visit `http://<your_ip_address>:8000` to test the WebSocket server.

At first time, your page will be empty because there is no client connected to the server. 

To connect a client, you can use any websocket-client example; but you can start using the one provided in this project; on the file `websocket_client.py`

If you have a look to the code, you will se we are using some of the defined variables in the `.env` file. So, you need to install the `python-dotenv` package to be able to use them.

Run the following commands to install the needed package and to start a client:
```bash
pip3 install python-dotenv
python3 websocket_client.py
```

If you dont have any error, you should see the following output:
```bash
Sent: {'type': 'message', 'auth': '123456', 'name': 'Client 1', 'content': 'Hello World from Client 1'}
Received: {"content": "OK"}
```

And your App in the browser should refresh automatically and show the new connected client and the total of messages received.

![alt text](/docs/img/single_client.png)

**Note:** If the page is still empty, try to refresh it manually, and next received messages will update the counter automatically.

Click on the client card to go inside, and see the messages:

![alt text](/docs/img/messages.png)

### Adding more clients

To add more clients, you can run the `websocket_client.py` script and change the name of the client. Locate the following line and change the name, to `Client 2`
```bash
...
CLIENT_NAME = 'Client 1'
...
```
Run the script again and a 2nd client should appear now in the browser.

![alt text](/docs/img/clients.png)

**Note:** We are using only `name` to differentiate the clients. We suggest to use more robust identifiers, like a UUID.

### Run the App in several Browsers
As we are using websocket connections also to update the frontend App, it will work if you open the App in several browsers/devices. Sending messages from the websocket-client will update the counter in all the connected browsers.


