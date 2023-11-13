import socket
import sys
import _thread
import time
import ssl
import queue


def main(serverIP, serverPort, localIP, localPort):
    _thread.start_new_thread(client, (serverIP, int(serverPort), localIP, int(localPort)))
    while True:
        time.sleep(60)



def client(serverIP, serverPort, localIP, localPort):
	while(True):
		try:
			# CREATE SOCKET
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			ctx = ssl.create_default_context()
			ctx.check_hostname = False
			ctx.verify_mode = ssl.CERT_NONE

			# WRAP SOCKET
			wrappedSocket = ctx.wrap_socket(sock)

			# CONNECT AND PRINT REPLY
			wrappedSocket.connect((serverIP, serverPort))
			fakeReq = "GET / HTTP/1.1\nHost: "+serverIP+"\n\n"
			wrappedSocket.send(fakeReq.encode('ascii'))
			wrappedSocket.recv(122)
			wrappedSocket.settimeout(10)
			message = wrappedSocket.recv(5)
			#print (message)
			if(message !=b"HELLO"):
				raise Exception("No client connected")
			else:
				print ("Connection Received")
				client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# Connect the socket to the port where the server is listening
				client_socket.connect((localIP, localPort))
				_thread.start_new_thread(forward, (client_socket, wrappedSocket))
				_thread.start_new_thread(forward, (wrappedSocket, client_socket)) 

		except Exception as e:
			print(e)
			time.sleep(3)
			try:
				wrappedSocket.close()
			except:
				pass
			try:
				client_socket.close()
			except:
				pass


def forward(source, destination):
	try:
		string = ' '
		while string:
			string = source.recv(1024)
			if string:
				destination.sendall(string)
			else:
				source.shutdown(socket.SHUT_RD)
				destination.shutdown(socket.SHUT_WR)
	except:
		try:
			source.shutdown(socket.SHUT_RD)
			destination.shutdown(socket.SHUT_WR)
		except:
			pass
	pass


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage:{} <serverIP> <serverPort> <localIP> <localPort>".format(sys.argv[0]))
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
