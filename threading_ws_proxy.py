import threading
import json
import asyncio
import websocket
import socket  

config = None
ws_server_entry_point = None
game_server_port = None
game_server_protrocl = None

socket_handle = None
websocket_handle = None

address = None


def udp2ws_handle(wait_ws:threading.Semaphore,wait_udp:threading.Semaphore):
    wait_ws.acquire()
    global socket_handle
    print('开始创建udp套接字')
    socket_handle = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    local_addr = ("", game_server_port)
    socket_handle.bind(local_addr)
    socket_handle.setblocking(True)
    print('套接字创建完成')
    wait_udp.release()
    print('开启socket2ws转发')
    global address
    while True:
        data,address = socket_handle.recvfrom(4096)
        print('msg of socket ---> ws:',data)
        websocket_handle.send_binary(data)


def ws2udp_handle(wait_ws:threading.Semaphore,wait_udp:threading.Semaphore):
    global websocket_handle
    websocket_handle = websocket.WebSocket()
    websocket_handle.connect(ws_server_entry_point)
    print('连接ws服务器端成功')
    wait_ws.release()
    wait_udp.acquire() #等待udp句柄创建
    print('开启ws2socket转发')
    global address
    while True:
        data_frame = websocket_handle.recv_frame()
        print('msg of ws ---> socket:',data_frame.data)
        socket_handle.sendto(data_frame.data,address)

def main():
    print('初始化ing')
    print('加载设置')
    with open('./config.json','r') as f:
        global config
        config = json.load(f)
    global ws_server_entry_point,game_server_port,game_server_protrocl
    ws_server_entry_point = config['ws_server_entry_point']
    game_server_port = config['game_server_port']
    game_server_protrocl = config['game_server_protrocl']
    print('加载设置完成')
    print('正在启动收发线程')
    if game_server_protrocl == 'udp':
        semp_wait_ws = threading.Semaphore(0)
        semp_wait_udp = threading.Semaphore(0)
        ws2udp = threading.Thread(target=ws2udp_handle,args=(semp_wait_ws,semp_wait_udp))
        udp2ws = threading.Thread(target=udp2ws_handle,args=(semp_wait_ws,semp_wait_udp))
        ws2udp.daemon = True
        udp2ws.daemon = True
        ws2udp.start()
        udp2ws.start()
    if game_server_protrocl == 'tcp':
        pass
    print('收发线程启动成功')
    while True:
        pass

if __name__ == '__main__':
    main()