from src.model import session
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from src.model.manutencao import Manutencao
from src.dao import manutencao_dao, usuario_dao, equipamento_dao
from datetime import date, datetime
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento


class AbaManutencao:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Manutenções")

        self.entries = {}
        self.manutencao_em_edicao = {"id": None}

        self._montar_formulario()
        self._montar_botoes()
        self._montar_tabela()
        
        self._atualizar_equipamentos()
        self._atualizar_usuarios()
        self.carregar_dados()


    # ----------------- FORMULÁRIO -----------------
    def _montar_formulario(self):
        labels = [
            "Tipo", "Equipamento", "Responsável", 
            "Data Prevista", 
            "Documento", "Ações Realizadas", "Observações", "Status","Prioridade"
        ]

        for i, label in enumerate(labels):
            tb.Label(self.frame, text=label + ":", anchor="w").grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if label == "Tipo":
                combo = tb.Combobox(self.frame, values=["Preventiva", "Corretiva", "Preditiva"], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo
            elif label == "Prioridade":
                combo = tb.Combobox(self.frame, values=["Urgente", "Alta", "Média","Baixa","Sem Prioridade"], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo            
                            
            elif label == "Equipamento":
                equipamentos = equipamento_dao.listar_equipamentos()
                combo = tb.Combobox(self.frame, values=[f"{e.id} - {e.nome}" for e in equipamentos], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo

            elif label == "Responsável":
                usuarios = usuario_dao.listar_usuarios()
                combo = tb.Combobox(self.frame, values=[f"{u.id} - {u.nome}" for u in usuarios], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo

            elif label in ("Data Prevista"):
                entry = tb.DateEntry(self.frame, dateformat="%d/%m/%Y", bootstyle=INFO)
                entry.set_date(datetime.today().date())
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry

            elif label in ("Documento", "Ações Realizadas", "Observações"):
                entry = tb.Entry(self.frame)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry

            elif label == "Status":
                combo = tb.Combobox(self.frame, values=[
                    "Pendente", "Em Análise", "Em Manutenção", 
                    "Concluída", "Revisada", "Disponível", "Descontinuado"
                ])
                combo.set("Pendente")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo

    # ----------------- BOTÕES FORM -----------------
    def _montar_botoes(self):
        frame_botoes_form = tb.Frame(self.frame)
        frame_botoes_form.grid(row=9, column=0, columnspan=2, pady=15, sticky="ew")

        self.btn_salvar = tb.Button(frame_botoes_form, text="Salvar Manutenção", bootstyle=SUCCESS, command=self.salvar)
        self.btn_salvar.pack(side=LEFT, expand=True, fill="x", padx=5)

        self.btn_cancelar = tb.Button(frame_botoes_form, text="Cancelar", bootstyle=SECONDARY, command=self.cancelar_edicao)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)
        self.btn_cancelar.pack_forget()

    # ----------------- TABELA -----------------
    def _montar_tabela(self):
        colunas = ("ID", "Tipo", "Equipamento", "Responsável", "Data Prevista", "Prioridade", "Status")
        self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # alternância de cores
        self.tree.tag_configure('par', background='#f2f2f2')
        self.tree.tag_configure('impar', background='white')

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(10, weight=1)

        frame_botoes = tb.Frame(self.frame)
        frame_botoes.grid(row=11, column=0, columnspan=2, pady=10)

        tb.Button(frame_botoes, text="Editar Manutenção", bootstyle=WARNING, command=self.editar).pack(side=LEFT, padx=5)
        tb.Button(frame_botoes, text="Excluir Manutenção", bootstyle=DANGER, command=self.excluir).pack(side=LEFT, padx=5)

    # ----------------- CARREGAR -----------------
    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        manutencoes = manutencao_dao.listar_manutencoes()
        for i, m in enumerate(manutencoes):
            tag = 'par' if i % 2 == 0 else 'impar'
            self.tree.insert("", "end", values=(
                m.id, m.tipo, m.equipamento.nome, m.responsavel.nome, 
                m.data_prevista,m.prioridade, m.status
            ), tags=(tag,))

    # ----------------- SALVAR -----------------
    def salvar(self):
        try:
            tipo = self.entries["Tipo"].get()
            equipamento_str = self.entries["Equipamento"].get()
            responsavel_str = self.entries["Responsável"].get()

            data_prevista = datetime.strptime(self.entries["Data Prevista"].entry.get(), "%d/%m/%Y").date()
            
            documento = self.entries["Documento"].get()
            acoes = self.entries["Ações Realizadas"].get()
            obs = self.entries["Observações"].get()
            prioridade=self.entries["Prioridade"].get()
            status = self.entries["Status"].get()

            if not (tipo and equipamento_str and responsavel_str and data_prevista and status):
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
                return

            equipamento_id = int(equipamento_str.split(" - ")[0])
            responsavel_id = int(responsavel_str.split(" - ")[0])

            
            equipamento = equipamento_dao.buscar_equipamento_por_id(equipamento_id)
            responsavel = usuario_dao.buscar_usuario_por_id(responsavel_id)

            manutencao = Manutencao(
                id=self.manutencao_em_edicao["id"],
                tipo=tipo,
                equipamento=equipamento,
                responsavel=responsavel,
                data_prevista=data_prevista,
                documento=documento,
                acoes_realizadas=acoes,
                observacoes=obs,
                prioridade=prioridade,
                status=status
            )

            if manutencao.id:
                manutencao_dao.atualizar_manutencao(manutencao)
                messagebox.showinfo("Sucesso", "Manutenção atualizada com sucesso!")
            else:
                manutencao_dao.inserir_manutencao(manutencao)
                messagebox.showinfo("Sucesso", "Manutenção cadastrada com sucesso!")

            self.limpar_formulario()
            self.carregar_dados()

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar: {e}")

    # ----------------- EDITAR -----------------
    def editar(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma manutenção para editar.")
            return

        item = self.tree.item(selecionado[0])
        valores = item["values"]
        manutencao_id = valores[0]

        manutencao = manutencao_dao.buscar_manutencao_por_id(manutencao_id)
        if not manutencao:
            messagebox.showerror("Erro", "Manutenção não encontrada.")
            return

        self.manutencao_em_edicao["id"] = manutencao.id
        self.entries["Tipo"].set(manutencao.tipo)
        self.entries["Equipamento"].set(f"{manutencao.equipamento.id} - {manutencao.equipamento.nome}")
        self.entries["Responsável"].set(f"{manutencao.responsavel.id} - {manutencao.responsavel.nome}")
        self.entries["Data Prevista"].set_date(manutencao.data_prevista)
        self.entries["Documento"].delete(0, "end")
        self.entries["Documento"].insert(0, manutencao.documento or "")
        self.entries["Ações Realizadas"].delete(0, "end")
        self.entries["Ações Realizadas"].insert(0, manutencao.acoes_realizadas or "")
        self.entries["Observações"].delete(0, "end")
        self.entries["Observações"].insert(0, manutencao.observacoes or "")
        self.entries["Prioridade"].set(manutencao.prioridade)

        self.entries["Status"].set(manutencao.status)

        self.btn_salvar.config(text="Atualizar Manutenção", bootstyle=WARNING)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)

    # ----------------- EXCLUIR -----------------
    def excluir(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma manutenção para excluir.")
            return

        item = self.tree.item(selecionado[0])
        valores = item["values"]
        manutencao_id = valores[0]

        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir a manutenção ID {manutencao_id}?"):
            try:
                manutencao_dao.excluir_manutencao(manutencao_id)
                self.carregar_dados()
                messagebox.showinfo("Sucesso", "Manutenção excluída com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir: {e}")

    # ----------------- LIMPAR / CANCELAR -----------------
    def limpar_formulario(self):
        for entry in self.entries.values():
            if isinstance(entry, tb.Entry):
                entry.delete(0, "end")
            elif isinstance(entry, tb.Combobox):
                entry.set("")
            elif isinstance(entry, tb.DateEntry):
                entry.set_date(date.today())
        self.manutencao_em_edicao["id"] = None

    def cancelar_edicao(self):
        self.limpar_formulario()
        self.btn_salvar.config(text="Salvar Manutenção", bootstyle=SUCCESS)
        self.btn_cancelar.pack_forget()

    def _atualizar_equipamentos(self):
        self.equipamentos = equipamento_dao.listar_equipamentos()
        combo_eq = self.entries.get("Equipamento")
        if combo_eq:
            combo_eq['values'] = [f"{e.id} - {e.nome}" for e in self.equipamentos]
            if self.equipamentos:
                combo_eq.set(f"{self.equipamentos[0].id} - {self.equipamentos[0].nome}")

    def _atualizar_usuarios(self):
        self.usuarios = usuario_dao.listar_usuarios()
        combo_resp = self.entries.get("Responsável")
        if combo_resp:
            combo_resp['values'] = [f"{u.id} - {u.nome}" for u in self.usuarios]
            if self.usuarios:
                combo_resp.set(f"{self.usuarios[0].id} - {self.usuarios[0].nome}")
