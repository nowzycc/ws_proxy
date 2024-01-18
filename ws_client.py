import asyncio
import websockets
import socket 
import ws_proxy
import json

VER = '0.2'

def version_check(config_ver,current_ver):
    if config_ver != current_ver:
        raise '配置文件版本错误'

def main():
    config = None
    with open('./config_v02.json','r') as f:
        config = json.load(f)
    config_version = config['version']
    version_check(config_version,VER)
    ws_proxy_list = []
    for app,app_configs in config['app']:
        proxy = ws_proxy.ws_proxy(app)
        ws_proxy_list.append(proxy)
        for app_config in app_configs:
            proxy.init_proxy(app_config['ws_server_entry_point'],app_config['app_server_port'],app_config['app_server_protocol'],'sync_thread')
        proxy.start_proxy()
    while True:
        pass