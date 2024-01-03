import json
import asyncio
import websockets
import socket  

config = None
with open('./config.json','r') as f:
    config = json.load(f)

ws_server_entry_point = config['ws_server_entry_point']
game_server_port = config['game_server_port']
game_server_protrocl = config['game_server_protrocl']

socket_handle = None
websocket_handle = None

async def socket2ws_handle(loop:asyncio.AbstractEventLoop,wait_ws:asyncio.Semaphore,wait_udp:asyncio.Semaphore):
    await wait_ws.acquire()
    global socket_handle
    if game_server_protrocl == 'udp':
        socket_handle = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        local_addr = ("", game_server_port)
        socket_handle.bind(local_addr)
    wait_udp.release()
    while True:
        data = await loop.sock_recv(socket_handle,1024)
        await websocket_handle.send(data)

async def ws2socket_handle(loop:asyncio.AbstractEventLoop,wait_ws:asyncio.Semaphore,wait_udp:asyncio.Semaphore):
    async with websockets.connect(ws_server_entry_point) as websocket:
        global websocket_handle
        websocket_handle = websocket
        wait_ws.release()
        await wait_udp.acquire() #等待udp句柄创建
        while True:
            data = await websocket.recv()
            await loop.sock_sendall(socket_handle,data)


def main():
    semp_wait_ws = asyncio.Semaphore(0)
    semp_wait_udp = asyncio.Semaphore(0)
    loop = asyncio.get_event_loop()
    loop.create_task(socket2ws_handle(loop=loop,wait_ws=semp_wait_ws,wait_udp=semp_wait_udp))
    loop.create_task(ws2socket_handle(loop=loop,wait_ws=semp_wait_ws,wait_udp=semp_wait_udp))
    loop.run_forever()


main()
