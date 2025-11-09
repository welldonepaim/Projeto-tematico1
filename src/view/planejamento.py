from datetime import date
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT
from tkinter import messagebox
from tkinter import ttk
from src.dao import planejamento_dao, manutencao_dao, usuario_dao, equipamento_dao
from src.model.manutencao import Manutencao
from src.model.planejamento import Planejamento
from datetime import datetime

def _format_date(val):
    """Retorna uma string DD/MM/YYYY a partir de datetime.date ou de string "YYYY-MM-DD"/com T.
    Se não for possível converter, retorna a representação em string original ou string vazia.
    """
    if not val:
        return ""
    # já é date/datetime
    if hasattr(val, 'strftime'):
        try:
            return val.strftime("%d/%m/%Y")
        except Exception:
            return str(val)
    s = str(val)
    if not s:
        return ""
    if 'T' in s:
        s = s.split('T')[0]
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return s


class AbaPlanejamento:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Planejamento")
        # Ações rápidas
        frame_actions = tb.Frame(self.frame)
        frame_actions.pack(fill="x", pady=5)
        tb.Button(frame_actions, text="Gerar agora (selecionado)", bootstyle="primary", command=self.gerar_agora).pack(side=LEFT, padx=5)
        tb.Button(frame_actions, text="Excluir", bootstyle="danger", command=self.excluir).pack(side=LEFT, padx=5)
        

        # Tabela de planejamentos
        colunas = ("ID", "Tipo", "Equipamento", "Frequencia", "Dias", "Data Inicial", "Proxima", "Criticidade", "Estagio")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=12)
        for c in colunas:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=5)
        
                
        

    def carregar_planejamentos(self):
    
        for item in self.tree.get_children():
            self.tree.delete(item)

        planejamentos = planejamento_dao.listar_planejamentos()
        for p in planejamentos:
            equipamento = p.equipamento.nome if p.equipamento else "N/A"
            data_inicial = _format_date(p.data_inicial)
            proxima = ""
            try:
                pd = p.proxima_data()
                if pd:
                    proxima = pd.strftime("%d/%m/%Y")
            except Exception:
                proxima = ""

            dias = str(p.dias_previstos) if p.dias_previstos else (p.frequencia or "")
            self.tree.insert("", "end", values=(p.id, p.tipo, equipamento, p.frequencia, dias, data_inicial, proxima, p.criticidade or "", p.estagio or ""))

    def _gerar_agendadas(self):
        # Botão provisório: não deve gerar ordens de serviço.
        # Apenas atualiza a lista de planejamentos e mostra a quantidade existente.
        try:
            planejamentos = planejamento_dao.listar_planejamentos()
            count = len(planejamentos)
            self.carregar_planejamentos()
            message = f"Existem {count} planejamento(s) cadastrados. Nenhuma ordem foi gerada (modo de teste)."
            messagebox.showinfo("Planejamentos", message)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao listar planejamentos: {e}")

    def _get_selected_planejamento(self) -> Planejamento:
        sel = self.tree.selection()
        if not sel:
            raise ValueError("Selecione um planejamento da lista.")
        item = self.tree.item(sel[0])
        pid = item['values'][0]
        p = planejamento_dao.buscar_planejamento_por_id(pid)
        if not p:
            raise ValueError("Planejamento não encontrado.")
        return p

    def gerar_agora(self):
        try:
            p = self._get_selected_planejamento()
        except Exception as e:
            messagebox.showwarning("Atenção", str(e))
            return

        # criar manutenção vinculada ao planejamento imediatamente
        try:
            hoje = date.today()
            manut = Manutencao(
                id=None,
                tipo=p.tipo,
                equipamento=p.equipamento,
                responsavel=p.responsavel,
                data_prevista=hoje,
                documento=None,
                acoes_realizadas=None,
                observacoes=(p.descricao or "") + f" (Gerada manualmente a partir do planejamento)",
                prioridade=p.criticidade,
                status='Programada'
            )
            manut.planejamento = p
            mid = manutencao_dao.inserir_manutencao(manut)

            # avançar last_gerada e persistir
            try:
                p.avançar_last_gerada()
                planejamento_dao.atualizar_planejamento(p)
            except Exception:
                pass

            messagebox.showinfo("Gerado", f"Manutenção gerada com ID {mid} a partir do planejamento {p.id}.")
          
            

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar manutenção: {e}")

    def editar(self):
        try:
            p = self._get_selected_planejamento()
        except Exception as e:
            messagebox.showwarning("Atenção", str(e))
            return
       
        self._abrir_editor(p)

    def excluir(self):
        try:
            p = self._get_selected_planejamento()
        except Exception as e:
            messagebox.showwarning("Atenção", str(e))
            return

        if not messagebox.askyesno("Confirmar", f"Deseja excluir o planejamento {p.id}? Esta ação é irreversível."):
            return
        try:
            planejamento_dao.excluir_planejamento(p.id)
            messagebox.showinfo("Removido", "Planejamento excluído com sucesso.")
            self.carregar_planejamentos()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir planejamento: {e}")

    
        def _salvar():
            try:
                planejamento.descricao = ent_desc.get().strip()
                planejamento.frequencia = combo_freq.get().strip() or None
                dias_txt = ent_dias.get().strip()
                planejamento.dias_previstos = int(dias_txt) if dias_txt else None
                data_txt = ent_data.get().strip()
                if data_txt:
                    planejamento.data_inicial = datetime.strptime(data_txt, "%d/%m/%Y").date()
                planejamento.criticidade = combo_crit.get().strip() or None
                planejamento.estagio = ent_estagio.get().strip() or None

                planejamento_dao.atualizar_planejamento(planejamento)
                self.gerar_os_de_planejamentos_atrasados()
                self.carregar_os_mes()
                self.carregar_planejamentos()

                messagebox.showinfo("Salvo", "Planejamento atualizado com sucesso.")
                win.destroy()
                self.carregar_planejamentos()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar planejamento: {e}")

        