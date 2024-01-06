import asyncio
import websockets
import socket               # 导入 socket 模块
 
async def main():
    async with websockets.connect("ws://192.168.100.78:8001/ws_test/") as websocket:
        while True:
            message = b'1'
            print(message)
            await websocket.send(message)
            print(f"Sent: {message}")

            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.run(main())