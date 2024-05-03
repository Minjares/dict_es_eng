from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def query_dictd(word, language):
    database = "wm" if language == "en" else "dic_es"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('127.0.0.1', 2628))

        request = f"DEFINE {database} {word}\r\n"
        sock.sendall(request.encode('utf-8'))

        sock.shutdown(socket.SHUT_WR)

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
    language = request.args.get('lang', 'en')  
    if not word:
        return jsonify({"error": "No word provided"}), 400

    try:
        result = query_dictd(word, language)
        return jsonify({"word": word, "meaning": result, "language": language, "hola": "hola"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

