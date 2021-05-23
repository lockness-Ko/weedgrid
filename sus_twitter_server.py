import socket
import urllib.parse

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

import random
import tensorflow as tf

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

one_step_reloaded = tf.saved_model.load('one_step')

while True:    
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    try:
        # Get the client request
        request = client_connection.recv(1024).decode()
        # print(request.split("GET /")[1].split(" HTTP")[0])

        states = None
        choices = ['C','S','P','D']
        rq = urllib.parse.unquote(request.split("GET /")[1].split(" HTTP")[0])
        if rq=="":next_char = tf.constant([random.choice(choices)])
        else:next_char = tf.constant([rq])
        result = [next_char]

        for n in range(80):
            next_char, states = one_step_reloaded.generate_one_step(next_char, states=states)
            result.append(next_char)

        # Send HTTP response
        response = 'HTTP/1.0 200 OK\n\n'+tf.strings.join(result)[0].numpy().decode("utf-8")
        client_connection.sendall(response.encode())
        client_connection.close()
    except Exception:
        pass
    

# Close socket
server_socket.close()

