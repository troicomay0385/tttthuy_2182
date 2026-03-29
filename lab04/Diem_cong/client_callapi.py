import sys
import socket
import threading
from PyQt5 import QtWidgets
from ui.Client import Ui_MainWindow  
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class ClientApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # UI setup
        self.ui.txt_chatlog_2.setReadOnly(True)
        self.ui.txt_chatlog.setPlaceholderText("Enter message...")

        # Button events
        self.ui.pushButton.clicked.connect(self.send_message)
        self.ui.pushButton_2.clicked.connect(self.disconnect)

        # SOCKET 
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 24682))

        # RSA
        self.client_key = RSA.generate(2048)

        # nhận public key server
        server_public_key = RSA.import_key(self.client_socket.recv(2048))

        # gửi public key client
        self.client_socket.send(self.client_key.publickey().export_key())

        # nhận AES key
        encrypted_aes = self.client_socket.recv(2048)
        cipher_rsa = PKCS1_OAEP.new(self.client_key)
        self.aes_key = cipher_rsa.decrypt(encrypted_aes)

        self.log("Connected to server")

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def encrypt_message(self, message):
        cipher = AES.new(self.aes_key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
        return cipher.iv + ciphertext

    def decrypt_message(self, data):
        iv = data[:AES.block_size]
        ciphertext = data[AES.block_size:]
        cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()

    def log(self, message):
        self.ui.txt_chatlog_2.append(message)

    def send_message(self):
        message = self.ui.txt_chatlog.toPlainText().strip()
        if not message:
            return

        encrypted = self.encrypt_message(message)
        self.client_socket.send(encrypted)

        self.log(f"You: {message}")
        self.ui.txt_chatlog.clear()

        if message == "exit":
            self.disconnect()

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                msg = self.decrypt_message(data)
                self.log(f"Friend: {msg}")

            except:
                break

    def disconnect(self):
        try:
            self.client_socket.close()
        except:
            pass

        self.log("Disconnected from server")
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ClientApp()
    window.show()
    sys.exit(app.exec_())