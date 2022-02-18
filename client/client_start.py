import math
import os
import threading
from pathlib import Path

from websocket import create_connection


def fun(arg, name=None, chunk=0, size=0):
    try:
        ws = create_connection("ws://0.0.0.0:8080")
        if chunk == 0 or chunk > int(size[arg - 1]):
            ws.send(name[arg - 1])
            file_in = ws.recv()
            if file_in != 'None':
                ws.close()
                f = open(name[arg - 1], 'wb')
                f.write(file_in)
                f.close()
            else:
                ws.close()
        else:
            if name[arg - 1] == 'None':
                ws.close()
            else:
                file_data = []
                for file_part in range(math.ceil(int(size[arg - 1]) / chunk)):
                    ws.send(f'{name[arg - 1]};'
                            f'{chunk};'
                            f'{file_part * chunk};'
                            f'{(file_part + 1) * chunk - 1}')
                    file_data.append(ws.recv())
                ws.close()
                path = os.getcwd()
                path = Path(path, 'file', name[arg - 1])
                file = open(path, "wb")
                for element in file_data:
                    file.write(bytes(element))
                file.close()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    with open('config.cfg', 'r') as open_file:
        config = open_file.read()
    open_file.close()
    threads_limit = int(config.split()[0].replace('treads=', ''))
    chunk = int(config.split()[1].replace('chunk_size=', ''))
    ws = create_connection("ws://0.0.0.0:8080")
    ws.send('get_list_files')
    file_data = ws.recv().replace(";", "").split('+')
    file_list = [(i.split('=')[0]) for i in file_data if len(i) > 0]
    file_size = [(i.split('=')[1]) for i in file_data if len(i) > 0]
    print('File name, file size')
    [print(f'{file_list[i]}, {file_size[i]}') for i in range(len(file_list))]
    ws.close()
    file_dict = {'name': file_list}

    try:
        element_in_step = math.ceil(len(file_list) / threads_limit)
        step = int(math.ceil(len(file_list) / element_in_step))
        file_dict_download = {}
        for thread_number in range(threads_limit):
            for element in range(element_in_step):
                if (element + 1) * step > len(file_list):
                    dict_element = file_list[element * step:]
                    dict_element_size = file_size[element * step:]
                    if len(dict_element) != len(file_list):
                        while len(dict_element) != step:
                            dict_element.append('None')
                        file_dict_download['name'] = dict_element
                        file_dict_download['size'] = dict_element_size
                    else:
                        file_dict_download['name'] = dict_element
                        file_dict_download['size'] = dict_element_size
                else:
                    file_dict_download['name'] = file_list[element * step:(element + 1) * step]
                    file_dict_download['size'] = file_size[element * step:(element + 1) * step]
                file_dict_download['chunk'] = chunk
                thread = threading.Thread(target=fun, args=(thread_number,), kwargs=file_dict_download)
                thread.start()

    except Exception as e:
        print(e)
