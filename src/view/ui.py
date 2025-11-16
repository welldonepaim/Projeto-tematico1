import ttkbootstrap as tb
import os
import sys
import tkinter as tk
from tkinter import PhotoImage, messagebox
from ttkbootstrap.constants import *

from src.view.painel import AbaPainel
from src.view.usuario import AbaUsuario
from src.view.setor import AbaSetor
from src.view.equipamento import AbaEquipamento
from src.view.manutencao import AbaManutencao
from src.view.planejamento import AbaPlanejamento
from src.dao.usuario_dao import verificar_login
from src.model import session


class App:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("ManuSys")
        self.app.geometry("1200x680")

        # Define ícone multiplataforma
        if sys.platform.startswith("win"):
            icone_path = r"C:/Users/william/Documents/GitHub/Projeto-tematico1/image/favicon.ico"
            if os.path.exists(icone_path):
                self.app.iconbitmap(icone_path)
        else:
            icone_path = os.path.join(os.path.dirname(__file__), "image", "favicon.png")
            if os.path.exists(icone_path):
                self.app.iconphoto(True, PhotoImage(file=icone_path))

        self._criar_cabecalho()
        self._criar_notebook()
        self._adicionar_abas()

        # Bind para atualizar setores quando mudar para a aba Equipamentos
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

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
        self.aba_painel = AbaPainel(self.notebook)
        self.aba_usuario = AbaUsuario(self.notebook)
        self.aba_setor = AbaSetor(self.notebook)
        self.aba_equipamento = AbaEquipamento(self.notebook)
        self.aba_manutencao = AbaManutencao(self.notebook)
        self.aba_planejamento = AbaPlanejamento(self.notebook)
    def _on_tab_changed(self, event):
        tab_id = event.widget.select() 
        tab_text = event.widget.tab(tab_id, "text")

        if tab_text == "Equipamentos":
            self.aba_equipamento._atualizar_setores()
            self.aba_equipamento.carregar_dados()

        elif tab_text == "Manutenções":
            self.aba_manutencao._atualizar_equipamentos()
            self.aba_manutencao._atualizar_usuarios()
            self.aba_manutencao.gerar_os_do_dia()
            self.aba_manutencao.carregar_dados()
            self.aba_manutencao.limpar_formulario()
        elif tab_text == "Painel":
            self.aba_painel.refresh()


        elif tab_text == "Setores":
            self.aba_setor.carregar_dados()
        elif tab_text == "Planejamento":
            self.aba_planejamento.carregar_planejamentos()

    def abrir_login(self):
        self.login_janela = tb.Toplevel(self.app)
        self.login_janela.title("Login")
        self.login_janela.geometry("300x200")
        self.login_janela.resizable(False, False)

        frame = tb.Frame(self.login_janela, padding=10)
        frame.pack(fill="both", expand=True)

        tb.Label(frame, text="E-mail:", anchor="w").pack(fill="x", pady=(5,2))
        self.email_entry = tb.Entry(frame)
        self.email_entry.pack(fill="x", pady=(0,5))

        tb.Label(frame, text="Senha:", anchor="w").pack(fill="x", pady=(5,2))
        self.senha_entry = tb.Entry(frame, show="*")
        self.senha_entry.pack(fill="x", pady=(0,10))

        tb.Button(frame, text="Entrar", bootstyle=SUCCESS, command=self.fazer_login).pack(fill="x", pady=10)

    def fazer_login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()

        usuario = verificar_login(email, senha)
        if usuario:
            session.set_usuario(usuario)
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario.nome}!")
            self.login_janela.destroy()
            self._atualizar_cabecalho_usuario()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def _atualizar_cabecalho_usuario(self):
        self.usuario_btn.destroy()

        frame_direita = tb.Frame(self.cabecalho)
        frame_direita.pack(side=RIGHT)

        usuario = session.get_usuario()
        tb.Label(frame_direita, text=f"{usuario.nome} ({usuario.perfil})",
                font=("Arial", 12), bootstyle=SECONDARY).pack(side=LEFT)
        tb.Button(frame_direita, text="Logout", bootstyle=DANGER, command=self.fazer_logout).pack(side=RIGHT, padx=5)

    def fazer_logout(self):
        session.logout()
        messagebox.showinfo("Logout", "Você saiu do sistema.")

        for widget in self.cabecalho.winfo_children():
            widget.destroy()

        tb.Label(self.cabecalho, text="ManuSys", font=("Arial", 18, "bold"), bootstyle=PRIMARY).pack(side=LEFT)
        self.usuario_btn = tb.Button(self.cabecalho, text="Login", bootstyle=INFO, command=self.abrir_login)
        self.usuario_btn.pack(side=RIGHT)


def iniciar_interface():
    App()
