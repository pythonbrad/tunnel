#!/usr/bin/env python
import sys
import socket
import threading
import base64
import requests
import time

"""
	SHOW ALL INFO FOR THE PRODUCTION MODE
"""

print("CONVERT TO PYTHON2, TO EXPLOIT ALL THE HEXDUMP AND FOR THE SPEED")


class RemoteServer:
	"""
		This class permit to simulate a normal socket to modify the way of the communication
	"""
	def __init__(self, host='http://127.0.0.1:8000/proxy/'):
		self.host = host
		# I create a token
		self.token = str(time.clock())
	def connect(self, addr):
		# We connect to the remote host
		re = requests.post(self.host+'connect', data={'token': self.token, 'remote_host': addr[0], 'remote_port': addr[1]})
		data = re.content
		re.close()
		if data != b'connect':
			print('[!!] Remote connection error')
			sys.exit(0)
	def send(self, data):
		# I send data to the remote host
		re = requests.post(self.host+'send', data={'token': self.token, 'data': base64.b64encode(data)})
		data = re.content
		re.close()
		if data != b'send':
			print('[!!] Sendind data from error')
			sys.exit(0)
	def recv(self, x):
		# This exception because while the reception by the proxy, all error is often ignored
		# We show error if catch
		try:
			re = requests.post(self.host+'recv', data={'token': self.token})
			# I receive data from the remote host
			data = re.content
			re.close()
			if data == b'error':
				print('[!!] Getting data from remote error')
				return b''
			elif data:
				data = base64.b64decode(data)
		except Exception as err:
			print('[!!] ', err)
			sys.exit(0)
		return data
	def test_tunnel(self):
		token = ''
		try:
			re = requests.post(self.host+'test', data={'token': self.token})
			token = re.text
			re.close()
		except:
			pass
		return token == self.token
	def settimeout(self, x):
		pass
	def close(self):
		re = requests.post(self.host+'close', data={'token': self.token})
		re.close()


def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		server.bind((local_host,local_port))
	except:
		print("[!!] Failed to listen on %s:%d" % (local_host,local_port))
		print("[!!] Check for other listening sockets or correct permissions.")
		sys.exit(0)
	print("[*] Listening on %s:%d" % (local_host,local_port))
	server.listen(5)
	while True:
		try:
			client_socket, addr = server.accept()
		except KeyboardInterrupt:
			server.close()
			print("Aborting...")
			sys.exit(0)
		# print out the local connection information
		print("[==>] Received incoming connection from %s:%d" % (addr[0],addr[1]))
		# start a thread to talk to the remote host
		proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,remote_host,remote_port,receive_first))
		proxy_thread.start()

def main():
	# no fancy command-line parsing here
	if len(sys.argv[1:]) != 5:
		print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
		print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
		sys.exit(0)
	# setup local listening parameters
	local_host = sys.argv[1]
	local_port = int(sys.argv[2])
	# setup remote target
	remote_host = sys.argv[3]
	remote_port = int(sys.argv[4])
	# this tells our proxy to connect and receive data
	# before sending to the remote host
	receive_first = sys.argv[5]
	if "True" in receive_first:
		receive_first = True
	else:
		receive_first = False

	# now spin up our listening socket
	server_loop(local_host,local_port,remote_host,remote_port,receive_first)

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
	# connect to the remote host
	# Replace it by remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# to got an normal proxy
	remote_socket = RemoteServer()
	remote_socket.connect((remote_host,remote_port))
	# receive data from the remote end if necessary
	if receive_first:
		remote_buffer = receive_from(remote_socket, dest=client_socket, send_name='remote', dest_name='localhost')
	# now lets loop and read from local,
	# send to remote, send to local
	# rinse, wash, repeat
	while True:
		# read from local host and send to remote host
		local_has_buffer = receive_from(client_socket, dest=remote_socket, send_name='localhost', dest_name='remote')
		# receive back the response and send to local host
		remote_has_buffer = receive_from(remote_socket, dest=client_socket, send_name='remote', dest_name='localhost')
		# if no more data on either side, close the connections
		if not local_has_buffer or not remote_has_buffer:
			client_socket.close()
			remote_socket.close()
			print("[*] No more data. Closing connections.")
			break

# this is a pretty hex dumping function directly taken from
# the comments here:
# http://code.activestate.com/recipes/142812-hex-dumper/
def hexdump(src, length=16):
	result = []
	digits = 4 if isinstance(src, unicode) else 2
	for i in xrange(0, len(src), length):
		s = src[i:i+length]
		hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
		text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
		result.append( b"%04X %-*s %s" % (i, length*(digits + 1), hexa, text) )
		print(b'\n'.join(result))

def receive_from(connection, dest, send_name='', dest_name=''):
	# We set a 2 second timeout; depending on your
	# target, this may need to be adjusted
	has_recv = False
	connection.settimeout(5)
	try:
		# keep reading into the buffer until
		# there's no more data
		# or we time out
		while True:
			buffer = connection.recv(4096)
			if not buffer:
				break
			else:
				has_recv = True
				print("[==>] Received %d bytes from %s." % (len(buffer), send_name))
				#hexdump(local_buffer)
				# send it to our request handler
				buffer = request_handler(buffer)
				# send off the data to the dest
				try:
					dest.send(buffer)
					print("[==>] Sent to %s."%dest_name)
				except Exception as err:
					if dest_name == "localhost":
						print("[!!] localhost lost")
	except Exception as err:
		print('[!!] ', err)
	return has_recv
# modify any requests destined for the remote host or local host
def request_handler(buffer):
	# perform packet modifications
	return buffer

remote_test = RemoteServer()
# We test the tunnel
status = remote_test.test_tunnel()
if status:
	main()
else:
	print("[!!] The server don't respond, aborting...")