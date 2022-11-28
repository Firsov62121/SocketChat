#!/usr/bin/env python3
import socket
import select
import json
import os
import tkinter as tk
from dotenv import load_dotenv
import sys

load_dotenv()
HOST = os.getenv('SERVER_HOST')
PORT = int(os.getenv('SERVER_PORT'))
MAX_MESSAGE_SIZE = int(os.getenv('MAX_MESSAGE_SIZE_CLIENT'))
COUNT_OF_MESSAGES = int(os.getenv('COUNT_OF_MESSAGES'))
TIME_DELAY = int(os.getenv('TIME_DELAY'))

conn = None


def try_connect():
    global conn
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((HOST, PORT))
    except ConnectionError:
        return False
    return True


if not try_connect():
    print("Server unavailable")
    sys.exit(0)

messages = []


def send_message(message):
    request = json.dumps({'type': 'addMessage', 'message': message})
    conn.send(request.encode('utf8'))


def send_username(name):
    request = json.dumps({'type': 'setName', 'name': name})
    conn.send(request.encode('utf8'))


def message_to_str(message):
    return f"{message['username']}: {message['text']}"


def get_messages_str():
    return "\n".join(map(message_to_str, messages))


window = tk.Tk()
window.title("Чат")

username_label = tk.Label(text="Ваше имя")
username_label.grid(row=0, column=1)
username_entry = tk.Entry(window, width=50)
username_entry.grid(row=0, column=0)

message_entry = tk.Entry(window, width=50)
message_entry.grid(row=1, column=0)
messages_widget = tk.Label(window, height=20)
messages_widget.grid(row=2, column=0, columnspan=2)
messages_widget.config(text=get_messages_str())


def onclick_send(event):
    send_message(message_entry.get())
    message_entry.delete(0, tk.END)


def onclick_setname(event):
    send_username(username_entry.get())
    username_entry.delete(0, tk.END)


message_entry.bind('<Return>', onclick_send)

button = tk.Button(window, text="Отправить")
button.bind('<Button-1>', onclick_send)
button.grid(column=1, row=1)
username_entry.bind('<Return>', onclick_setname)


def read_messages_from_socket():
    global messages
    messages = json.loads(conn.recv(MAX_MESSAGE_SIZE).decode('utf8'))
    messages_widget.config(text=get_messages_str())


def get_last_messages(n=COUNT_OF_MESSAGES):
    global messages, conn
    request = json.dumps({'type': 'getLastMessages', 'size': n})
    conn.send(request.encode('utf8'))
    read_messages_from_socket()


def redraw_messages():
    try:
        ready_to_read, ready_to_write, in_error = \
            select.select([conn, ], [conn, ], [], 5)
        if len(ready_to_write) > 0:
            get_last_messages()
            window.after(TIME_DELAY, redraw_messages)
    except Exception as e:
        # 0 = done receiving, 1 = done sending, 2 = both
        conn.shutdown(2)
        conn.close()
        window.quit()


window.after(100, redraw_messages)

try:
    window.mainloop()
except:
    print("you pressed control c")
    sys.exit(0)
