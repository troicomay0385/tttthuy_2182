from flask import Flask, render_template, request, json
from cipher.caesar import CaesarCipher
from cipher.vigenere import VigenereCipher
from cipher.railfence import RailFenceCipher
app = Flask(__name__)

# router routes for home page
@app.route("/")
def home():
    return render_template("index.html")


# router routes for caesar cypher
@app.route("/caesar")
def caesar():
    return render_template("caesar.html")


@app.route("/caesar/encrypt", methods=["POST"])
def caesar_encrypt():
    text = request.form['inputPlainText']
    key = int(request.form['inputKeyPlain'])

    Caesar = CaesarCipher()

    encrypted_text = Caesar.encrypt_text(text, key)

    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"


@app.route("/caesar/decrypt", methods=["POST"])
def caesar_decrypt():
    text = request.form['inputCipherText']
    key = int(request.form['inputKeyCipher'])

    Caesar = CaesarCipher()

    decrypted_text = Caesar.decrypt_text(text, key)

    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

#vigenere
# router routes for vigenere cypher
@app.route("/vigenere")
def vigenere():
    return render_template("vigenere.html")


@app.route("/vigenere/encrypt", methods=["POST"])
def vigenere_encrypt():
    text = request.form['inputPlainText']
    key = request.form['inputKeyPlain']

    Vigenere =VigenereCipher()

    encrypted_text = Vigenere.vigenere_encrypt(text, key)

    return f"text: {text}<br/>key: {key}<br/>encrypted text: {encrypted_text}"


@app.route("/vigenere/decrypt", methods=["POST"])
def vigenere_decrypt():
    text = request.form['inputCipherText']
    key = request.form['inputKeyCipher']

    Vigenere =VigenereCipher()

    decrypted_text = Vigenere.vigenere_decrypt(text, key)

    return f"text: {text}<br/>key: {key}<br/>decrypted text: {decrypted_text}"

#rail
@app.route("/railfence")
def railfence():
    return render_template("railfence.html")


@app.route("/railfence/encrypt", methods=["POST"])
def railfence_encrypt():
    text = request.form['inputPlainText']
    try:
        rails = int(request.form['inputKey'])
        if rails < 2:
            return "Error: Number of rails must be ≥ 2", 400
    except:
        return "Error: Invalid key", 400

    RailFence = RailFenceCipher()
    encrypted_text = RailFence.rail_fence_encrypt(text, rails)

    return f"""
    <pre>
Plain text  : {text}
Rails (key) : {rails}
Cipher text : {encrypted_text}
    </pre>
    <br><a href="/railfence">← Quay lại</a>
    """


@app.route("/railfence/decrypt", methods=["POST"])
def railfence_decrypt():
    text = request.form['inputCipherText']
    try:
        rails = int(request.form['inputKey'])
        if rails < 2:
            return "Error: Number of rails must be ≥ 2", 400
    except:
        return "Error: Invalid key", 400

    RailFence = RailFenceCipher()
    decrypted_text = RailFence.rail_fence_decrypt(text, rails)

    return f"""
    <pre>
Cipher text : {text}
Rails (key) : {rails}
Plain text  : {decrypted_text}
    </pre>
    <br><a href="/railfence">← Quay lại</a>
    """

# main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)