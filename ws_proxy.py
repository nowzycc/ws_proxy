import copy
import threading
import socket
import websockets.sync.client
import json

class ws_proxy:
    def __init__(self,name) -> None:
        self.name = name
        self.proxy_address_list = []
        self.proxy_resource_dict = {}

    def __heartbeat_handle(self,resource_key,sleep_time):
        pass

    def __init_proxy_resource_dict(self,proxy_port,proxy_protocol):
        self.proxy_resource_dict[(proxy_port,proxy_protocol)] = {
            "websocket_handle":None,
            'entry_point':None,
            "socket_handle":None,
            'work_mode':None,
            "threading_handles":{

            },
            "semps":{
                
            }
        }

    def __get_proxy_resource_dict(self,proxy_port,proxy_protocol):
        return self.proxy_resource_dict[(proxy_port,proxy_protocol)]

    def init_proxy(self,proxy_port,proxy_protocol,work_mode):
        self.proxy_address_list.append((proxy_port,proxy_protocol))
        self.__init_proxy_resource_dict(proxy_port,proxy_protocol)
        if work_mode == 'sync_thread':
            self.__init_proxy_with_sync_thread(proxy_port,proxy_protocol)
        if work_mode == 'sync_process':
            pass
        if work_mode == 'async':
            self.__init_proxy_with_async(proxy_port,proxy_protocol)

    def __init_proxy_with_sync_thread(self,proxy_port,proxy_protocol):
        resource_dict = self.__get_proxy_resource_dict(proxy_port,proxy_protocol)
        resource_dict['workmode']
        resource_dict['semps']['wait_ws'] = threading.Semaphore(0)
        resource_dict['semps']['wait_sock'] = threading.Semaphore(0)
        if proxy_protocol == 'udp':
            resource_dict['threading_handles']['udp2ws_handle'] = threading.Thread(target=self.__udp2ws_handle,args=((proxy_port,proxy_protocol)))
            resource_dict['threading_handles']['ws2udp_handle'] = threading.Thread(target=self.__ws2udp_handle,args=((proxy_port,proxy_protocol)))
            resource_dict['threading_handles']['heartbeat'] = threading.Thread(target=self.__heartbeat_handle,args=((proxy_port,proxy_protocol),10))
        if proxy_protocol == 'tcp':
            resource_dict['threading_handles']['udp2ws_handle'] = threading.Thread(target=self.__tcp2ws_handle,args=((proxy_port,proxy_protocol)))
            resource_dict['threading_handles']['ws2udp_handle'] = threading.Thread(target=self.__ws2tcp_handle,args=((proxy_port,proxy_protocol)))
            resource_dict['threading_handles']['heartbeat'] = threading.Thread(target=self.__heartbeat_handle,args=((proxy_port,proxy_protocol),10))

    def __init_proxy_with_async(self,proxy_port,proxy_protocol):
        pass

    def test_delay(self):
        pass

    def start_proxy(self):
        for key in self.proxy_address_list:
            resource_dict = self.__get_proxy_resource_dict(key[0],key[1])
            if resource_dict['work_mode'] == 'sync_thread':
                resource_dict['threading_handles']['udp2ws_handle'].start()
                resource_dict['threading_handles']['ws2udp_handle'].start()
                resource_dict['threading_handles']['heartbeat'].start()
    
    @staticmethod
    def __sync_proxy_shake(ws_handle,port,protocol):
        msg = {'port':port,'protocol':protocol}
        ws_handle.send(json.dumps(msg))
        recv_msg = ws_handle.recv()
        json.loads(recv_msg)
        if recv_msg['status'] == 'ok':
            return True
        else:
            return False
    
    def __tcp2ws_handle(self,resource_key):
        resource_dict = self.__get_proxy_resource_dict(resource_key[0],resource_key[1])
        wait_ws = resource_dict['semps']['wait_ws']
        wait_tcp = resource_dict['semps']['wait_sock']
        server_port = resource_key[0]
        
        wait_ws.acquire()
        websocket_handle = resource_dict['websocket_handle']
        print('开始创建tcp套接字')
        socket_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_addr = ("", server_port)
        socket_handle.bind(local_addr)
        socket_handle.setblocking(True)
        resource_dict['socket_handle'] = socket_handle
        print('套接字创建完成')
        wait_tcp.release()
        print('开启socket2ws转发')
        socket_handle.listen()
        while True:
            try:
                data = socket_handle.recv(4096)
            except:
                if len(data) > 0:
                    pass
                else:
                    continue
            print('msg of socket ---> ws:',data)
            websocket_handle.send(data)

    def __ws2tcp_handle(self,resource_key):
        resource_dict = self.__get_proxy_resource_dict(resource_key[0],resource_key[1])
        wait_ws = resource_dict['semps']['wait_ws']
        wait_tcp = resource_dict['semps']['wait_sock']
        server_port = resource_key[0]
        
        websocket_handle = websockets.sync.client.connect(ws_server_entry_point)
        print('连接ws服务器端成功')
        wait_ws.release()
        wait_tcp.acquire() #等待tcp句柄创建
        socket_handle = resource_dict['socket_handle']
        print('开启ws2socket转发')
        while True:
            data = websocket_handle.recv()
            print('msg of ws ---> socket:',data)
            socket_handle.send(data)

    def __udp2ws_handle(self,resource_key):
        resource_dict = self.__get_proxy_resource_dict(resource_key[0],resource_key[1])
        wait_ws = resource_dict['semps']['wait_ws']
        wait_udp = resource_dict['semps']['wait_sock']
        server_port = resource_key[0]
        
        wait_ws.acquire()
        websocket_handle = resource_dict['websocket_handle']
        print('开始创建udp套接字')
        socket_handle = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        local_addr = ("", server_port)
        socket_handle.bind(local_addr)
        socket_handle.setblocking(True)
        resource_dict['socket_handle'] = socket_handle
        print('套接字创建完成')
        wait_udp.release()
        print('开启socket2ws转发')
        
        data,address = socket_handle.recvfrom(4096)
        print('msg of socket ---> ws:',data)
        websocket_handle.send_binary(data)
        resource_dict['address'] = address
        
        while True:
            try:
                data,address = socket_handle.recvfrom(4096)
            except:
                if len(data) > 0:
                    pass
                else:
                    continue
            print('msg of socket ---> ws:',data)
            websocket_handle.send(data)
            
    def __ws2udp_handle(self,resource_key):
        resource_dict = self.__get_proxy_resource_dict(resource_key[0],resource_key[1])
        wait_ws = resource_dict['semps']['wait_ws']
        wait_udp = resource_dict['semps']['wait_sock']
        ws_server_entry_point = resource_key['entry_point']
        
        websocket_handle = websockets.sync.client.connect(ws_server_entry_point)
        resource_dict['websocket_handle'] = websocket_handle
        print('连接ws服务器端成功')
        wait_ws.release()
        wait_ws.release()
        wait_udp.acquire() #等待udp句柄创建
        print('开启ws2socket转发')
        address = copy.deepcopy(resource_dict['address']) 
        while True:
            data = websocket_handle.recv()
            print('msg of ws ---> socket:',data)
            socket_handle.sendto(data,address)