import asyncio
import os
from functools import partial
from io import DEFAULT_BUFFER_SIZE
from os import listdir
from os.path import isfile, join
from pathlib import Path

import websockets


def read_file(file_name_read):
    path = os.getcwd()
    path = Path(path, 'file', file_name_read)
    with open(path, 'rb') as open_file:
        file = open_file.read()
    return file


def get_dir_files():
    path = os.getcwd()
    path = Path(path, 'file')
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    out_files_data = ''
    for file in onlyfiles:
        out_files_data += f'{file}={os.path.getsize(Path(path, file))}+'
    return out_files_data


def file_byte_iterator(path):
    path = Path(path)
    with path.open('rb') as file:
        reader = partial(file.read1, DEFAULT_BUFFER_SIZE)
        file_iterator = iter(reader, bytes())
        for chunk in file_iterator:
            for byte in chunk:
                yield byte


async def server(websocket, path):
    async for message in websocket:
        if len(message.split(';')) == 1:
            if message == 'get_list_files':
                await websocket.send(";".join(get_dir_files()))
            else:
                if message != 'None':
                    file = read_file(message)
                    await websocket.send(file)
                else:
                    await websocket.send('None')
        else:
            file = message.split(';')[0]
            chunk_size = message.split(';')[1]
            chunk_start = int(message.split(';')[2])
            chunk_end = int(message.split(';')[3])
            path = os.getcwd()
            path = Path(path, 'file', file)
            read_file = list(file_byte_iterator(path))
            if chunk_end > len(read_file):
                chunk_file = read_file[chunk_start:]
            else:
                chunk_file = read_file[chunk_start:chunk_end]
            await websocket.send(bytes(chunk_file))

async def main():
    host = '0.0.0.0'
    port = 8080
    async with websockets.serve(server, host, port):
        await asyncio.Future()  # run forever

asyncio.run(main())
