import ttkbootstrap as tb
from ttkbootstrap.constants import *
from src.view.manutencao import AbaManutencao  # ajuste o caminho se necessário

# Janela principal temporária só pra teste
def main():
    app = tb.Window(themename="flatly")  # ou "darkly" se quiser modo escuro
    app.title("Teste da Aba de Manutenções")
    app.geometry("1000x700")

    notebook = tb.Notebook(app)
    notebook.pack(fill="both", expand=True)

    # Cria só a aba de manutenção
    AbaManutencao(notebook)

    app.mainloop()

if __name__ == "__main__":
    main()

