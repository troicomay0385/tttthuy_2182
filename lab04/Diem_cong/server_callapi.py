import sys
import socket
import threading

from PyQt5 import QtWidgets
from ui.Server import Ui_MainWindow  

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 24682))
server_socket.listen(5)

server_key = RSA.generate(2048)
clients = []

def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cipher.iv + ciphertext


def decrypt_message(key, encrypted_message):
    iv = encrypted_message[:AES.block_size]
    ciphertext = encrypted_message[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted.decode()


# lớp UI
class ServerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # set mặc định
        self.ui.lbl_status.setText("Running...")
        self.ui.txt_chatlog.setReadOnly(True)
        self.ui.txt_connectclient.setReadOnly(True)

        # button
        self.ui.btn_connect.clicked.connect(self.stop_server)

        # start server thread
        threading.Thread(target=self.start_server, daemon=True).start()

    def start_server(self):
        self.log("Server is listening...")
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                self.log(f"Connected: {client_address}")
                self.add_client(client_address)

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                thread.start()
            except:
                break

    def handle_client(self, client_socket, client_address):
        try:
            # gửi public key
            client_socket.send(server_key.publickey().export_key())

            # nhận key client
            client_key = RSA.import_key(client_socket.recv(2048))

            # tạo AES
            aes_key = get_random_bytes(16)

            cipher_rsa = PKCS1_OAEP.new(client_key)
            encrypted_aes = cipher_rsa.encrypt(aes_key)
            client_socket.send(encrypted_aes)

            clients.append((client_socket, aes_key))

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                msg = decrypt_message(aes_key, data)
                self.log(f"{client_address}: {msg}")

                if msg == "exit":
                    break

                # broadcast
                for client, key in clients:
                    if client != client_socket:
                        client.send(encrypt_message(key, msg))

        except Exception as e:
            self.log(f"Error: {e}")

        # disconnect
        self.log(f"Disconnected: {client_address}")
        self.remove_client(client_address)
        client_socket.close()

    # cập nhật
    def log(self, message):
        self.ui.txt_chatlog.append(message)

    def add_client(self, addr):
        self.ui.txt_connectclient.append(str(addr))

    def remove_client(self, addr):
        self.ui.txt_connectclient.append(f"Removed: {addr}")

    def stop_server(self):
        self.ui.lbl_status.setText("Stopped")
        self.log("Server stopping...")

    # đóng tất cả client
        for client, _ in clients:
            try:
                client.close()
            except:
                pass

        clients.clear()

        # đóng server
        try:
            server_socket.close()
        except:
            pass

        self.log("Server stopped")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ServerApp()
    window.show()
    sys.exit(app.exec_())