import tkinter as tk
from tkinter import messagebox, ttk
import db

def iniciar_interface():
    root = tk.Tk()
    root.title("Cadastro de Usuários - SQLite")

    tk.Label(root, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(root)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Email:").grid(row=1, column=0, padx=5, pady=5)
    entry_email = tk.Entry(root)
    entry_email.grid(row=1, column=1, padx=5, pady=5)

    def salvar():
        nome = entry_nome.get()
        email = entry_email.get()
        if nome and email:
            db.inserir_usuario(nome, email)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            entry_nome.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            carregar_dados()
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")

    btn_salvar = tk.Button(root, text="Salvar", command=salvar)
    btn_salvar.grid(row=2, column=0, columnspan=2, pady=10)

    # Tabela para listar os usuários
    tree = ttk.Treeview(root, columns=("ID", "Nome", "Email"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Email", text="Email")
    tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def carregar_dados():
        for item in tree.get_children():
            tree.delete(item)
        for (id_, nome, email) in db.listar_usuarios():
            tree.insert("", tk.END, values=(id_, nome, email))

    carregar_dados()

    root.mainloop()
