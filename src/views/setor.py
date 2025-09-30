import ttkbootstrap as tb
# from src import db  # descomentar quando precisar acessar o banco

class AbaSetor:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Setores")
        tb.Label(self.frame, text="📌 Cadastro de Setores (em construção)", font=("Arial", 14)).pack(pady=50)
