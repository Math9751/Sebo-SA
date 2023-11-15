import mysql.connector

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='H@pp!n3$',
    database='db_sebo',
)

cursor = conexao.cursor()

# # CREATE itens
# titulo = 'O Corvo'
# autor = 'Edgar Allan Poe'
# preco = 58.90
# descricao = 'Poema'
# status = 1
# periodicidade = 'mensal'
# dataEdicao = 20201214
# area = 4
# vendedor = 2
# categoria = 4
# comando = f'INSERT INTO itens (titulo, autor, preco, descricao, status, periodicidade, dataEdicao, area, userID, categoriaID) VALUES ("{titulo}", "{autor}", {preco}, "{descricao}", {status}, "{periodicidade}", {dataEdicao}, {area}, {vendedor}, {categoria})'
# cursor.execute(comando)
# conexao.commit() #edita o banco de dados
# resultado = cursor.fetchall() #lê o banco de dados

# CREATE users
# nome = 
# email = 
# senha = 
# tipo = 
# status =
# comando = f'INSERT INTO users (nome, email, senha, tipo, tipoID, status) VALUES ("Matheus Silva", "matheus.correia@aluno.ifsp.edu.br", SHA2("63557", 256), "Vendedor", 2, 1)' #cadastro do usuário no banco de dados com senha criptografa com hash de 256 bytes
# cursor.execute(comando)
# conexao.commit() #edita o banco de dados
# resultado = cursor.fetchall() #lê o banco de dados

# READ transações
# comando = f'SELECT * FROM transacions where userId = 1'
# cursor.execute(comando)
# resultado = cursor.fetchall() #lê o banco de dados
# print(resultado)



# UPDATE
titulo = "O Corvo"
preco = 54.90
comando = f'UPDATE itens SET preco = {preco} WHERE titulo = "{titulo}"'
cursor.execute(comando)
conexao.commit()


# DELETE
# titulo = "O Corvo"
# comando = f'DELETE FROM itens WHERE titulo = "{titulo}"'
# cursor.execute(comando)
# conexao.commit()

cursor.close()
conexao.close()