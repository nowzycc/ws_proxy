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

async def main():
    async with websockets.connect(ws_server_entry_point) as websocket:
        s = socket.socket()         # 创建 socket 对象
        print(s.getblocking())
        host = socket.gethostname() # 获取本地主机名
        s.setblocking(True)
        port = game_server_port                # 设置端口
        s.bind((host, port))        # 绑定端口
        s.listen(5) 
        c,addr = s.accept()
        while True:
            data = c.recv(1500)
            message = data
            print(message)
            await websocket.send(message)
            print(f"Sent: {message}")
            response = await websocket.recv()
            c.send(response)
            print(f"Received: {response}")


asyncio.run(main())