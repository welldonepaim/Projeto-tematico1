import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import Tk, Frame, Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AbaPainel:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Painel")

        # Dados fictícios
        self.total_setores = 12
        self.usuarios_ativos = 8
        self.usuarios_inativos = 3
        self.setores_sem_responsavel = 2

        self.ordens_abertas = 7
        self.ordens_encerradas = 15

        # Monta a interface
        self._montar_cards()
        self._montar_graficos()
        self._montar_alertas()

    # ----------------- Cards de resumo -----------------
    def _montar_cards(self):
        frame_cards = tb.Frame(self.frame)
        frame_cards.pack(fill="x", pady=10)

        cards = [
            ("Total de Setores", self.total_setores, "#5dade2"),
            ("Usuários Ativos", self.usuarios_ativos, "#58d68d"),
            ("Usuários Inativos", self.usuarios_inativos, "#ec7063"),
            ("Setores sem Responsável", self.setores_sem_responsavel, "#f4d03f")
        ]

        for title, value, color in cards:
            card = tb.Frame(frame_cards, bootstyle="light", padding=10, relief="raised")
            card.pack(side="left", expand=True, fill="both", padx=5)
            tb.Label(card, text=title, font=("Arial", 10), foreground=color).pack(pady=(0,5))
            tb.Label(card, text=str(value), font=("Arial", 20, "bold")).pack()

    # ----------------- Gráficos -----------------
    def _montar_graficos(self):
        frame_graficos = tb.Frame(self.frame)
        frame_graficos.pack(fill="both", expand=True, pady=10)

        # Gráfico 1: Usuários ativos vs inativos (pizza)
        fig1, ax1 = plt.subplots(figsize=(3,3))
        ax1.pie(
            [self.usuarios_ativos, self.usuarios_inativos],
            labels=["Ativos", "Inativos"],
            autopct="%1.1f%%",
            colors=["#58d68d", "#ec7063"]
        )
        ax1.set_title("Usuários")
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_graficos)
        canvas1.get_tk_widget().pack(side="left", expand=True)

        # Gráfico 2: Ordens abertas vs encerradas (barra)
        fig2, ax2 = plt.subplots(figsize=(3,3))
        ax2.bar(["Abertas", "Encerradas"], [self.ordens_abertas, self.ordens_encerradas], color=["#f39c12", "#5dade2"])
        ax2.set_title("Ordens de Serviço")
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_graficos)
        canvas2.get_tk_widget().pack(side="left", expand=True)

    # ----------------- Alertas -----------------
    def _montar_alertas(self):
        frame_alertas = tb.Frame(self.frame)
        frame_alertas.pack(fill="x", pady=10)

        mensagens = [
            f"⚠️ Existem {self.setores_sem_responsavel} setores sem responsável!",
            f"ℹ️ Total de ordens abertas: {self.ordens_abertas}"
        ]

        for msg in mensagens:
            tb.Label(frame_alertas, text=msg, font=("Arial", 11), bootstyle=INFO).pack(anchor="w", pady=2)

# ----------------- Teste da interface -----------------
if __name__ == "__main__":
    root = tb.Window(title="Painel do Sistema", themename="superhero", size=(900,600))
    notebook = tb.Notebook(root)
    notebook.pack(fill="both", expand=True)

    AbaPainel(notebook)

    root.mainloop()

