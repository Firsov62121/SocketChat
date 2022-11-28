#!/usr/bin/env python3
import asyncio
import socket
import json
import os
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('SERVER_HOST')
PORT = int(os.getenv('SERVER_PORT'))
MAX_MESSAGE_SIZE = int(os.getenv('MAX_MESSAGE_SIZE_SERVER'))
DEBUG = os.getenv('DEBUG') == "True"

usernames = []
all_messages = []
max_id = 0


def message_to_dict(id, message):
    name = None
    result = {"text": message[1]}
    if id == message[0]:
        name = "Вы"
    elif usernames[message[0]]:
        name = usernames[message[0]]
    else:
        name = f"User №{message[0]}"
    return {"text": message[1], "username": name}


def handle_request(id, request):
    global all_messages
    request = json.loads(request)
    if request["type"] == "exit":
        return ["op", "close"]
    if request["type"] == "getLastMessages":
        n = min(len(all_messages), max(0, int(request["size"])))
        result = list(
            map(lambda s: message_to_dict(id, s), all_messages[-n:]))
        return ["info", json.dumps(result)]
    if request["type"] == "addMessage":
        all_messages.append([id, request["message"]])
    elif request["type"] == "setName":
        usernames[id] = request["name"]


async def handle_client(client, id):
    loop = asyncio.get_event_loop()
    request = None
    while True:
        request = (await loop.sock_recv(client, MAX_MESSAGE_SIZE)).decode("utf8")
        if not request:
            break
        if DEBUG:
            print("request = ", request)
        try:
            response = handle_request(id, request)
            if response:
                if response[0] == "op":
                    if response[1] == "close":
                        break
                elif response[0] == "info":
                    response[1] = response[1].encode("utf8")
                    if DEBUG:
                        print(f"Sending to {id}: {response[1]}")
                    await loop.sock_sendall(client, response[1])
        except Exception as e:
            print(e)
        if DEBUG:
            print(all_messages)
    client.close()


async def run_server():
    global max_id
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(8)
    server.setblocking(False)

    loop = asyncio.get_event_loop()
    print("Server started on port: ", PORT)
    try:
        while True:

            client, _ = await loop.sock_accept(server)
            loop.create_task(handle_client(client, max_id))
            print(f"new client with id = {max_id}")
            usernames.append(None)
            max_id += 1
    except KeyboardInterrupt:
        server.close()

asyncio.run(run_server())
