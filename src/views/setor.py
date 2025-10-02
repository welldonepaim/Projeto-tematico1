# src/views/setor.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Listbox, messagebox, simpledialog
from src import db
import os
import json

ARQUIVO = "setores.json"

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

# ===== Aba Setor =====
class AbaSetor:
    setores = []

    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Setores")

        # Lista usada para exibição (filtrada)
        self.setores_exibidos = AbaSetor.setores.copy()

        # ===== Menu de ações =====
        menu_frame1 = tb.Frame(self.frame)
        menu_frame1.pack(fill="x", pady=5)
        tb.Button(menu_frame1, text="Criar Setor", bootstyle=SUCCESS, command=self.mostrar_criar_setor).pack(side=LEFT, padx=5)
        tb.Button(menu_frame1, text="Alterar Responsável", bootstyle=INFO, command=self.alterar_responsavel_lista).pack(side=LEFT, padx=5)
        tb.Button(menu_frame1, text="Remover Responsável", bootstyle=DANGER, command=self.remover_responsavel_lista).pack(side=LEFT, padx=5)

        menu_frame2 = tb.Frame(self.frame)
        menu_frame2.pack(fill="x", pady=5)
        tb.Button(menu_frame2, text="Renomear Setor", bootstyle=INFO, command=self.renomear_setor).pack(side=LEFT, padx=5)
        tb.Button(menu_frame2, text="Remover Setor", bootstyle=DANGER, command=self.remover_setor).pack(side=LEFT, padx=5)

        # ===== Pesquisa =====
        tb.Label(self.frame, text="Pesquisar Setor:").pack(pady=(10,0))
        self.entry_pesquisa = tb.Entry(self.frame, width=30)
        self.entry_pesquisa.pack(pady=5)
        self.entry_pesquisa.bind("<KeyRelease>", self.pesquisar_setor)

        # ===== Lista de setores =====
        self.lista_setores = Listbox(self.frame, width=60)
        self.lista_setores.pack(pady=10, fill="both", expand=True)
        self.lista_setores.bind("<Button-3>", self.mostrar_menu_contexto)

        # ===== Frame dinâmico para criação de setor =====
        self.criar_frame = tb.Frame(self.frame)
        self.criar_frame.pack_forget()  # começa escondido

        tb.Label(self.criar_frame, text="Nome do Setor:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nome = tb.Entry(self.criar_frame, width=30)
        self.entry_nome.grid(row=0, column=1, pady=2)

        tb.Label(self.criar_frame, text="Responsável:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_responsavel = tb.Entry(self.criar_frame, width=30)
        self.entry_responsavel.grid(row=1, column=1, pady=2)

        # Botões OK e Cancelar
        btn_frame = tb.Frame(self.criar_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        tb.Button(btn_frame, text="OK", bootstyle=SUCCESS, command=self.criar_setor).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle=DANGER, command=lambda: self.criar_frame.pack_forget()).pack(side=LEFT, padx=5)

        # Carrega dados existentes
        self.carregar_dados()

    # ===== Persistência =====
    def carregar_dados(self):
        setores_db = db.listar_setores()
        AbaSetor.setores = [Setor(id, nome, responsavel) for id, nome, responsavel in setores_db]
        self.setores_exibidos = AbaSetor.setores.copy()
        self.atualizar_lista()


    def salvar_dados(self):
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump([s.__dict__ for s in AbaSetor.setores], f, indent=4, ensure_ascii=False)

    # ===== Funções de interface =====
    def atualizar_lista(self, setores=None):
        self.lista_setores.delete(0, tb.END)
        for s in (setores if setores is not None else self.setores_exibidos):
            self.lista_setores.insert(tb.END, str(s))

    def mostrar_criar_setor(self):
        self.entry_nome.delete(0, tb.END)
        self.entry_responsavel.delete(0, tb.END)
        self.criar_frame.pack(pady=5, fill="x")

    def criar_setor(self):
        nome = self.entry_nome.get().strip()
        responsavel = self.entry_responsavel.get().strip()
        if nome:
            db.inserir_setor(nome, responsavel if responsavel else None)
            self.entry_nome.delete(0, tb.END)
            self.entry_responsavel.delete(0, tb.END)
            self.criar_frame.pack_forget()
            self.carregar_dados()
        else:
            messagebox.showwarning("Atenção", "Digite um nome válido!")

    def mostrar_menu_contexto(self, event):
        try:
            idx = self.lista_setores.nearest(event.y)
            self.lista_setores.selection_clear(0, tb.END)
            self.lista_setores.selection_set(idx)
        except IndexError:
            pass

  

    def pesquisar_setor(self, event):
        termo = self.entry_pesquisa.get().strip().lower()
        if termo:
            self.setores_exibidos = [s for s in AbaSetor.setores if termo in s.nome.lower()]
        else:
            self.setores_exibidos = AbaSetor.setores.copy()
        self.atualizar_lista()

    def alterar_responsavel_lista(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            novo_resp = simpledialog.askstring("Alterar responsável", f"Novo responsável para {setor.nome}:")
            if novo_resp:
                db.atualizar_setor(setor.id, responsavel=novo_resp)
                self.carregar_dados()

    def remover_responsavel_lista(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            db.atualizar_setor(setor.id, responsavel=None)
            self.carregar_dados()

    def renomear_setor(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            novo_nome = simpledialog.askstring("Renomear Setor", f"Novo nome para {setor.nome}:")
            if novo_nome:
                db.atualizar_setor(setor.id, nome=novo_nome)
                self.carregar_dados()

    def remover_setor(self):
        sel = self.lista_setores.curselection()
        if sel:
            setor = self.setores_exibidos[sel[0]]
            if messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o setor {setor.nome}?"):
                db.desativar_setor(setor.id)  # apenas desativa
                self.carregar_dados()


