import socket
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import reverse
import os
import time
import base64

# This store the temp data
temp = {}

def receive_from(connection):
	buffer = b""
	# We set a 2 second timeout; depending on your
	# target, this may need to be adjusted
	connection.settimeout(5)
	try:
		buffer = connection.recv(4096)
	except:
		pass
	return buffer

# Create your views here.
# This view init the connection
@csrf_exempt
def connect(request):
	global temp
	# should put POST, and given the crfs token, for more security
	if request.method == 'POST':
		# This is the token given by client, it will represent the socket used for an operation
		token = request.POST.get('token', None)
		# We get data of the remote server
		remote_host = request.POST.get('remote_host', None)
		remote_port = request.POST.get('remote_port', '0')
		# We verify is data valid
		if token and remote_host and remote_port.isdigit() and remote_port != '0':
			remote_port = int(remote_port)
			# connect to the remote host
			remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			remote_socket.connect((remote_host, remote_port))
			# This is the key to access to the socket
			key = '<facebook_account_token>|%s'%token
			# We put the socket in temp
			temp[key] = remote_socket
			return HttpResponse('connect')
	return HttpResponse('error')

@csrf_exempt
# This view permit only to read data by the client to remote host
def recv(request):
	global temp
	if request.method == 'POST':
		token = request.POST.get('token', None)
		key = '<facebook_account_token>|%s'%token
		# We verify data and if key exists
		if token and key in temp:
			# We get the socket to use
			remote_socket = temp[key]
			# We receive from the remote host
			remote_buffer = receive_from(remote_socket)
			if len(remote_buffer):
				# We send to the client
				return HttpResponse(base64.b64encode(remote_buffer))
			else:
				return HttpResponse('')
	return HttpResponse('error')

@csrf_exempt
# This view permit only to send only data by the client to remote host
def send(request):
	global temp
	if request.method == 'POST':
		token = request.POST.get('token', None)
		# We receive data from the client
		data = request.POST.get('data', None)
		key = '<facebook_account_token>|%s'%token
		# We verify data and if key exists
		if token and data and key in temp:
			remote_socket = temp[key]
			data = base64.b64decode(data.encode())
			# We send to the remote
			remote_socket.send(data)
			return HttpResponse('send')
	return HttpResponse('error')

@csrf_exempt
# This view permit to end a connection
def close(request):
	global temp
	if request.method == 'POST':
		token = request.POST.get('token', None)
		key = '<facebook_account_token>|%s'%token
		# We verify data and if key exists
		if token and key in temp:
			# We get the socket to use
			remote_socket = temp[key]
			remote_socket.close()
			return HttpResponse('close')
	return HttpResponse('error')

@csrf_exempt
# This view permit to verify if the connection
# with the client pass
def test(request):
	if request.POST:
		return HttpResponse(request.POST.get('token', None))
	return HttpResponse('error')