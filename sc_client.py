import socket
from time import sleep               
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    udp_socket.sendto("hello".encode("utf-8"), ("127.0.0.1", 12345))
    data,server = udp_socket.recvfrom(1024)
    print(data)
    sleep(0.1)