from src.model import session
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from src.dao import db  # importa o módulo session
from src.model.usuario import Usuario
from src.dao import usuario_dao

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
        if usuario_logado.perfil not in ("Administrador", "Gestor"):
            messagebox.showwarning("Atenção", "Acesso restrito: apenas Administrador ou Gestor pode realizar esta ação.")
            return False
        return True

    def _montar_formulario(self):
        labels = ["Nome", "Login (E-mail)", "Senha", "Contato", "Perfil", "Status"]

        for i, label in enumerate(labels):
            tb.Label(self.frame, text=label + ":", anchor="w").grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if label == "Perfil":
                combo = tb.Combobox(self.frame, values=["Administrador", "Técnico", "Gestor", "Usuário"], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo
            elif label == "Status":
                combo = tb.Combobox(self.frame, values=["Ativo", "Inativo"], state="readonly")
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
        frame_botoes_form = tb.Frame(self.frame)
        frame_botoes_form.grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")

        self.btn_salvar = tb.Button(frame_botoes_form, text="Salvar Usuário", bootstyle=SUCCESS, command=self.salvar)
        self.btn_salvar.pack(side=LEFT, expand=True, fill="x", padx=5)

        self.btn_cancelar = tb.Button(frame_botoes_form, text="Cancelar", bootstyle=SECONDARY, command=self.cancelar_edicao)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)
        self.btn_cancelar.pack_forget()  # esconde inicialmente

    def _montar_tabela(self):
        # campo de pesquisa linha 7 
        frame_pesquisa = tb.Frame(self.frame)
        frame_pesquisa.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")

        tb.Label(frame_pesquisa, text="Pesquisar:").pack(side=LEFT, padx=5)
        self.entry_pesquisa = tb.Entry(frame_pesquisa)
        self.entry_pesquisa.pack(side=LEFT, fill="x", expand=True, padx=5)

        tb.Button(frame_pesquisa, text="Buscar", bootstyle=INFO, command=self.pesquisar_usuario).pack(side=LEFT, padx=5)
        tb.Button(frame_pesquisa, text="Limpar", bootstyle=SECONDARY, command=self.carregar_dados).pack(side=LEFT, padx=5)

        # tabela (linha 8)
        colunas = ("ID", "Nome", "Login", "Perfil", "Contato", "Status")
        self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # ----------------- Cores alternadas -----------------
        self.tree.tag_configure('par', background='#f2f2f2')   # cinza claro
        self.tree.tag_configure('impar', background='white')    # branco
        # -----------------------------------------------------

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(8, weight=1)

        # botoes da tabela (linha 9)
        frame_botoes = tb.Frame(self.frame)
        frame_botoes.grid(row=9, column=0, columnspan=2, pady=10)

        tb.Button(frame_botoes, text="Editar Usuário", bootstyle=WARNING, command=self.editar_usuario).pack(side=LEFT, padx=5)
        tb.Button(frame_botoes, text="Excluir Usuário", bootstyle=DANGER, command=self.excluir_usuario).pack(side=LEFT, padx=5)

    def pesquisar_usuario(self):
        termo = self.entry_pesquisa.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        usuarios = usuario_dao.listar_usuarios()
        filtrados = [
            u for u in usuarios
            if termo in (u.nome or "").lower()
            or termo in (u.login or "").lower()
            or termo in (u.contato or "").lower()
        ]

        for usuario in filtrados:
            self.tree.insert("", "end", values=(
                usuario.id, usuario.nome, usuario.login,
                usuario.perfil, usuario.contato, usuario.status
            ))

    # def _montar_tabela(self):
    #     colunas = ("ID", "Nome", "Login", "Perfil", "Contato", "Status")
    #     self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
    #     for col in colunas:
    #         self.tree.heading(col, text=col)
    #         self.tree.column(col, width=120, anchor="center")
    #     self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    #     self.frame.columnconfigure(1, weight=1)
    #     self.frame.rowconfigure(7, weight=1)

    #     frame_botoes = tb.Frame(self.frame)
    #     frame_botoes.grid(row=8, column=0, columnspan=2, pady=10)

    #     tb.Button(frame_botoes, text="Editar Usuário", bootstyle=WARNING, command=self.editar_usuario).pack(side=LEFT, padx=5)
    #     tb.Button(frame_botoes, text="Excluir Usuário", bootstyle=DANGER, command=self.excluir_usuario).pack(side=LEFT, padx=5)

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        usuarios = usuario_dao.listar_usuarios()
        for i, usuario in enumerate(usuarios):
            tag = 'par' if i % 2 == 0 else 'impar'
            self.tree.insert("", "end", values=(
                usuario.id, usuario.nome, usuario.login,
                usuario.perfil, usuario.contato, usuario.status
            ), tags=(tag,))


    def editar_usuario(self):
        if not self._verificar_permissao():
            return

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para editar.")
            return

        # pega o id a partir do primeiro valor da linha (garantir que é o id)
        item = self.tree.item(selecionado[0])
        valores = item.get("values", [])
        if not valores:
            messagebox.showerror("Erro", "Dados da linha inválidos.")
            return

        try:
            usuario_id = int(valores[0])
        except Exception:
            usuario_id = valores[0]  # fallback, se for string

        # busca objeto Usuario no DAO — mais seguro que confiar apenas em `values`
        usuario = usuario_dao.buscar_usuario_por_id(usuario_id)
        if not usuario:
            messagebox.showerror("Erro", "Usuário não encontrado no banco.")
            return

        # preenche o formulário com o objeto recuperado
        self.usuario_em_edicao["id"] = usuario.id
        self.entries["Nome"].delete(0, "end")
        self.entries["Nome"].insert(0, usuario.nome or "")
        self.entries["Login (E-mail)"].delete(0, "end")
        self.entries["Login (E-mail)"].insert(0, usuario.login or "")
        # não mostramos a senha por segurança — campo fica vazio
        self.entries["Senha"].delete(0, "end")
        self.entries["Perfil"].set(usuario.perfil or "")
        self.entries["Contato"].delete(0, "end")
        self.entries["Contato"].insert(0, usuario.contato or "")
        self.entries["Status"].set(usuario.status or "")

        self.btn_salvar.config(text="Atualizar Usuário", bootstyle=WARNING)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)

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
                usuario_dao.excluir_usuario(usuario_id)
                self.carregar_dados()
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir: {e}")

    def salvar(self):
        if not self._verificar_permissao():
            return

        usuario = Usuario(
            id=self.usuario_em_edicao["id"],
            nome=self.entries["Nome"].get(),
            login=self.entries["Login (E-mail)"].get(),
            senha=self.entries["Senha"].get(),
            perfil=self.entries["Perfil"].get(),
            contato=self.entries["Contato"].get(),
            status=self.entries["Status"].get()
        )

        if not (usuario.nome and usuario.login and usuario.perfil and usuario.status):
            messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
            return

        try:
            if usuario.id:
                # se senha estiver vazia, mantém a antiga
                if not usuario.senha:
                    antigo = usuario_dao.buscar_usuario_por_id(usuario.id)
                    usuario.senha = antigo.senha

                usuario_dao.atualizar_usuario(usuario)
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                self.usuario_em_edicao["id"] = None
                self.btn_salvar.config(text="Salvar Usuário", bootstyle=SUCCESS)
                self.btn_cancelar.pack_forget()
            else:
                usuario_dao.inserir_usuario(usuario)
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            
            self.limpar_formulario()
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar: {e}")

    def limpar_formulario(self):
        for entry in self.entries.values():
            if isinstance(entry, tb.Entry):
                entry.delete(0, "end")
            elif isinstance(entry, tb.Combobox):
                entry.set("")
        self.usuario_em_edicao["id"] = None

    def cancelar_edicao(self):
        """Cancela edição e reseta formulário"""
        self.limpar_formulario()
        self.btn_salvar.config(text="Salvar Usuário", bootstyle=SUCCESS)
        self.btn_cancelar.pack_forget()
