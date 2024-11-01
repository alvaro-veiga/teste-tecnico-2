from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'tmp/teste-api'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload', methods=['PUT'])
def upload_file():
    filename = request.args.get('filename')

    if not re.match(r'^[A-Za-z0-9-_]+$', filename):
        return jsonify({"error": "Invalid filename"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, 'wb') as f:
        f.write(request.get_data())

    return jsonify({"message": "File uploaded successfully"}), 201


@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files), 200


def process_file(file_path):
    users = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                print(f"Processando linha: {line}")  # Debug: imprime a linha original

                line = line.strip()  # Remove espaços em branco nas extremidades
                if not line:
                    print("Linha vazia encontrada, pulando.")
                    continue

                parts = line.split()
                print(f"Partes da linha: {parts}")  # Debug: imprime as partes divididas

                if len(parts) < 5:
                    print(f"Formato incorreto na linha: '{line}'. Pulando.")
                    continue

                try:
                    username = parts[0]
                    folder = parts[1]
                    number_messages = int(parts[2])
                    size = int(parts[4])  # Tamanho da mensagem ou arquivo

                    user_data = {
                        "username": username,
                        "folder": folder,
                        "numberMessages": number_messages,
                        "size": size
                    }
                    users.append(user_data)
                    print(f"Usuário adicionado: {user_data}")

                except ValueError as e:
                    print(f"Erro ao processar a linha '{line}': {e}. Pulando.")
                    continue
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

    return users

@app.route('/max-size', methods=['GET'])
def get_max_size_user():
    file_path = os.path.join(UPLOAD_FOLDER, 'input')

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    users = process_file(file_path)

    if not users:
        return jsonify({"error": "No data found"}), 404

    max_user = max(users, key=lambda x: x['size'])
    return jsonify(max_user), 200


@app.route('/min-size', methods=['GET'])
def get_min_size_user():
    file_path = os.path.join(UPLOAD_FOLDER, 'input')

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    users = process_file(file_path)

    if not users:
        return jsonify({"error": "No data found"}), 404

    min_user = min(users, key=lambda x: x['size'])
    return jsonify(min_user), 200


@app.route('/ordered-users', methods=['GET'])
def get_ordered_users():
    file_path = os.path.join(UPLOAD_FOLDER, 'input')

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    users = process_file(file_path)

    if not users:
        return jsonify({"error": "No data found"}), 404

    descending = request.args.get('desc', 'false').lower() == 'true'
    ordered_users = sorted(users, key=lambda x: x['username'], reverse=descending)
    return jsonify(ordered_users), 200


@app.route('/between-msgs', methods=['GET'])
def get_users_between_msgs():
    min_msgs = int(request.args.get('min', 0))

    max_msgs = request.args.get('max')

    if max_msgs is None:
        max_msgs = float('inf')
    else:
        max_msgs = int(max_msgs)

    file_path = os.path.join(UPLOAD_FOLDER, 'input')

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    users = process_file(file_path)

    if not users:
        return jsonify({"error": "No data found"}), 404

    # Filtra os usuários com base no número de mensagens
    filtered_users = [user for user in users if min_msgs <= user['numberMessages'] <= max_msgs]
    return jsonify(filtered_users), 200


if __name__ == '__main__':
    app.run(debug=True)
