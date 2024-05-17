import socket
import threading

server_address = ('127.0.0.1', 8080)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creaza un socket TCP/IP
client_socket.connect(server_address)  # se conecteaza la server folosind adresa specificata


def listen_for_messages():
    while True:
        data = client_socket.recv(1024)  # primeste pana la 1024 bytes de la server
        if data:
            print(f"\nMessage from server: {data.decode()}")


def send_command(command):
    client_socket.sendall(command.encode())  # trimite comanda codificata ca bytes la server


try:
    threading.Thread(target=listen_for_messages, daemon=True).start()  # incepe un thread pentru a asculta mesajele de la server
    while True:
        command = input("\nEnter command type (ADD, FIND, DELETE, VIEW, EDIT): ").strip().upper()
        if command == "ADD":
            key = input("Enter the key: ").strip()
            obj_type = input("Enter the object type (int, float, string, other): ").strip().lower()

            if obj_type not in ["int", "float", "string", "other"]:
                print("Error: Invalid object type!")
                continue

            if obj_type == "int":
                try:
                    obj_content = int(input("Enter the object content: ").strip())  # converteste input-ul la int
                    obj_content = str(obj_content)  # converteste la string pentru trimiterea catre server
                except ValueError:
                    print("Error: Object content must be an integer!")
                    continue
            elif obj_type == "float":
                try:
                    obj_content = float(input("Enter the object content: ").strip())  # converteste input-ul la float
                    obj_content = str(obj_content)  # converteste la string pentru trimiterea catre server
                except ValueError:
                    print("Error: Object content must be a float!")
                    continue
            elif obj_type == "string":
                obj_content = input("Enter the object content: ").strip()  # citeste continutul obiectului ca string
            elif obj_type == "other":
                obj_content = input("Enter the object content: ").strip()

            send_command(f"{command} {key} {obj_type} {obj_content}")

        elif command == "VIEW":
            send_command(command)  # trimite comanda VIEW la server

        elif command in ["FIND", "DELETE"]:
            key = input("Enter the key: ").strip()  # citeste cheia pentru operatiunile FIND sau DELETE
            send_command(f"{command} {key}")

        elif command == "EDIT":
            key = input("Enter the key: ").strip()
            obj_type = input("Enter the new object type (int, float, string, other): ").strip().lower()
            if obj_type not in ["int", "float", "string", "other"]:
                print("Error: Invalid object type!")
                continue
            if obj_type == "int":
                try:
                    obj_content = int(input("Enter the new object content: ").strip())  # converteste input-ul la int
                    obj_content = str(obj_content)  # converteste la string pentru trimiterea catre server
                except ValueError:
                    print("Error: Object content must be an integer!")
                    continue
            elif obj_type == "float":
                try:
                    obj_content = float(input("Enter the new object content: ").strip())  # converteste input-ul la float
                    obj_content = str(obj_content)  # converteste la string pentru trimiterea catre server
                except ValueError:
                    print("Error: Object content must be a float!")
                    continue
            elif obj_type == "string":
                obj_content = input("Enter the new object content: ").strip()  # citeste continutul obiectului ca string
            elif obj_type == "other":
                obj_content = input("Enter the new object content: ").strip()
            send_command(f"{command} {key} {obj_type} {obj_content}")
        else:
            print("Invalid command. Please enter one of ADD, FIND, DELETE, VIEW, EDIT.")
finally:
    client_socket.close()  # inchide conexiunea cu serverul
