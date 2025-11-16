from src.model import session
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, LEFT
from src.model.manutencao import Manutencao
from src.dao import manutencao_dao, usuario_dao, equipamento_dao, planejamento_dao
from src.model.planejamento import Planejamento
from datetime import date, datetime,timedelta


class AbaManutencao:
    def __init__(self, notebook,aba_planejamento=None):
        self.aba_planejamento = aba_planejamento

        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Manutenções")

     
        self.canvas = tb.Canvas(self.frame)
        self.scrollbar = tb.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

      
        self.inner_frame = tb.Frame(self.canvas, padding=10)
     
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
  
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
    
        self.inner_frame.columnconfigure(1, weight=1)

        self.entries = {}
        self.manutencao_em_edicao = {"id": None}

        self._montar_formulario()
        self._montar_botoes()
        self._montar_tabela()
        self.limpar_formulario()
        self._atualizar_equipamentos()
        self._atualizar_usuarios()
        self.carregar_dados()
        self.bloquear_eventos = False

                
##  Formulário
    def _montar_formulario(self):
        labels = [
            "Tipo", "Equipamento", "Responsável",
            "Data Prevista", "Documento", "Ações Realizadas",
            "Observações", "Status", "Prioridade","Periodicidade"
        ]

        for i, label in enumerate(labels):
            tb.Label(self.inner_frame, text=label + ":", anchor="w").grid(row=i, column=0, padx=5, pady=5, sticky="w")

            if label == "Tipo":
                combo = tb.Combobox(self.inner_frame, values=["Preventiva", "Corretiva", "Preditiva"], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                combo.bind("<<ComboboxSelected>>", self.on_tipo_change)
                self.entries[label] = combo

            elif label == "Prioridade":
                combo = tb.Combobox(self.inner_frame, values=["Urgente", "Alta", "Média", "Baixa", "Sem Prioridade"], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo

            elif label == "Equipamento":
                equipamentos = equipamento_dao.listar_equipamentos()
                combo = tb.Combobox(self.inner_frame, values=[f"{e.id} - {e.nome}" for e in equipamentos], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo

            elif label == "Responsável":
                usuarios = usuario_dao.listar_usuarios()
                combo = tb.Combobox(self.inner_frame, values=[f"{u.id} - {u.nome}" for u in usuarios], state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo

            elif label == "Data Prevista":
                entry = tb.DateEntry(self.inner_frame, dateformat="%d/%m/%Y", bootstyle=INFO)
                entry.set_date(datetime.today().date())  # sempre inicia com hoje
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry


            elif label in ("Documento", "Ações Realizadas", "Observações"):
                entry = tb.Entry(self.inner_frame)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = entry

            elif label == "Status":
                combo = tb.Combobox(self.inner_frame, values=[
                     "Programada","Pendente","Em Análise", "Em Manutenção",
                    "Concluída"
                ], state="readonly")
                combo.set("")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo
            elif label == "Periodicidade":
                combo = tb.Combobox(self.inner_frame, values=[
                     "Diario","Semanal","Mensal","Trimestral","Semestral","Anual"
                ],state="readonly")
                combo.set("")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label] = combo
       
            # Botões
    def _montar_botoes(self):
            
        frame_botoes_form = tb.Frame(self.inner_frame)
        frame_botoes_form.grid(row=10, column=0, columnspan=2, pady=15, sticky="ew")

        self.btn_salvar = tb.Button(frame_botoes_form, text="Salvar Manutenção", bootstyle=SUCCESS, command=self.salvar)
        self.btn_salvar.pack(side=LEFT, expand=True, fill="x", padx=5)

        self.btn_cancelar = tb.Button(frame_botoes_form, text="Cancelar", bootstyle=SECONDARY, command=self.cancelar_edicao)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)
        self.btn_cancelar.pack_forget()
            
############### Tabela


    def _montar_tabela(self):
        frame_tabela = tb.Frame(self.inner_frame)
        frame_tabela.grid(row=11, column=0, columnspan=2, pady=5, sticky="nsew")

        # Frame de pesquisa
        frame_pesquisa = tb.Frame(frame_tabela)
        frame_pesquisa.pack(fill="x", pady=5)
        tb.Label(frame_pesquisa, text="Pesquisar:").pack(side=LEFT, padx=5)
        self.entry_pesquisa = tb.Entry(frame_pesquisa)
        self.entry_pesquisa.pack(side=LEFT, fill="x", expand=True, padx=5)
        tb.Button(frame_pesquisa, text="Buscar", bootstyle=INFO, command=self.pesquisar_manutencao).pack(side=LEFT, padx=5)
        tb.Button(frame_pesquisa, text="Limpar", bootstyle=SECONDARY, command=self.carregar_dados).pack(side=LEFT, padx=5)
        

        # Treeview
        colunas = ("ID", "Tipo", "Equipamento", "Responsável", "Data Prevista", "Prioridade", "Status")
        self.tree = tb.Treeview(frame_tabela, columns=colunas, show="headings", bootstyle=INFO)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure('par', background='#f2f2f2')
        self.tree.tag_configure('impar', background='white')

        # Botões Editar / Excluir
        frame_botoes_tree = tb.Frame(frame_tabela)
        frame_botoes_tree.pack(pady=5)
        tb.Button(frame_botoes_tree, text="Editar", bootstyle=WARNING, command=self.editar).pack(side=LEFT, padx=5)
        tb.Button(frame_botoes_tree, text="Excluir", bootstyle=DANGER, command=self.excluir).pack(side=LEFT, padx=5)

    def carregar_dados(self):
       
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lista_os= manutencao_dao.listar_manutencoes()
        
        hoje = datetime.today().date()
        exibiveis = []
        
        for m in self.lista_os:
            try:
                is_future_planned = (
                    (m.tipo == 'Preventiva' or (m.tipo and m.tipo.lower() == 'preventiva')) and
                    (m.status == 'Programada' or (m.status and m.status.lower() == 'programada')) and
                    m.data_prevista is not None and
                    m.data_prevista > hoje
                )
            except Exception:
                is_future_planned = False
            
            # Filtra manutenções concluídas e futuras preventivas programadas
            if not is_future_planned and (m.status != 'Concluída' and (m.status or "").lower() != 'concluída'):
                exibiveis.append(m)

        for i, m in enumerate(exibiveis):
            tag = 'par' if i % 2 == 0 else 'impar'
            eq = m.equipamento.nome if m.equipamento else "N/A"
            resp = m.responsavel.nome if m.responsavel else "N/A"
            data = m.data_prevista.strftime("%d/%m/%Y") if m.data_prevista else ""
            self.tree.insert("", "end", values=(m.id, m.tipo, eq, resp, data, m.prioridade, m.status), tags=(tag,))


    def pesquisar_manutencao(self):
        termo = self.entry_pesquisa.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        manutencoes = manutencao_dao.listar_manutencoes()
        hoje = datetime.today().date()
        filtrados = []
        for m in manutencoes:
            try:
                is_future_planned = (
                    (m.tipo == 'Preventiva' or (m.tipo and m.tipo.lower() == 'preventiva'))
                    and (m.status == 'Programada' or (m.status and m.status.lower() == 'programada'))
                    and m.data_prevista is not None
                    and m.data_prevista > hoje
                )
            except Exception:
                is_future_planned = False
            if is_future_planned:
                continue
            if termo in (m.tipo or "").lower() or termo in (m.equipamento.nome if m.equipamento else "").lower() or termo in (m.responsavel.nome if m.responsavel else "").lower():
                filtrados.append(m)
        for i, m in enumerate(filtrados):
            tag = 'par' if i % 2 == 0 else 'impar'
            eq = m.equipamento.nome if m.equipamento else "N/A"
            resp = m.responsavel.nome if m.responsavel else "N/A"
            data = m.data_prevista.strftime("%d/%m/%Y") if m.data_prevista else ""
            self.tree.insert("", "end", values=(m.id, m.tipo, eq, resp, data, m.prioridade, m.status), tags=(tag,))
            
    
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

        self.entries["Tipo"].set(manutencao.tipo)
        self.entries["Tipo"].configure(state="disabled")  # tipo bloqueado
        self.entries["Equipamento"].set(f"{manutencao.equipamento.id} - {manutencao.equipamento.nome}")
        self.entries["Equipamento"].configure(state="disabled")
        self.entries["Responsável"].set(f"{manutencao.responsavel.id} - {manutencao.responsavel.nome}")

        # Data Prevista
        if manutencao.status == "Concluída":
            self.entries["Data Prevista"].entry.config(state="readonly")
        else:
            self.entries["Data Prevista"].entry.config(state="normal")
        self.entries["Data Prevista"].set_date(manutencao.data_prevista)

        self.entries["Documento"].delete(0, "end")
        self.entries["Documento"].insert(0, manutencao.documento or "")
        self.entries["Ações Realizadas"].delete(0, "end")
        self.entries["Ações Realizadas"].insert(0, manutencao.acoes_realizadas or "")
        self.entries["Observações"].delete(0, "end")
        self.entries["Observações"].insert(0, manutencao.observacoes or "")
        self.entries["Prioridade"].set(manutencao.prioridade)
        
        # Status sempre editável em OS existente
        self.entries["Status"].set(manutencao.status)
        self.entries["Status"].configure(state="readonly")

        self.manutencao_em_edicao["id"] = manutencao.id
        self.btn_salvar.config(text="Atualizar Manutenção", bootstyle=WARNING)
        self.btn_cancelar.pack(side=LEFT, expand=True, fill="x", padx=5)

    def salvar(self):
               
        
        try:
            tipo = self.entries["Tipo"].get()
            equipamento_str = self.entries["Equipamento"].get()
            responsavel_str = self.entries["Responsável"].get()
            data_prevista = datetime.strptime(self.entries["Data Prevista"].entry.get(), "%d/%m/%Y").date()
            documento = self.entries["Documento"].get()
            acoes = self.entries["Ações Realizadas"].get()
            obs = self.entries["Observações"].get()


            prioridade = self.entries["Prioridade"].get()
            status = self.entries["Status"].get()
            periodicidade = self.entries["Periodicidade"].get() if "Periodicidade" in self.entries else None

            # Validação obrigatória
            if not (tipo and equipamento_str and responsavel_str and data_prevista and status):
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
                return

            # Preventiva Programada exige periodicidade
            if tipo == "Preventiva" and status == "Programada" and not periodicidade:
                messagebox.showwarning("Atenção", "Para manutenções Preventivas e Programadas, o campo Periodicidade é obrigatório.")
                return
            
            equipamento_id = int(equipamento_str.split(" - ")[0])
            responsavel_id = int(responsavel_str.split(" - ")[0])

            equipamento = equipamento_dao.buscar_equipamento_por_id(equipamento_id)
            responsavel = usuario_dao.buscar_usuario_por_id(responsavel_id)

            # Se for Preventiva Programada, cria planejamento
            if tipo == "Preventiva" and status == "Programada":
                freq_map = {
                    "Diario": 1,
                    "Semanal": 7,
                    "Mensal": 30,
                    "Trimestral": 90,
                    "Semestral": 180,
                    "Anual": 365,
                }
                dias = freq_map.get(periodicidade)
                if dias is None:
                    messagebox.showwarning("Atenção", "Periodicidade inválida.")
                    return

                planejamento = Planejamento(
                    id=None,
                    tipo=tipo,
                    descricao=obs or documento or "Manutenção preventiva",
                    frequencia=periodicidade,
                    dias_previstos=dias,
                    data_inicial=data_prevista,
                    criticidade=prioridade,
                    responsavel=responsavel,
                    equipamento=equipamento,
                    estagio="Ativo",
                    last_gerada=None,
                )

                try:
                    planejamento_dao.inserir_planejamento(planejamento)
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível criar planejamento: {e}")
                    return

                messagebox.showinfo("Sucesso", "Planejamento cadastrado com sucesso! A manutenção será gerada quando chegar a data prevista.")
               
                if self.aba_planejamento:
                    self.aba_planejamento.carregar_planejamentos()
                    
            else:
                # Manutenção simples (Corretiva, Preditiva ou Preventiva não programada)
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
                    # Atualiza existente
                    manutencao_dao.atualizar_manutencao(manutencao)
                    messagebox.showinfo("Sucesso", "Manutenção atualizada com sucesso!")
                    status_antigo=None 
                    if self.manutencao_em_edicao["id"]:
                        manut_antigo = manutencao_dao.buscar_manutencao_por_id(self.manutencao_em_edicao["id"])
                        status_antigo = manut_antigo.status
                    if status == "Concluída":
                        
                        self.concluir_manutencao(manutencao.id)

                else:
                    # Nova manutenção
                    manutencao_dao.inserir_manutencao(manutencao)
                    messagebox.showinfo("Sucesso", "Manutenção cadastrada com sucesso!")

            # Atualizar combos e Treeview
            self._atualizar_equipamentos()
            self._atualizar_usuarios()
            self.carregar_dados()
            if self.manutencao_em_edicao["id"]:
                self.cancelar_edicao()  # sai do menu
            else:
                self.limpar_formulario()  # apenas limpa para nova entrada

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar: {e}")


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
                if self.aba_planejamento:
                 self.aba_planejamento.carregar_planejamentos()
                messagebox.showinfo("Sucesso", "Manutenção excluída com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível excluir: {e}")
 
    def limpar_formulario(self):
        """
        Limpa todos os campos do formulário e impede que o on_tipo_change rode sozinho.
        """
        self.bloquear_eventos = True   # <--- IMPRESCINDÍVEL

        for label, entry in self.entries.items():

            # TEXTOS
            if isinstance(entry, tb.Entry):
                entry.delete(0, "end")

            # COMBOBOXES
            elif isinstance(entry, tb.Combobox):
                entry.set("")
                entry.configure(state="readonly")

            # DATEENTRY
            elif isinstance(entry, tb.DateEntry):
                entry.set_date(datetime.today().date())
                entry.entry.config(state="normal")  # sempre liberado ao limpar

        # Reset do modo edição
        self.manutencao_em_edicao["id"] = None
        self.entries["Tipo"].configure(state="readonly")
        self.btn_salvar.config(text="Salvar Manutenção", bootstyle=SUCCESS)
        self.btn_cancelar.pack_forget()

        self.bloquear_eventos = False 
    def _atualizar_equipamentos(self):
        self.equipamentos = equipamento_dao.listar_equipamentos()
        combo_eq = self.entries.get("Equipamento")
        if combo_eq:
            combo_eq['values'] = [f"{e.id} - {e.nome}" for e in self.equipamentos]
            combo_eq.set("")

    def _atualizar_usuarios(self):
        self.usuarios = usuario_dao.listar_usuarios()
        combo_resp = self.entries.get("Responsável")
        if combo_resp:
            combo_resp['values'] = [f"{u.id} - {u.nome}" for u in self.usuarios]
            if self.usuarios:
                 combo_resp['values'] = [f"{u.id} - {u.nome}" for u in self.usuarios]
                 combo_resp.set("")  
    
    def cancelar_edicao(self):
        self.limpar_formulario()
        self.btn_salvar.config(text="Salvar Manutenção", bootstyle=SUCCESS)
        self.btn_cancelar.pack_forget()
        
    def concluir_manutencao(self, manutencao_id):
            manutencao = manutencao_dao.buscar_manutencao_por_id(manutencao_id)
            if not manutencao:
                messagebox.showerror("Erro", "Manutenção não encontrada.")
                return

            # Atualiza a manutenção como concluída
            manutencao.status = "Concluída"
            manutencao_dao.atualizar_manutencao(manutencao)

            # Se essa manutenção faz parte de um planejamento
            if manutencao.planejamento:
                planejamento = planejamento_dao.buscar_planejamento_por_id(
                    manutencao.planejamento.id
                )

                if planejamento:
                    hoje = date.today()

                    # Atualiza data da última execução
                    planejamento.last_gerada = hoje

                    # Recalcula próxima geração
                    if planejamento.dias_previstos:
                        planejamento.data_prevista = hoje + timedelta(days=planejamento.dias_previstos)

                    planejamento_dao.atualizar_planejamento(planejamento)

            messagebox.showinfo("Sucesso", "Manutenção concluída e próxima preventiva programada!")
            self.limpar_formulario()

            # Atualizar telas
            self.carregar_dados()
            if self.aba_planejamento:
                self.aba_planejamento.carregar_planejamentos()
    def gerar_os_do_dia(self):
       ## ESSA FUNÇÃO DEVE SER IMPLEMENTADA POR ULTIMO
       ##
       ###
       #####
        planejamentos = planejamento_dao.listar_planejamentos()
        hoje = date.today()

        for p in planejamentos:
            # Garantir que last_gerada e data_inicial sejam date
            last_gerada = p.last_gerada
            if isinstance(last_gerada, str):
                last_gerada = datetime.strptime(last_gerada, "%Y-%m-%d").date()
            
            data_inicial = p.data_inicial
            if isinstance(data_inicial, str):
                data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d").date()

            proxima_data = last_gerada + timedelta(days=p.dias_previstos) if last_gerada else data_inicial

            # Só gera OS se a data for hoje ou anterior
            if proxima_data > hoje:
                continue

            # Evita criar OS duplicadas
            if self.existe_os_aberta_no_banco(p.id, proxima_data):
                continue

            # Cria a OS preventiva
            manutencao = Manutencao(
                tipo="Preventiva",
                equipamento=p.equipamento,
                responsavel=p.responsavel,
                data_prevista=proxima_data,
                status="Pendente",
                observacoes=f"Preventiva automática (Periodicidade: {p.dias_previstos} dias)",
                planejamento=p
            )
            manutencao_dao.inserir_manutencao(manutencao)

            # Atualiza a última geração
            p.last_gerada = proxima_data
            planejamento_dao.atualizar_planejamento(p)

    def existe_os_aberta_no_banco(self, id_planejamento: int, data_prevista: date) -> bool:
            manuts = manutencao_dao.listar_manutencoes_por_planejamento(id_planejamento)
            for m in manuts:
                if m.status != "Concluída" and m.data_prevista == data_prevista:
                    return True
            return False
            
    def on_tipo_change(self, event=None):
        if self.bloquear_eventos:
            return
        tipo = self.entries["Tipo"].get()
        status_combo = self.entries["Status"]
        status_combo.configure(state="disabled")
        data_entry = self.entries["Data Prevista"]
        periodicidade_entry = self.entries["Periodicidade"]
        periodicidade_entry.config(state="disabled") # desabilita por padrão

        if data_entry is None:
            return  
        #Para que quando eu definir algum tipo de manutenção o campo de data seja preenchido automaticamente com a data atual
        try:
            data_entry.set_date(datetime.today().date())
        except Exception:
            pass
        
        #Para saber quando estou criando uma nova OS
        if self.manutencao_em_edicao["id"] is None:

                # Preventiva  Programada
            if tipo == "Preventiva":
                status_combo.set("Programada")
                status_combo.configure(state="disabled")
                data_entry.entry.config(state="normal")
                periodicidade_entry.config(state="readonly")

            # Qualquer outro tipo  Pendente
            else:
                status_combo.set("Pendente")
                status_combo.configure(state="disabled")  #    
                data_entry.entry.config(state="readonly")
                

        else:
            # Para pode editar qualquer manutenção existente
            status_combo.configure(state="readonly")

            if tipo == "Preventiva":
                data_entry.entry.config(state="normal")
            else:
                data_entry.entry.config(state="readonly")