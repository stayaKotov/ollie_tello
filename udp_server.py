from socket import socket, AF_INET, SOCK_DGRAM
maxsize = 4096

sock = socket(AF_INET,SOCK_DGRAM)
sock.bind(('', 12345))
print('start server')
while True:  
  data, addr = sock.recvfrom(maxsize)
  resp = "UDP server sending data"   
  print(data) 
  sock.sendto(str.encode(resp),addr)
