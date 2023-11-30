from flask import Flask, g, make_response, jsonify, request
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import secrets


conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='H@pp!n3$',
    database='db_sebo',
)

secret_key = secrets.token_hex(16)
#Exemplo de saída, secret_key = 4bd253d62aae3cf0230c1cd0dc6c107c

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = secret_key

#-----------USERS----------------------------------------------------------------------------------------------
@app.route('/users/cadastro', methods=['POST'])
def cadastrar_user():
    try:
        user_data = request.get_json()

        # Verifica se o e-mail já existe no banco de dados
        cursor = conexao.cursor()
        check_email_query = f"SELECT COUNT(*) FROM users WHERE email = '{user_data['email']}'"
        cursor.execute(check_email_query)
        email_exists = cursor.fetchone()[0]

        if email_exists > 0:
            return jsonify({"error": "E-mail já está em uso."}), 409  # 400 Bad Request

        # Criptografa a senha antes de armazenar no banco de dados
        senha_hash = generate_password_hash(user_data['senha'])

        cursor = conexao.cursor()
        create = f"INSERT INTO users (nome, email, senha, tipo, isAdmin) VALUES ('{user_data['nome']}', '{user_data['email']}', '{senha_hash}', '{user_data['tipo']}', {user_data.get('isAdmin', 0)})"
        cursor.execute(create)
        conexao.commit()

        return jsonify(
            mensagem='Usuário cadastrado com sucesso.',
            user=user_data
        ), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request

# Exemplo de depuração
import jwt

# ... (código anterior)

@app.route('/users/login', methods=['POST'])
def login_user():
    try:
        dados_login = request.get_json()

        cursor = conexao.cursor()
        read = f"SELECT * FROM users WHERE email = '{dados_login['email']}'"
        cursor.execute(read)
        user = cursor.fetchone()

        print("Dados de Login:", dados_login)
        print("Usuário do Banco de Dados:", user)

        if user is not None:
            user_id_str = str(user[0])
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            
            print("User ID (convertido para string):", user_id_str)
            print("Tempo de Expiração:", expiration_time)

            payload = {
                'user_id': user_id_str,
                'exp': expiration_time
            }

            secret_key = app.config['SECRET_KEY']
            
            print("Payload:", payload)
            print("Chave Secreta:", secret_key)

            token = jwt.encode({
                'user_id': user[0],  # Substitua por sua lógica para obter o ID do usuário
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                }, app.config['SECRET_KEY'], algorithm='HS256')


            print("Token Gerado:", token)

            return jsonify(
                mensagem='Login bem-sucedido.',
                token=token
            ), 200  # 200 OK
        else:
            return jsonify({"error": "Credenciais inválidas."}), 401  # 401 Unauthorized

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request

def verifica_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"error": "Token ausente."}), 401  # 401 Unauthorized

        try:
            decoded_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Adiciona informações do usuário ao contexto da solicitação
            g.user_id = decoded_data['user_id']
            print(f"Token decodificado com sucesso: {decoded_data}")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado."}), 401  # 401 Unauthorized
        except jwt.InvalidTokenError as e:
            print(f"Erro ao decodificar o token: {e}")
            return jsonify({"error": f"Token inválido. Detalhes: {str(e)}"}), 401  # 401 Unauthorized

        return f(*args, **kwargs)

    return decorator

def verifica_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # Verifica se o usuário está autenticado
        if 'user_id' not in g:
            return jsonify({"error": "Usuário não autenticado."}), 401  # 401 Unauthorized

        # Verifica se o usuário é um administrador
        cursor = conexao.cursor()
        read = f"SELECT isAdmin FROM users WHERE userID = {g.user_id}"
        cursor.execute(read)
        user = cursor.fetchone()

        if user and user[0] == 1:  # 1 indica que o usuário é um administrador
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Acesso não autorizado."}), 403  # 403 Forbidden

    return decorator


@app.route('/users/relatorio', methods=['GET'])
# @verifica_token
# @verifica_admin #verifica se o usuário é um admin antes de acessar essa funcionalidade
def list_users():
    try:
        cursor = conexao.cursor()
        read = "SELECT * FROM users WHERE status = 0"
        cursor.execute(read)
        users = cursor.fetchall()

        user_list = []
        for user in users:
            user_list.append({
                'userID': user[0],
                'nome': user[1],
                'email': user[2],
                'isAdmin': bool(user[4])  # Convertendo para booleano
            })

        return jsonify({
            'mensagem': 'Lista de usuários ativos.',
            'usuarios': user_list
        }), 200  # 200 OK

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Internal Server Error

@app.route('/users/perfil', methods=['POST'])
# @verifica_token
# @verifica_admin #verifica se o usuário é um admin antes de acessar essa funcionalidade
def profile_users():
    dados_user = request.get_json()
    try:
        cursor = conexao.cursor()
        update = "UPDATE users SET nome = %s, email = %s, senha = %s, tipo = %s WHERE userID = %s"
        cursor.execute(update, (dados_user['nome'], dados_user['email'], dados_user['senha'], dados_user['tipo'], dados_user['userID']))

        conexao.commit()

        return jsonify({
            'mensagem': 'Perfil do usuário atualizado com sucesso.',
            'usuario': dados_user
        }), 200  # 200 OK

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Internal Server Error
 

#SOFT DELETE
@app.route('/users/banidos', methods=['DELETE'])
# @verifica_token
# @verifica_admin #verifica se o usuário é um admin antes de acessar essa funcionalidade
def ban_users():
    dados_user = request.get_json()
    try:
        cursor = conexao.cursor()
        delete = "UPDATE users SET status = 1 WHERE userID = %s"
        cursor.execute(delete, (dados_user['userID'],))

        conexao.commit()

        return jsonify({
            'mensagem': 'Usuário banido com sucesso.',
            'usuarios': dados_user
        }), 200  # 200 OK

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 500 Internal Server Error

#-----------ITENS------------------------------------------------------------------------------------
@app.route('/itens', methods=['GET'])
def get_itens():

    cursor = conexao.cursor()
    read = f"SELECT * FROM itens WHERE status = 0"
    cursor.execute(read)
    meus_itens = cursor.fetchall()

    itens = list()
    for item in meus_itens:
        itens.append(
            {
                'itemID': item[0],
                'titulo': item[1],
                'autor': item[2],
                'preco': item[3],
                'descricao': item[4],
                'periodicidade': item[5],
                'dataEdicao': item[6],
                'userID': item[7],
                'categoriaID': item[8],
                'status': item[9]
            }
        )

    return make_response(
        jsonify (
            mensagem='Lista de itens.',
            dados=itens
            )
        )


@app.route('/itens', methods=['POST'])
def create_item():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        item = request.get_json()

        # Adicione o novo item à lista
        cursor = conexao.cursor()
        create = f"INSERT INTO itens (titulo, autor, preco, descricao, periodicidade, dataEdicao, userID, categoriaID, isbn) VALUES ('{item['titulo']}', '{item['autor']}', '{item['preco']}', '{item['descricao']}', '{item['periodicidade']}', '{item['dataEdicao']}', '{item['userID']}', '{item['categoriaID']}', '{item['isbn']}')"
        cursor.execute(create)
        conexao.commit()

        # Retorne o item criado
        return jsonify(
            mensagem='Livro adicionado com sucesso.',
            álbum=item
            ), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request
    
@app.route('/itens', methods=['PUT'])
def update_item():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        item = request.get_json()

        # Atualiza o item 
        cursor = conexao.cursor()

        update = f"UPDATE itens SET titulo = '{item['titulo']}', autor = '{item['autor']}', preco = '{item['preco']}', descricao = '{item['descricao']}', periodicidade = '{item['periodicidade']}', dataEdicao = '{item['dataEdicao']}', userID = '{item['userID']}', categoriaID = '{item['categoriaID']}' WHERE isbn = '{item['isbn']}'"
        cursor.execute(update)
        conexao.commit()

        # Retorne o item criado
        return jsonify(
            mensagem='Livro atualizado com sucesso.',
            álbum=item
            ), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request

@app.route('/itens/isbn', methods=['PUT'])
def update_isbn():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        item = request.get_json()

        # Atualiza o item 
        cursor = conexao.cursor()

        update = f"UPDATE itens SET isbn = '{item['isbn']}' WHERE titulo = '{item['titulo']}'"
        cursor.execute(update)
        conexao.commit()

        # Retorne o item criado
        return jsonify(
            mensagem='ISBN atualizada com sucesso.',
            álbum=item
            ), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request


@app.route('/itens', methods=['DELETE'])
def delete_item():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        item = request.get_json()

        # Deleta o registro do item mas mantem os dados no banco de dados
        cursor = conexao.cursor()

        delete = f"UPDATE itens SET status = 1 WHERE titulo = '{item['titulo']}'"
        cursor.execute(delete)
        conexao.commit()

        # Confirma a exclusão da categoria
        return jsonify(
            mensagem='Livro excluído com sucesso.'
            ), 201  # 201 Created
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request


#-----------CATEGORIAS-----------------------------------------------------------------------------------------------
@app.route('/categorias', methods=['GET'])
def get_categorias():

    cursor = conexao.cursor()
    read = f"SELECT * FROM categorias WHERE status = 0"
    cursor.execute(read)
    meus_categorias = cursor.fetchall()

    categorias = list()
    for categoria in meus_categorias:
        categorias.append(
            {
                'categoriaID': categoria[0],
                'nomeCategoria': categoria[1],
                'status': categoria[2]
            }
        )

    return make_response(
        jsonify (
            mensagem='Lista de categorias.',
            dados=categorias
            )
        )


@app.route('/categorias', methods=['POST'])
def create_categoria():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        categoria = request.get_json()

        # Adicione a nova categoria à lista
        cursor = conexao.cursor()
        create = f"INSERT INTO categorias (nomecategoria) VALUES ('{categoria['nomeCategoria']}')"
        cursor.execute(create)
        conexao.commit()

        # Retorna a categoria criada
        return jsonify(
            mensagem='Categoria adicionada com sucesso.',
            categoria=categoria
            ), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request
    
@app.route('/categorias', methods=['PUT'])
def update_categoria():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        categoria = request.get_json()

        # Atualiza a categoria
        cursor = conexao.cursor()

        update = f"UPDATE categorias SET nomeCategoria = '{categoria['nomeCategoria']}' WHERE categoriaID = '{categoria['categoriaID']}'"
        cursor.execute(update)
        conexao.commit()

        # Retorne a categoria criada
        return jsonify(
            mensagem='Categoria atualizada com sucesso.',
            álbum=categoria
            ), 201  # 201 Created

    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request

@app.route('/categorias', methods=['DELETE'])
def delete_categoria():
    try:
        # Obtenha os dados do corpo da solicitação como JSON
        categoria = request.get_json()

         # Deleta o registro da categoria mas mantem os dados no banco de dados
        cursor = conexao.cursor()

        delete = f"UPDATE categorias SET status = 1 WHERE nomeCategoria = '{categoria['nomeCategoria']}'"
        cursor.execute(delete)
        conexao.commit()

        # Confirma a exclusão da categoria
        return jsonify(
            mensagem='Categoria excluída com sucesso.'
            ), 201  # 201 Created


    except Exception as e:
        return jsonify({"error": str(e)}), 400  # 400 Bad Request

if __name__ == '__main__':
    app.run(debug=True)