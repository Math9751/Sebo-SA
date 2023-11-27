from flask import Flask, make_response, jsonify, request
import mysql.connector

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='H@pp!n3$',
    database='db_sebo',
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False 

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
        create = f"INSERT INTO itens (titulo, autor, preco, descricao, periodicidade, dataEdicao, userID, categoriaID) VALUES ('{item['titulo']}', '{item['autor']}', '{item['preco']}', '{item['descricao']}', '{item['periodicidade']}', '{item['dataEdicao']}', '{item['userID']}', '{item['categoriaID']}')"
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

        update = f"UPDATE itens SET titulo = '{item['titulo']}', autor = '{item['autor']}', preco = '{item['preco']}', descricao = '{item['descricao']}', periodicidade = '{item['periodicidade']}', dataEdicao = '{item['dataEdicao']}', userID = '{item['userID']}', categoriaID = '{item['categoriaID']}', WHERE id = '{item['itemID']}'"
        cursor.execute(update)
        conexao.commit()

        # Retorne o item criado
        return jsonify(
            mensagem='Livro atualizado com sucesso.',
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
            álbum=categoria
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

        update = f"UPDATE categorias SET nomeCategoria = '{categoria['nomeCategoria']}' WHERE id = '{categoria['categoriaID']}'"
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