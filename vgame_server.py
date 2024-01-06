import socket
from time import sleep               
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("127.0.0.1", 12345))
while True:
    data,address = udp_socket.recvfrom(1024)
    print(data,address)
    udp_socket.sendto(data, address)
    
    # sleep(1)