# src/view/setor.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Listbox, messagebox, simpledialog
from src.dao.setor_dao import listar_setores
from src.dao import setor_dao, usuario_dao

# ===== Classe Setor =====
class Setor:
    def __init__(self, id, nome, responsavel=None):
        self.id = id
        self.nome = nome
        self.responsavel = responsavel

    def __str__(self):
        if self.responsavel:
            return f"Id:{self.id}, Setor: {self.nome}, Responsável: {self.responsavel}"
        return f"Id:{self.id}, Setor: {self.nome}, Responsável: (não definido)"

    def alterar_responsavel(self, novo_responsavel):
        self.responsavel = novo_responsavel

    def remover_responsavel(self):
        self.responsavel = None

    def alterar_nome(self, novo_nome):
        self.nome = novo_nome


# ===== Classe AbaSetor =====
class AbaSetor:
    setores = []

    def __init__(self, notebook):
        # ===== Inicialização da aba =====
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Setores")

        # Lista usada para exibição (filtrada)
        self.setores_exibidos = AbaSetor.setores.copy()

        # ===== Criação dos frames permanentes =====
        self._criar_menu_acoes()
        self._criar_pesquisa()
        self._criar_lista_setores()
        self._criar_frame_criar_setor()

        # Carrega dados existentes
        self.carregar_dados()


    def _criar_menu_acoes(self):
        menu_frame1 = tb.Frame(self.frame)
        menu_frame1.pack(fill="x", pady=(5,2))
        tb.Button(menu_frame1, text="Criar Setor", bootstyle=SUCCESS, width=15,
                  command=self.mostrar_criar_setor).pack(side=LEFT, padx=5)
        tb.Button(menu_frame1, text="Alterar Responsável", bootstyle=INFO, width=18,
                  command=self.alterar_responsavel_lista).pack(side=LEFT, padx=5)
        tb.Button(menu_frame1, text="Remover Responsável", bootstyle=DANGER, width=18,
                  command=self.remover_responsavel_lista).pack(side=LEFT, padx=5)

        menu_frame2 = tb.Frame(self.frame)
        menu_frame2.pack(fill="x", pady=(2,5))
        tb.Button(menu_frame2, text="Renomear Setor", bootstyle=INFO, width=18,
                  command=self.renomear_setor).pack(side=LEFT, padx=5)
        tb.Button(menu_frame2, text="Remover Setor", bootstyle=DANGER, width=18,
                  command=self.remover_setor).pack(side=LEFT, padx=5)

    def _criar_pesquisa(self):
        tb.Label(self.frame, text="Pesquisar Setor:").pack(pady=(10, 0))
        self.entry_pesquisa = tb.Entry(self.frame, width=30)
        self.entry_pesquisa.pack(pady=5)
        self.entry_pesquisa.bind("<KeyRelease>", self.pesquisar_setor)

    def _criar_lista_setores(self):
        self.lista_setores = Listbox(self.frame, width=60)
        self.lista_setores.pack(pady=10, fill="both", expand=True)
        self.lista_setores.bind("<Button-3>", self.mostrar_menu_contexto)

    def _criar_frame_criar_setor(self):
        self.criar_frame = tb.Frame(self.frame)
        self.criar_frame.pack_forget()

        tb.Label(self.criar_frame, text="Nome do Setor:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nome = tb.Entry(self.criar_frame, width=30)
        self.entry_nome.grid(row=0, column=1, pady=2)

        btn_frame = tb.Frame(self.criar_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        tb.Button(btn_frame, text="OK", bootstyle=SUCCESS, command=self.criar_setor).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle=DANGER,
                  command=lambda: self.criar_frame.pack_forget()).pack(side=LEFT, padx=5)

    # ===== Funções auxiliares =====
    def carregar_dados(self):
        setores_db = listar_setores()
        AbaSetor.setores = [Setor(id, nome, responsavel) for id, nome, responsavel in setores_db]
        self.setores_exibidos = AbaSetor.setores.copy()
        self.atualizar_lista()

    def atualizar_lista(self, setores=None):
        self.lista_setores.delete(0, tb.END)
        for s in (setores if setores is not None else self.setores_exibidos):
            self.lista_setores.insert(tb.END, str(s))

    def pesquisar_setor(self, event=None):
        termo = self.entry_pesquisa.get().strip().lower()
        if termo:
            self.setores_exibidos = [s for s in AbaSetor.setores if termo in s.nome.lower()]
        else:
            self.setores_exibidos = AbaSetor.setores.copy()
        self.atualizar_lista()

    def mostrar_menu_contexto(self, event):
        try:
            idx = self.lista_setores.nearest(event.y)
            self.lista_setores.selection_clear(0, tb.END)
            self.lista_setores.selection_set(idx)
        except IndexError:
            pass

    # ===== Ações dos botões =====
    def mostrar_criar_setor(self):
        self.entry_nome.delete(0, tb.END)
        self.criar_frame.pack(pady=5, fill="x")

    def criar_setor(self):
        nome = self.entry_nome.get().strip()
        if nome:
            setor_dao.inserir_setor(nome, None)
            self.entry_nome.delete(0, tb.END)
            self.criar_frame.pack_forget()
            self.carregar_dados()
        else:
            messagebox.showwarning("Atenção", "Digite um nome válido!")

    def alterar_responsavel_lista(self):
        sel = self.lista_setores.curselection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um setor primeiro.")
            return
        setor = self.setores_exibidos[sel[0]]

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
                setor_dao.atualizar_setor(setor.id, responsavel=responsavel_nome)
                self.carregar_dados()
                win.destroy()
            else:
                messagebox.showwarning("Atenção", "Selecione um responsável!")

        tb.Button(btn_frame, text="Confirmar", bootstyle=SUCCESS, command=salvar).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle=DANGER, command=win.destroy).pack(side=LEFT, padx=5)

    def remover_responsavel_lista(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            setor_dao.atualizar_setor(setor.id, limpar_resp=True)
            self.carregar_dados()

    def renomear_setor(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            novo_nome = simpledialog.askstring("Renomear Setor", f"Novo nome para {setor.nome}:")
            if novo_nome:
                setor_dao.atualizar_setor(setor.id, nome=novo_nome)
                self.carregar_dados()

    def remover_setor(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            if messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o setor {setor.nome}?"):
                setor_dao.desativar_setor(setor.id)
                self.carregar_dados()

