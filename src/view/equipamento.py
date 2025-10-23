from src.model import session
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from src.model.equipamento import Equipamento
from src.dao import equipamento_dao, setor_dao
from datetime import datetime


class AbaEquipamento:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Equipamentos")

        self.entries = {}
        self.equipamento_em_edicao = {"id": None}
        self.setores = []

        self._montar_formulario()
        self._montar_botoes()
        self._montar_tabela()

        # Atualiza setores e carrega equipamentos
        self._atualizar_setores()
        self.carregar_dados()

    def _verificar_permissao(self):
        usuario_logado = session.get_usuario()
        if not usuario_logado:
            messagebox.showwarning("Atenção", "Você precisa estar logado para realizar esta ação.")
            return False
        if usuario_logado.perfil not in ("Administrador", "Gestor"):
            messagebox.showwarning("Atenção", "Acesso restrito: apenas Administrador ou Gestor pode realizar esta ação.")
            return False
        return True

    def _montar_formulario(self):
            labels = ["Nome", "Tipo", "Número de Série", "Fabricante", "Setor", "Status", "Data de Aquisição"]

            for i, label in enumerate(labels):
                # Label alinhada à direita, próxima do campo
                tb.Label(self.frame, text=label + ":", anchor="e").grid(
                    row=i, column=0, padx=5, pady=2, sticky="e"
                )

                if label == "Status":
                    combo = tb.Combobox(self.frame, values=["Disponível", "Indisponível"], state="readonly", width=25)
                    combo.set("Disponível")
                    combo.grid(row=i, column=1, padx=5, pady=2, sticky="we")
                    self.entries[label] = combo

                elif label == "Setor":
                    combo_setor = tb.Combobox(self.frame, state="readonly", width=25)
                    combo_setor.grid(row=i, column=1, padx=5, pady=2, sticky="we")
                    self.entries[label] = combo_setor

                elif "Data" in label:
                    date_entry = tb.DateEntry(self.frame, dateformat="%d/%m/%Y", width=22)
                    date_entry.set_date(datetime.today().date())
                    date_entry.grid(row=i, column=1, padx=5, pady=2, sticky="we")
                    self.entries[label] = date_entry

                else:
                    entry = tb.Entry(self.frame, width=25)
                    entry.grid(row=i, column=1, padx=5, pady=2, sticky="we")
                    self.entries[label] = entry

            # Ajusta largura das colunas
            self.frame.columnconfigure(0, weight=0)  # coluna de labels
            self.frame.columnconfigure(1, weight=1)  # coluna de campos

    def _montar_botoes(self):
        frame_botoes_form = tb.Frame(self.frame)
        frame_botoes_form.grid(row=7, column=0, columnspan=2, pady=15, sticky="ew")

        self.btn_salvar = tb.Button(frame_botoes_form, text="Salvar Equipamento", bootstyle=SUCCESS, command=self.salvar)
        self.btn_salvar.pack(side=LEFT, expand=True, fill="x", padx=5)

        self.btn_cancelar = tb.Button(frame_botoes_form, text="Cancelar", bootstyle=SECONDARY, command=self.cancelar_edicao)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)
        self.btn_cancelar.pack_forget()
   
    def _montar_tabela(self):
        frame_pesquisa = tb.Frame(self.frame)
        frame_pesquisa.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

        tb.Label(frame_pesquisa, text="Pesquisar:").pack(side=LEFT, padx=5)
        self.entry_pesquisa = tb.Entry(frame_pesquisa)
        self.entry_pesquisa.pack(side=LEFT, fill="x", expand=True, padx=5)

        tb.Button(frame_pesquisa, text="Buscar", bootstyle=INFO, command=self.pesquisar_equipamento).pack(side=LEFT, padx=5)
        tb.Button(frame_pesquisa, text="Limpar", bootstyle=SECONDARY, command=self.carregar_dados).pack(side=LEFT, padx=5)

        # Treeview
        colunas = ("ID", "Nome", "Tipo", "Número de Série", "Setor", "Status", "Fabricante", "Data de Aquisição")
        self.tree = tb.Treeview(self.frame, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Cores alternadas
        self.tree.tag_configure('par', background='#f2f2f2')
        self.tree.tag_configure('impar', background='white')

        # Permitir que o frame cresça
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(9, weight=1)

        # Frame de botões abaixo da tabela
        frame_botoes = tb.Frame(self.frame)
        frame_botoes.grid(row=10, column=0, columnspan=2, pady=10)
        tb.Button(frame_botoes, text="Editar", bootstyle=WARNING, command=self.editar_equipamento).pack(side=LEFT, padx=5)
        tb.Button(frame_botoes, text="Excluir", bootstyle=DANGER, command=self.excluir_equipamento).pack(side=LEFT, padx=5)

    def pesquisar_equipamento(self):
        termo = self.entry_pesquisa.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        equipamentos = equipamento_dao.listar_equipamentos()
        filtrados = [
            e for e in equipamentos
            if termo in (e.nome or "").lower()
            or termo in (e.tipo or "").lower()
            or termo in (e.numero_serie or "").lower()
            or termo in (e.setor or "").lower()
            or termo in (e.fabricante or "").lower()
        ]

        for eq in filtrados:
            self.tree.insert("", "end", values=(
                eq.id, eq.nome, eq.tipo, eq.numero_serie, eq.setor, eq.status, eq.fabricante, eq.data_aquisicao
            ))

    def carregar_dados(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        equipamentos = equipamento_dao.listar_equipamentos()
        for i, eq in enumerate(equipamentos):
            tag = 'par' if i % 2 == 0 else 'impar'

            # Se eq.setor for um objeto, pega o nome; se for um ID, busca o nome correspondente
            if hasattr(eq.setor, "nome"):
                nome_setor = eq.setor.nome
            else:
                setor_obj = next((s for s in self.setores if s.id == eq.setor), None)
                nome_setor = setor_obj.nome if setor_obj else "Desconhecido"

            self.tree.insert("", "end", values=(
                eq.id,
                eq.nome,
                eq.tipo,
                eq.numero_serie,
                nome_setor,
                eq.status,
                eq.fabricante,
                eq.data_aquisicao
            ), tags=(tag,))


    def editar_equipamento(self):
        if not self._verificar_permissao():
            return

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um equipamento para editar.")
            return

        item = self.tree.item(selecionado[0])
        valores = item.get("values", [])

        equipamento = equipamento_dao.buscar_equipamento_por_id(valores[0])
        if not equipamento:
            messagebox.showerror("Erro", "Equipamento não encontrado.")
            return

        self.equipamento_em_edicao["id"] = equipamento.id
        self.entries["Nome"].delete(0, "end")
        self.entries["Nome"].insert(0, equipamento.nome or "")
        self.entries["Tipo"].delete(0, "end")
        self.entries["Tipo"].insert(0, equipamento.tipo or "")
        self.entries["Número de Série"].delete(0, "end")
        self.entries["Número de Série"].insert(0, equipamento.numero_serie or "")
        self.entries["Setor"].delete(0, "end")
        self.entries["Setor"].insert(0, equipamento.setor or "")
        self.entries["Status"].set(equipamento.status or "")
        self.entries["Fabricante"].delete(0, "end")
        self.entries["Fabricante"].insert(0, equipamento.fabricante or "")

        if equipamento.data_aquisicao:
            self.entries["Data de Aquisição"].set_date(equipamento.data_aquisicao)
        else:
            self.entries["Data de Aquisição"].set_date(datetime.today().date())

        self.btn_salvar.config(text="Atualizar Equipamento", bootstyle=WARNING)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)

    def excluir_equipamento(self):
        if not self._verificar_permissao():
            return

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um equipamento para excluir.")
            return

        item = self.tree.item(selecionado[0])
        valores = item["values"]
        equipamento_id = valores[0]

        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o equipamento {valores[1]}?"):
            try:
                equipamento_dao.excluir_equipamento(equipamento_id)
                self.carregar_dados()
                messagebox.showinfo("Sucesso", "Equipamento excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir: {e}")

    def salvar(self):
        if not self._verificar_permissao():
            return
        
        data_aquisicao = self.entries["Data de Aquisição"].get_date()
        nome_setor_selecionado = self.entries["Setor"].get()
        setor_obj = next((s for s in self.setores if s.nome == nome_setor_selecionado), None)

        equipamento = Equipamento(
            id=self.equipamento_em_edicao["id"],
            nome=self.entries["Nome"].get(),
            tipo=self.entries["Tipo"].get(),
            numero_serie=self.entries["Número de Série"].get(),
            setor=setor_obj,
            status=self.entries["Status"].get(),
            fabricante=self.entries["Fabricante"].get(),
            data_aquisicao=data_aquisicao
        )

        if not (equipamento.nome and equipamento.tipo and equipamento.status):
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios: Nome, Tipo e Status.")
            return
        
        setor_nome = self.entries["Setor"].get().strip()
        if not setor_nome:
            messagebox.showwarning("Atenção", "Selecione um setor para o equipamento.")
            return


        try:
            if equipamento.id:
                equipamento_dao.atualizar_equipamento(equipamento)
                messagebox.showinfo("Sucesso", "Equipamento atualizado com sucesso!")
                self.btn_salvar.config(text="Salvar Equipamento", bootstyle=SUCCESS)
                self.btn_cancelar.pack_forget()
            else:
                equipamento_dao.inserir_equipamento(equipamento)
                messagebox.showinfo("Sucesso", "Equipamento cadastrado com sucesso!")

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
            elif isinstance(entry, tb.DateEntry):
                entry.set_date(datetime.today().date())

        self.equipamento_em_edicao["id"] = None

    def cancelar_edicao(self):
        self.limpar_formulario()
        self.btn_salvar.config(text="Salvar Equipamento", bootstyle=SUCCESS)
        self.btn_cancelar.pack_forget()

    def _atualizar_setores(self):
        """Atualiza o combobox de setores com todos os setores cadastrados."""
        self.setores = setor_dao.listar_setores()
        nomes_setores = [s.nome for s in self.setores if getattr(s, "status", "Ativo") == "Ativo"]

        combo_setor = self.entries.get("Setor")
        if combo_setor:
            combo_setor["values"] = nomes_setores
            # Define o primeiro setor da lista como padrão, se houver
            if nomes_setores:
                combo_setor.set(nomes_setores[0])


