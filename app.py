import re
import socket
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Initialize CORS right after app creation

def query_dictd(word, language):
    """Query the dictd server for definitions of the given word in the specified language."""
    if language == "en":
        database = "wn"
    else:
        database = "dic_es"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("127.0.0.1", 2628))
        request_str = f"DEFINE {database} {word}\r\n"
        sock.sendall(request_str.encode("utf-8"))
        sock.shutdown(socket.SHUT_WR)
        response = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response.append(data.decode("utf-8"))
        return "".join(response)

def format_meaning_en(response):
    """Extract all definitions from the English response, cleaning up formatting and removing synonyms/examples."""
    response = response.replace("\r\n", " ")  # Remove all carriage returns and new lines
    definitions = []
    start_index = response.find("151")  # Index where definitions start
    if start_index != -1:
        response = response[start_index:]
        definitions = re.findall(r'\d+:\s.*?(?=\s+\[\w+:|\s+\d+:|$)', response)
        definitions = [re.sub(r'\s+\[\w+:\s*{[^}]+}\]', '', definition).strip() for definition in definitions]  # Remove synonyms
        definitions = [re.sub(r'".*?"', '', definition).strip() for definition in definitions]  # Remove examples
        definitions = [re.sub(r'\s{2,}', ' ', definition) for definition in definitions]  # Normalize spaces
        # Capitalize the first letter after the definition number
        definitions = [re.sub(r'(\d+:\s)([a-z])', lambda match: match.group(1) + match.group(2).upper(), definition) for definition in definitions]
    return definitions

def format_meaning_es_improved(response):
    """Improved definition extraction for Spanish responses."""
    definitions = []
    lines = response.split("\n")
    start_index = next(
        (i for i, line in enumerate(lines) if re.match(r'^\d+\s"[^"]+"\sdic_es\s', line)), -1
    )
    lines = lines[start_index + 1:] if start_index != -1 else lines
    full_text = " ".join(line.strip() for line in lines)
    start_split = re.split(r"(\d+\.\s)", full_text, 1)
    start_part = start_split[0].strip() if len(start_split) > 2 else ""
    full_text = start_split[1] + start_split[2] if len(start_split) > 2 else full_text
    raw_definitions = re.split(r"(\d+\.\s)", full_text)
    current_definition = raw_definitions.pop(0) if raw_definitions else ""
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
    definitions = [defn for defn in definitions if defn.strip() and re.match(r"\d+\.\s.+", defn)]
    return start_part, definitions

@app.route("/meaning", methods=["GET"])
def get_meaning():
    """Endpoint to get word meanings."""
    word = request.args.get("word", "").strip()
    language = request.args.get("lang", "").strip()
    if not word:
        return jsonify({"error": "No word provided"}), 400
    try:
        raw_response = query_dictd(word, language)
        if language == "en":
            formatted_meanings = format_meaning_en(raw_response)
            start_part = "n/a"  # No initial part relevant in English format
        else:
            start_part, formatted_meanings = format_meaning_es_improved(raw_response)
        return jsonify(
            {"word": word, "meanings": formatted_meanings, "language": language, "start": start_part}
        )
    except Exception as e:
        app.logger.error(f"Error fetching meaning for word '{word}': {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

