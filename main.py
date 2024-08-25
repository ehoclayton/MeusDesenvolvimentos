import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='CadastroUsuarios',
            user='root',
            password='20@Fev91'
        )
        if conexao.is_connected():
            print('Conexão bem-sucedida com o banco de dados')
            return conexao
    except Error as e:
        print(f'Erro ao conectar ao banco de dados: {e}')
    return None

def cadastrar_usuario():
    nome = entry_nome.get()
    email = entry_email.get()
    
    if not nome or not email:
        messagebox.showwarning('Aviso', 'Por favor, preencha todos os campos.')
        return

    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            query = "INSERT INTO Usuarios (nome, email) VALUES (%s, %s)"
            valores = (nome, email)
            cursor.execute(query, valores)
            conexao.commit()
            messagebox.showinfo('Cadastro', f'Usuário {nome} cadastrado com sucesso!')
        except Error as e:
            messagebox.showerror('Erro', f'Erro ao cadastrar usuário: {e}')
        finally:
            cursor.close()
            conexao.close()

root = tk.Tk()
root.title('Cadastro de Usuário')

tk.Label(root, text='Nome:').grid(row=0, column=0)
tk.Label(root, text='Email:').grid(row=1, column=0)

entry_nome = tk.Entry(root)
entry_email = tk.Entry(root)
entry_nome.grid(row=0, column=1)
entry_email.grid(row=1, column=1)

tk.Button(root, text='Cadastrar', command=cadastrar_usuario).grid(row=2, column=1)

root.mainloop()
