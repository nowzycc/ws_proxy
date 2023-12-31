import asyncio
import websockets
import socket               # 导入 socket 模块
 
async def main():
    async with websockets.connect("ws://192.168.100.78:8080/ws_test/") as websocket:
        s = socket.socket()         # 创建 socket 对象
        print(s.getblocking())
        host = socket.gethostname() # 获取本地主机名
        s.setblocking(True)
        port = 12345                # 设置端口
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
            print(f"Received: {response}")

asyncio.run(main())