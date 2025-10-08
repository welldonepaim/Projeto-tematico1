import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox,simpledialog
from src.dao import setor_dao, usuario_dao
from src.model.setor import Setor

class AbaSetor:
    setores = []

    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Setores")

        self.setores_exibidos = AbaSetor.setores.copy()
        self.setor_em_edicao = {"id": None}

        # Montar os componentes
        self._montar_formulario_criacao()
        self._montar_botoes_acoes()
        self._montar_pesquisa()
        self._montar_tabela()

        self.carregar_dados()

    # ----------------- Formulário de criação/edição -----------------
    def _montar_formulario_criacao(self):
        self.frame_form = tb.Frame(self.frame)
        self.frame_form.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        self.frame_form.grid_remove()  # esconde inicialmente

        tb.Label(self.frame_form, text="Nome do Setor:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_nome = tb.Entry(self.frame_form)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        btn_frame = tb.Frame(self.frame_form)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        tb.Button(btn_frame, text="OK", bootstyle=SUCCESS, command=self.criar_ou_atualizar_setor).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle=SECONDARY, command=lambda: self.frame_form.grid_remove()).pack(side=LEFT, padx=5)

        self.frame.columnconfigure(1, weight=1)

    # ----------------- Botões de ações -----------------
    def _montar_botoes_acoes(self):
        self.frame_botoes = tb.Frame(self.frame)
        self.frame_botoes.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        tb.Button(self.frame_botoes, text="Criar Setor", bootstyle=SUCCESS, width=15, command=self.mostrar_formulario).pack(side=LEFT, padx=5)
        tb.Button(self.frame_botoes, text="Renomear Setor", bootstyle=INFO, width=15, command=self.renomear_setor).pack(side=LEFT, padx=5)
        tb.Button(self.frame_botoes, text="Remover Setor", bootstyle=DANGER, width=15, command=self.remover_setor).pack(side=LEFT, padx=5)
        tb.Button(self.frame_botoes, text="Alterar Responsável", bootstyle=INFO, width=18, command=self.alterar_responsavel).pack(side=LEFT, padx=5)
        tb.Button(self.frame_botoes, text="Remover Responsável", bootstyle=DANGER, width=18, command=self.remover_responsavel).pack(side=LEFT, padx=5)

    # ----------------- Pesquisa -----------------
    def _montar_pesquisa(self):
        tb.Label(self.frame, text="Pesquisar Setor:").grid(row=2, column=0, sticky="w", padx=5)
        self.entry_pesquisa = tb.Entry(self.frame)
        self.entry_pesquisa.grid(row=2, column=1, sticky="ew", padx=5)
        self.entry_pesquisa.bind("<KeyRelease>", self.pesquisar_setor)

    # ----------------- Tabela -----------------
    def _montar_tabela(self):
        colunas = ("ID", "Nome", "Responsável")
        self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.tree.tag_configure('par', background='#f2f2f2')
        self.tree.tag_configure('impar', background='white')

        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(1, weight=1)

    # ----------------- Carregar dados -----------------
    def carregar_dados(self):
        setores_db = setor_dao.listar_setores()
        AbaSetor.setores = setores_db
        self.setores_exibidos = AbaSetor.setores.copy()
        self.atualizar_tabela()

    def atualizar_tabela(self, setores=None):
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(setores if setores is not None else self.setores_exibidos):
            tag = 'par' if i % 2 == 0 else 'impar'
            self.tree.insert("", "end", values=(s.id, s.nome, getattr(s, 'responsavel', '')), tags=(tag,))

    # ----------------- Pesquisa -----------------
    def pesquisar_setor(self, event=None):
        termo = self.entry_pesquisa.get().strip().lower()
        if termo:
            self.setores_exibidos = [s for s in AbaSetor.setores if termo in s.nome.lower()]
        else:
            self.setores_exibidos = AbaSetor.setores.copy()
        self.atualizar_tabela()

    # ----------------- Formulário -----------------
    def mostrar_formulario(self):
        self.entry_nome.delete(0, tb.END)
        self.setor_em_edicao["id"] = None
        self.frame_form.grid(pady=5, sticky="ew")

    def criar_ou_atualizar_setor(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite um nome válido!")
            return

        if self.setor_em_edicao["id"]:
            setor_dao.atualizar_setor(self.setor_em_edicao["id"], nome=nome)
            messagebox.showinfo("Sucesso", "Setor atualizado!")
        else:
            setor_dao.inserir_setor(nome, None)
            messagebox.showinfo("Sucesso", "Setor criado!")

        self.frame_form.grid_remove()
        self.carregar_dados()

    # ----------------- Ações -----------------
    def renomear_setor(self):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            setor_id = item["values"][0]
            novo_nome = simpledialog.askstring("Renomear Setor", "Novo nome do setor:")
            if novo_nome:
                setor_dao.atualizar_setor(setor_id, nome=novo_nome)
                self.carregar_dados()

    def remover_setor(self):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            setor_id = item["values"][0]
            nome = item["values"][1]
            if messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o setor {nome}?"):
                setor_dao.desativar_setor(setor_id)
                self.carregar_dados()

    def alterar_responsavel(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um setor primeiro.")
            return
        item = self.tree.item(sel[0])
        setor_id = item["values"][0]

        win = tb.Toplevel(self.frame)
        win.title("Definir Responsável")
        win.geometry("300x150")
        win.resizable(False, False)

        tb.Label(win, text="Selecione o responsável:").pack(pady=10)

        usuarios = [u.nome for u in usuario_dao.listar_usuarios() if u.perfil.lower() == "usuário"]
        combo_responsavel = tb.Combobox(win, values=usuarios, state="readonly")
        combo_responsavel.pack(pady=5)

        btn_frame = tb.Frame(win)
        btn_frame.pack(pady=10)

        def salvar():
            responsavel_nome = combo_responsavel.get()
            if responsavel_nome:
                setor_dao.atualizar_setor(setor_id, responsavel=responsavel_nome)
                self.carregar_dados()
                win.destroy()
            else:
                messagebox.showwarning("Atenção", "Selecione um responsável!")

        tb.Button(btn_frame, text="Confirmar", bootstyle=SUCCESS, command=salvar).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle=SECONDARY, command=win.destroy).pack(side=LEFT, padx=5)

    def remover_responsavel(self):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            setor_id = item["values"][0]
            setor_dao.atualizar_setor(setor_id, limpar_resp=True)
            self.carregar_dados()

