import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from src import db, session  # importa o módulo session

class AbaUsuario:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Usuários")

        self.entries = {}
        self.usuario_em_edicao = {"id": None}

        self._montar_formulario()
        self._montar_botoes()
        self._montar_tabela()
        self.carregar_dados()

    def _verificar_permissao(self):
        """Retorna True se usuário for Administrador ou Gestor"""
        usuario_logado = session.get_usuario()
        if not usuario_logado:
            messagebox.showwarning("Atenção", "Você precisa estar logado para realizar esta ação.")
            return False
        if usuario_logado['perfil'] not in ("Administrador", "Gestor"):
            messagebox.showwarning("Atenção", "Acesso restrito: apenas Administrador ou Gestor pode realizar esta ação.")
            return False
        return True

    def _montar_formulario(self):
        labels = ["Nome", "Login (E-mail)", "Senha", "Perfil", "Contato", "Status"]

        for i, label in enumerate(labels):
            tb.Label(self.frame, text=label + ":", anchor="w").grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if label == "Perfil":
                combo = tb.Combobox(self.frame, values=["Administrador", "Técnico", "Gestor", "Usuário"])
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo
            elif label == "Status":
                combo = tb.Combobox(self.frame, values=["Ativo", "Inativo"])
                combo.set("Ativo")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo
            elif label == "Senha":
                entry = tb.Entry(self.frame, show="*")
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry
            else:
                entry = tb.Entry(self.frame)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry

    def _montar_botoes(self):
        self.btn_salvar = tb.Button(self.frame, text="Salvar Usuário", bootstyle=SUCCESS, command=self.salvar)
        self.btn_salvar.grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

    def _montar_tabela(self):
        colunas = ("ID", "Nome", "Login", "Perfil", "Contato", "Status")
        self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(7, weight=1)

        frame_botoes = tb.Frame(self.frame)
        frame_botoes.grid(row=8, column=0, columnspan=2, pady=10)

        tb.Button(frame_botoes, text="Editar Usuário", bootstyle=WARNING, command=self.editar_usuario).pack(side=LEFT, padx=5)
        tb.Button(frame_botoes, text="Excluir Usuário", bootstyle=DANGER, command=self.excluir_usuario).pack(side=LEFT, padx=5)

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for linha in db.listar_usuarios():
            self.tree.insert("", "end", values=linha)

    def salvar(self):
        if not self._verificar_permissao():
            return

        nome = self.entries["Nome"].get()
        login = self.entries["Login (E-mail)"].get()
        senha = self.entries["Senha"].get()
        perfil = self.entries["Perfil"].get()
        contato = self.entries["Contato"].get()
        status = self.entries["Status"].get()

        if not (nome and login and perfil and status):
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
            return

        try:
            if self.usuario_em_edicao["id"]:
                db.atualizar_usuario(self.usuario_em_edicao["id"], nome, login, senha, perfil, contato, status)
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                self.usuario_em_edicao["id"] = None
                self.btn_salvar.config(text="Salvar Usuário", bootstyle=SUCCESS)
            else:
                db.inserir_usuario(nome, login, senha, perfil, contato, status)
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")

            for entry in self.entries.values():
                if isinstance(entry, tb.Entry):
                    entry.delete(0, "end")
                elif isinstance(entry, tb.Combobox):
                    entry.set("")
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar: {e}")

    def editar_usuario(self):
        if not self._verificar_permissao():
            return

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para editar.")
            return
        item = self.tree.item(selecionado[0])
        valores = item["values"]

        self.usuario_em_edicao["id"] = valores[0]
        self.entries["Nome"].delete(0, "end")
        self.entries["Nome"].insert(0, valores[1])
        self.entries["Login (E-mail)"].delete(0, "end")
        self.entries["Login (E-mail)"].insert(0, valores[2])
        self.entries["Senha"].delete(0, "end")
        self.entries["Perfil"].set(valores[3])
        self.entries["Contato"].delete(0, "end")
        self.entries["Contato"].insert(0, valores[4])
        self.entries["Status"].set(valores[5])
        self.btn_salvar.config(text="Atualizar Usuário", bootstyle=WARNING)

    def excluir_usuario(self):
        if not self._verificar_permissao():
            return

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para excluir.")
            return
        item = self.tree.item(selecionado[0])
        valores = item["values"]
        usuario_id = valores[0]

        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o usuário {valores[1]}?"):
            try:
                db.excluir_usuario(usuario_id)
                self.carregar_dados()
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir: {e}")
