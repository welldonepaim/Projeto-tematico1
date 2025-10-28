from datetime import date
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT
from tkinter import messagebox
from tkinter import ttk
from src.dao import planejamento_dao, manutencao_dao


class AbaPlanejamento:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Planejamento")

        # Ações rápidas
        frame_actions = tb.Frame(self.frame)
        frame_actions.pack(fill="x", pady=5)
        tb.Button(frame_actions, text="Gerar manutenções agendadas", bootstyle="info", command=self._gerar_agendadas).pack(side=LEFT, padx=5)
        tb.Button(frame_actions, text="Atualizar lista", bootstyle="secondary", command=self.carregar_planejamentos).pack(side=LEFT, padx=5)

        # Tabela de planejamentos
        colunas = ("ID", "Tipo", "Equipamento", "Frequencia", "Dias", "Data Inicial", "Proxima", "Criticidade", "Estagio")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=12)
        for c in colunas:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=5)

        self.carregar_planejamentos()

    def carregar_planejamentos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        planejamentos = planejamento_dao.listar_planejamentos()
        for p in planejamentos:
            equipamento = p.equipamento.nome if p.equipamento else "N/A"
            data_inicial = p.data_inicial.strftime("%d/%m/%Y") if p.data_inicial else ""
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
