from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def query_dictd(word):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to the dictd server running on the same machine
        sock.connect(('127.0.0.1', 2628))

        # Send the request for definitions according to the DICT protocol
        request = f"DEFINE * {word}\r\n"
        sock.sendall(request.encode('utf-8'))

        # Terminate the sending side to signify end of request
        sock.shutdown(socket.SHUT_WR)

        # Collect the response
        response = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response.append(data.decode('utf-8'))

        return ''.join(response)

@app.route('/meaning', methods=['GET'])
def get_meaning():
    word = request.args.get('word')
    if not word:
        return jsonify({"error": "No word provided"}), 400

    try:
        # Query the dictd server for the meaning
        result = query_dictd(word)
        return jsonify({"word": word, "meaning": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

