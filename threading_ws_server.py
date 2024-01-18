import sys
import json
from  websockets.sync.server import serve
import socket
import threading

def listen_udp(sock,websocket):
    print('udp 线程启动')
    while True:
        data,server = sock.recvfrom(1024)
        print('msg of socket ---> ws:',data)
        # await websocket.send(data)
        websocket.send(data)

def ws2socket(websocket):
    print('收到连接',websocket.remote_address)
    global config
    dport = config['game_server_port']
    sport = websocket.remote_address[1]
    dst = config['game_server_ip']
    src = websocket.remote_address[0]
    sock = None
    if config['game_server_protrocl'] == 'udp':
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        # asyncio.get_event_loop().create_task(listen_udp(sock,websocket))
        listen_threading = threading.Thread(target=listen_udp,args=(sock,websocket))
        listen_threading.daemon = True
        listen_threading.start()
    while True:
        data = websocket.recv()
        print('msg of ws ---> socket:',data)
        # pkt = IP(src='127.0.0.1', dst=dst)/UDP(dport=dport,sport=sport)/data
        # send(pkt)
        sock.sendto(data,(dst,dport))

def main():
    app_name = sys.argv[1]
    global config
    with open('./server_config.json','r') as f:
        config = json.load(f)
    config = config[app_name]
    print(config)
    with serve(ws2socket,"192.168.100.77", 9999,open_timeout=180) as server:
        server.serve_forever()

main()