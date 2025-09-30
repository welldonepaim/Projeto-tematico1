import ttkbootstrap as tb

class AbaEquipamento:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Equipamentos")

        tb.Label(
            self.frame,
            text="⚙️ Cadastro de Equipamentos (em construção)",
            font=("Arial", 14)
        ).pack(pady=50)
