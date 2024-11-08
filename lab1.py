import struct
import threading
import sys
import socket

host = 'localhost'
port_sender = 5000
port_receiver = 6000

def run_sender():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port_sender))
        message = input(f"Introduceti mesajul de tip notification, care doriti ca brokerul sa-l primeasca: ")
        message_bytes = message.encode('utf-8')
        s.sendall(struct.pack('>I', len(message_bytes)) + message_bytes)
        print(f"Mesaj trimis broker-ului: {message}")
    finally:
        s.close()

def run_broker():
    def handle_client(client_socket):
        with client_socket:
            raw_length = client_socket.recv(4)
            if not raw_length:
                return
            message_length = struct.unpack('>I', raw_length)[0]
            message = client_socket.recv(message_length).decode('utf-8')
            print(f"Mesaj primit de la sender: {message}")

            receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                receiver_socket.connect((host, port_receiver))
                receiver_socket.sendall(struct.pack('>I', len(message.encode('utf-8'))) + message.encode('utf-8'))
                print(f"Mesaj transmis receiver-ului: {message}")
            finally:
                receiver_socket.close()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port_sender))
    server_socket.listen()
    print("Broker-ul este pornit si asculta pe portul 5000...")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def run_receiver():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port_receiver))
    server_socket.listen()
    print("Receiver-ul este pornit si asculta pe portul 6000...")

    while True:
        client_socket, addr = server_socket.accept()
        with client_socket:
            raw_length = client_socket.recv(4)
            if not raw_length:
                continue
            message_length = struct.unpack('>I', raw_length)[0]
            message = client_socket.recv(message_length).decode('utf-8')
            if message:
                print(f"Mesaj primit: {message}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizare: python script.py [sender|broker|receiver]")
        sys.exit(1)

    role = sys.argv[1]

    if role == "sender":
        run_sender()
    elif role == "broker":
        run_broker()
    elif role == "receiver":
        run_receiver()
    else:
        print("Rol necunoscut. Utilizați: sender, broker, sau receiver.")
        sys.exit(1)