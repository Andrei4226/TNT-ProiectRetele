import socket
import threading

server_address = ('127.0.0.1', 8080)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creaza un socket TCP/IP
server_socket.bind(server_address)  # asociaza socket-ul cu adresa serverului
server_socket.listen(5)  # seteaza serverul pentru a asculta pana la 5 conexiuni in asteptare

key_object_map = {}
clients = []


def client_thread(connection, client_address):
    global key_object_map
    if not key_object_map:
        connection.sendall("KEYS: empty".encode())  # trimite un mesaj de 'empty' daca nu exista chei
    else:
        connection.sendall(("KEYS: " + ",".join(key_object_map.keys())).encode())  # trimite lista cheilor existente

    try:
        while True:
            data = connection.recv(1024).decode()  # primeste pana la 1024 bytes si decodeaza mesajul
            if not data:
                break

            command, *params = data.split()

            if command == 'ADD':
                if len(params) < 3:
                    connection.sendall("ERROR: Missing key, object type or object content!".encode())
                    continue
                key, obj_type, obj_content = params
                if key in key_object_map:
                    connection.sendall(f"ERROR: Key {key} already exists!".encode())
                    continue
                key_object_map[key] = {'type': obj_type, 'content': obj_content, 'client': connection}
                broadcast(f"NEW_KEY {key}")  # trimite mesajul de tip broadcast catre toti clientii
                connection.sendall("ADD_SUCCESSFUL".encode())

            elif command == 'EDIT':
                if len(params) < 3:
                    connection.sendall("ERROR: Missing key, object type or object content!".encode())
                    continue
                key, obj_type, obj_content = params
                if key not in key_object_map:
                    connection.sendall("ERROR: Key not found!".encode())
                    continue
                if key_object_map[key]['client'] != connection:
                    connection.sendall("ERROR: You are not authorized to edit this key!".encode())
                    continue
                key_object_map[key] = {'type': obj_type, 'content': obj_content, 'client': connection}
                broadcast(f"EDIT_KEY {key}")
                connection.sendall("EDIT_SUCCESSFUL".encode())

            elif command == 'VIEW':
                if not key_object_map:
                    connection.sendall("KEYS: empty".encode())  # trimite mesajul daca nu exista chei
                else:
                    connection.sendall(("KEYS: " + ",".join(key_object_map.keys())).encode())  # trimite lista cheilor existente

            elif command == 'FIND':
                if len(params) < 1:
                    connection.sendall("ERROR: Missing key!".encode())
                    continue
                key = params[0]
                if key not in key_object_map:
                    connection.sendall(f"ERROR: Key {key} not found!".encode())
                    continue
                obj = key_object_map[key]
                connection.sendall(f"KEY {key} - TYPE {obj['type']} - CONTENT {obj['content']}".encode())  # trimite detalii despre cheia gasita

            elif command == 'DELETE':
                if len(params) < 1:
                    connection.sendall("ERROR: Missing key!".encode())
                    continue
                key = params[0]
                if key not in key_object_map:
                    connection.sendall("ERROR: Key not found!".encode())
                    continue
                if key_object_map[key]['client'] != connection:
                    connection.sendall("ERROR: You are not authorized to delete this key!".encode())
                    continue
                del key_object_map[key]  # sterge cheia din dictionar
                broadcast(f"DELETE_KEY {key}")  # trimite mesajul de tip broadcast catre toti clientii
                connection.sendall("DELETE_SUCCESSFUL".encode())

    finally:
        connection.close()  # inchide conexiunea clientului
        clients.remove(connection)  # elimina clientul din lista


def broadcast(message):
    for client in clients:
        client.sendall(message.encode())  # trimite mesajul catre toti clientii din lista


print(f"Server is waiting for connections at {server_address}")
while True:
    connection, client_address = server_socket.accept()  # accepta o noua conexiune
    clients.append(connection)  # adauga noul client in lista
    threading.Thread(target=client_thread, args=(connection, client_address)).start()  # porneste un thread pentru fiecare client
