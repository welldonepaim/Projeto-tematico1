import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from src.dao import setor_dao, usuario_dao

class AbaSetor:
    setores = []

    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Setores")

        self.entries = {}
        self.setores_exibidos = AbaSetor.setores.copy()
        self.setor_em_edicao = {"id": None}

        # Montar componentes
        self._montar_formulario()
        self._montar_botoes_acoes()
        self._montar_pesquisa()
        self._montar_tabela()
        self._montar_botoes_tabela()

        self.carregar_dados()

    # ----------------- Formulário -----------------
    def _montar_formulario(self):
        labels = ["Nome do setor", "Responsável"]
        for i, label in enumerate(labels):
            tb.Label(self.frame, text=label + ":", anchor="w").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            if label == "Responsável":
                combo_usuario = tb.Combobox(self.frame, state="readonly")
                combo_usuario.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo_usuario
            else:
                entry = tb.Entry(self.frame)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry

        self.frame.columnconfigure(1, weight=1)
        self._atualizar_responsaveis()  # preencher combobox

    # ----------------- Atualizar lista de responsáveis -----------------
    def _atualizar_responsaveis(self):
        combo = self.entries.get("Responsável")
        if combo:
            usuarios = usuario_dao.listar_usuarios()
            nomes_usuarios = ["Nenhum"] + [u.nome for u in usuarios]
            nomes_usuarios = [u.nome for u in usuarios]
            combo['values'] = nomes_usuarios
            if nomes_usuarios:
                combo.set("Nenhum")

    # ----------------- Botões de ações do formulário -----------------
    def _montar_botoes_acoes(self):
        frame_botoes_form = tb.Frame(self.frame)
        frame_botoes_form.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        self.btn_salvar = tb.Button(frame_botoes_form, text="Salvar Setor", bootstyle=SUCCESS, command=self.criar_ou_atualizar_setor)
        self.btn_salvar.pack(side=LEFT, expand=True, fill="x", padx=5)

        self.btn_cancelar = tb.Button(frame_botoes_form, text="Cancelar", bootstyle=SECONDARY, command=self.cancelar_edicao)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)
        self.btn_cancelar.pack_forget()

    # ----------------- Pesquisa -----------------
    def _montar_pesquisa(self):
        frame_pesquisa = tb.Frame(self.frame)
        frame_pesquisa.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        tb.Label(frame_pesquisa, text="Pesquisar Setor:").pack(side=LEFT, padx=5)
        self.entry_pesquisa = tb.Entry(frame_pesquisa)
        self.entry_pesquisa.pack(side=LEFT, fill="x", expand=True, padx=5)
        self.entry_pesquisa.bind("<KeyRelease>", self.pesquisar_setor)

        tb.Button(frame_pesquisa, text="Buscar", bootstyle=INFO, command=self.pesquisar_setor).pack(side=LEFT, padx=5)
        tb.Button(frame_pesquisa, text="Limpar", bootstyle=SECONDARY, command=self.carregar_dados).pack(side=LEFT, padx=5)

    # ----------------- Tabela -----------------
    def _montar_tabela(self):
        colunas = ("ID", "Nome", "Responsável")
        self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.tree.tag_configure('par', background='#f2f2f2')
        self.tree.tag_configure('impar', background='white')

        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(1, weight=1)

    # ----------------- Botões Editar / Excluir abaixo da tabela -----------------
    def _montar_botoes_tabela(self):
        frame_botoes = tb.Frame(self.frame)
        frame_botoes.grid(row=5, column=0, columnspan=2, pady=5)

        tb.Button(frame_botoes, text="Editar Setor", bootstyle=WARNING, command=self.editar_setor).pack(side=LEFT, padx=5)
        tb.Button(frame_botoes, text="Excluir Setor", bootstyle=DANGER, command=self.remover_setor).pack(side=LEFT, padx=5)

    # ----------------- Carregar dados -----------------
    def carregar_dados(self):
        AbaSetor.setores = setor_dao.listar_setores()
        self.setores_exibidos = AbaSetor.setores.copy()
        self._atualizar_responsaveis()
        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(self.setores_exibidos):
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

    # ----------------- Formulário e ações -----------------
    def criar_ou_atualizar_setor(self):
        nome = self.entries["Nome do setor"].get().strip()
        responsavel = self.entries["Responsável"].get().strip()
        if responsavel == "Nenhum":
            responsavel = None  # interpreta "Nenhum" como None

        if not nome:
            messagebox.showwarning("Atenção", "Digite um nome válido!")
            return

        # Confirmação antes de salvar
        acao = "atualizar" if self.setor_em_edicao["id"] else "criar"
        if not messagebox.askyesno("Confirmação", f"Deseja {acao} o setor '{nome}'?"):
            return  # se cancelar, nada acontece

        if self.setor_em_edicao["id"]:
            setor_dao.atualizar_setor(self.setor_em_edicao["id"], nome=nome, responsavel=responsavel)
            messagebox.showinfo("Sucesso", "Setor atualizado!")
        else:
            setor_dao.inserir_setor(nome, responsavel)
            messagebox.showinfo("Sucesso", "Setor criado!")

        # Limpa formulário e atualiza tabela
        self.setor_em_edicao["id"] = None
        self.carregar_dados()


    def cancelar_edicao(self):
        self.entries["Nome do setor"].delete(0, "end")
        if isinstance(self.entries["Responsável"], tb.Combobox):
            self._atualizar_responsaveis()  # reseta combobox com valores atuais
        self.setor_em_edicao["id"] = None
        self.btn_cancelar.pack_forget()

    # ----------------- Editar setor -----------------
    def editar_setor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um setor para editar.")
            return

        item = self.tree.item(sel[0])
        setor_id = item["values"][0]
        setor = next((s for s in AbaSetor.setores if s.id == setor_id), None)
        if setor:
            self.setor_em_edicao["id"] = setor.id
            self.entries["Nome do setor"].delete(0, "end")
            self.entries["Nome do setor"].insert(0, setor.nome)

            # Atualiza combobox de responsáveis
            self._atualizar_responsaveis()
            combo = self.entries["Responsável"]
            if getattr(setor, 'responsavel', None) in combo['values']:
                combo.set(setor.responsavel)
            else:
                combo.set("Nenhum")

            self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)

    # ----------------- Remover setor -----------------
    def remover_setor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um setor para remover.")
            return

        item = self.tree.item(sel[0])
        setor_id = item["values"][0]
        nome = item["values"][1]

        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover o setor '{nome}'?"):
            setor_dao.desativar_setor(setor_id)
            self.carregar_dados()

