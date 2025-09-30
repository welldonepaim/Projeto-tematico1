import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from src.views.painel import AbaPainel
from src.views.usuario import AbaUsuario
from src.views.setor import AbaSetor
from src.views.equipamento import AbaEquipamento
from src import db

class App:
    def __init__(self):
        self.usuario_logado = None
        self.app = tb.Window(themename="cosmo")
        self.app.title("ManuSys")
        self.app.geometry("900x600")

        # Define o ícone da aplicação
        self.app.iconbitmap("C:/Users/william/Documents/GitHub/Projeto-tematico1/image/favicon.ico")

        self._criar_cabecalho()
        self._criar_notebook()
        self._adicionar_abas()

        self.app.mainloop()

    def _criar_cabecalho(self):
        self.cabecalho = tb.Frame(self.app)
        self.cabecalho.pack(fill="x", padx=10, pady=5)

        # Nome do app
        tb.Label(self.cabecalho, text="ManuSys", font=("Arial", 18, "bold"), bootstyle=PRIMARY).pack(side=LEFT)

        # Botão de login
        self.usuario_btn = tb.Button(self.cabecalho, text="Login", bootstyle=INFO, command=self.abrir_login)
        self.usuario_btn.pack(side=RIGHT)

    def _criar_notebook(self):
        self.notebook = tb.Notebook(self.app, bootstyle=PRIMARY)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def _adicionar_abas(self):
        AbaPainel(self.notebook)
        AbaUsuario(self.notebook)
        AbaSetor(self.notebook)
        AbaEquipamento(self.notebook)

    def abrir_login(self):
        # Janela de login
        self.login_janela = tb.Toplevel(self.app)
        self.login_janela.title("Login")
        self.login_janela.geometry("300x200")
        self.login_janela.resizable(False, False)

        # Frame interno para organizar os widgets
        frame = tb.Frame(self.login_janela, padding=10)
        frame.pack(fill="both", expand=True)

        # E-mail
        tb.Label(frame, text="E-mail:", anchor="w").pack(fill="x", pady=(5,2))
        self.email_entry = tb.Entry(frame)
        self.email_entry.pack(fill="x", pady=(0,5))

        # Senha
        tb.Label(frame, text="Senha:", anchor="w").pack(fill="x", pady=(5,2))
        self.senha_entry = tb.Entry(frame, show="*")
        self.senha_entry.pack(fill="x", pady=(0,10))

        # Botão Entrar
        tb.Button(frame, text="Entrar", bootstyle=SUCCESS, command=self.fazer_login).pack(fill="x", pady=10)

    def fazer_login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()

        usuario = db.verificar_login(email, senha)
        if usuario:
            self.usuario_logado = usuario
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario['nome']}!")
            self.login_janela.destroy()
            self._atualizar_cabecalho_usuario()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def _atualizar_cabecalho_usuario(self):
        # Remove botão login
        self.usuario_btn.destroy()

        # Cria um frame à direita para organizar nome + logout
        frame_direita = tb.Frame(self.cabecalho)
        frame_direita.pack(side=RIGHT)

        # Nome do usuário à esquerda dentro do frame
        tb.Label(frame_direita, text=f"{self.usuario_logado['nome']} ({self.usuario_logado['perfil']})",
                font=("Arial", 12), bootstyle=SECONDARY).pack(side=LEFT)

        # Botão logout à direita dentro do frame
        tb.Button(frame_direita, text="Logout", bootstyle=DANGER, command=self.fazer_logout).pack(side=RIGHT, padx=5)

    def fazer_logout(self):
        self.usuario_logado = None
        messagebox.showinfo("Logout", "Você saiu do sistema.")

        # Remove apenas os widgets filhos do cabeçalho
        for widget in self.cabecalho.winfo_children():
            widget.destroy()

        # Reconstrói os widgets do cabeçalho (nome do app e botão login)
        tb.Label(self.cabecalho, text="ManuSys", font=("Arial", 18, "bold"), bootstyle=PRIMARY).pack(side=LEFT)
        self.usuario_btn = tb.Button(self.cabecalho, text="Login", bootstyle=INFO, command=self.abrir_login)
        self.usuario_btn.pack(side=RIGHT)


def iniciar_interface():
    App()
