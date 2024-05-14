import re
import socket

from flask import Flask, jsonify, request

app = Flask(__name__)


def query_dictd(word, language):
    if language == "en":
        database = "wn"
    else:
        database = "dic_es"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 2628))

        request = f"DEFINE {database} {word}\r\n"
        sock.sendall(request.encode("utf-8"))

        sock.shutdown(socket.SHUT_WR)

        response = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response.append(data.decode("utf-8"))

        return "".join(response)


def format_meaning(response):
    definitions = []
    capture = False
    current_definition = []

    for line in response.split("\n"):
        if re.match(r'^\d+\s"[^"]+"\swn\s', line):
            capture = True
            continue

        if line.strip() == ".":
            capture = False
            if current_definition:
                definitions.append(" ".join(current_definition).strip())
                current_definition = []
            break

        if capture:
            if re.match(r"^\s*(adj|n|v|adv|prep|conj|pron|interj)\s+\d+:", line):
                if current_definition:
                    definitions.append(" ".join(current_definition).strip())
                    current_definition = []
            current_definition.append(line.strip())

    if current_definition:
        definitions.append(" ".join(current_definition).strip())

    return definitions


def format_meaning_es_improved(response):
    definitions = []
    lines = response.split("\n")

    start_index = next(
        i for i, line in enumerate(lines) if re.match(r'^\d+\s"[^"]+"\sdic_es\s', line)
    )
    lines = lines[start_index + 1 :]

    full_text = " ".join(line.strip() for line in lines)

    raw_definitions = re.split(r"(\d+\.\s)", full_text)

    current_definition = ""

    if raw_definitions:
        first_part = raw_definitions.pop(0)
        current_definition += first_part

    for part in raw_definitions:
        if re.match(r"\d+\.\s", part):
            if current_definition:
                definitions.append(current_definition.strip())
                current_definition = part
            else:
                current_definition = part
        else:
            current_definition += part

    if current_definition:
        definitions.append(current_definition.strip())

    return definitions


@app.route("/meaning", methods=["GET"])
def get_meaning():
    word = request.args.get("word").strip()
    language = request.args.get("lang").strip()
    if not word:
        return jsonify({"error": "No word provided"}), 400

    try:
        raw_response = query_dictd(word, language)
        if language == "en":
            formatted_meaning = format_meaning(raw_response)
        else:
            formatted_meaning = format_meaning_es_improved(raw_response)
        return jsonify(
            {"word": word, "meanings": formatted_meaning, "language": language}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
