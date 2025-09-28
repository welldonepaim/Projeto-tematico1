import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from Setor import Setor
import json, os

ARQUIVO = "setores.json"
setores = []

# Persistência de dados

def carregar_dados():
    global setores
    if os.path.exists(ARQUIVO) and os.path.getsize(ARQUIVO) > 0:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                setores = [Setor(**s) for s in dados]
            except json.JSONDecodeError:
                setores = []
    atualizar_lista()

def salvar_dados():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump([s.__dict__ for s in setores], f, indent=4, ensure_ascii=False)
######################################################################################

# Funções GUI

def atualizar_lista(lista=None):
    lista_setores.delete(0, tk.END)
    mostrar = lista if lista is not None else setores
    for s in mostrar:
        lista_setores.insert(tk.END, str(s))

def criar_setor():
    nome = entry_nome.get().strip()
    if nome:
        s = Setor(nome)
        setores.append(s)
        entry_nome.delete(0, tk.END)
        atualizar_lista()
        salvar_dados()
        lbl_criar_status.config(text=f"Setor '{nome}' criado!", fg="green")
    else:
        lbl_criar_status.config(text="Digite um nome válido!", fg="red")

def alterar_responsavel(selecionado=None):
    if selecionado is None:
        nome = entry_alt_nome.get().strip()
        setor = next((s for s in setores if s.nome == nome), None)
    else:
        setor = selecionado

    responsavel = entry_alt_responsavel.get().strip()
    if setor and responsavel:
        setor.alterar_responsavel(responsavel)
        entry_alt_nome.delete(0, tk.END)
        entry_alt_responsavel.delete(0, tk.END)
        atualizar_lista()
        salvar_dados()
        lbl_alt_status.config(text=f"Responsável alterado!", fg="green")
    else:
        lbl_alt_status.config(text="Setor ou responsável inválido!", fg="red")

def remover_responsavel(selecionado=None):
    if selecionado is None:
        nome = entry_rem_nome.get().strip()
        setor = next((s for s in setores if s.nome == nome), None)
    else:
        setor = selecionado

    if setor:
        if setor.responsavel:
            setor.remover_responsavel()
            lbl_rem_status.config(text=f"Responsável removido!", fg="green")
        else:
            lbl_rem_status.config(text="Setor não possui responsável!", fg="orange")
        atualizar_lista()
        salvar_dados()
        entry_rem_nome.delete(0, tk.END)
    else:
        lbl_rem_status.config(text="Setor não encontrado!", fg="red")
######################################################################################

# Funções para menu contexto

def mostrar_menu_contexto(event):
    try:
        idx = lista_setores.nearest(event.y)
        lista_setores.selection_clear(0, tk.END)
        lista_setores.selection_set(idx)
        menu_contexto.post(event.x_root, event.y_root)
    except IndexError:
        pass

def alterar_responsavel_lista():
    sel = lista_setores.curselection()
    if sel:
        idx = sel[0]
        setor = setores_filtrados[idx] if 'setores_filtrados' in globals() else setores[idx]
        novo_resp = simpledialog.askstring("Alterar responsável", f"Novo responsável para {setor.nome}:")
        if novo_resp:
            setor.alterar_responsavel(novo_resp)
            atualizar_lista(setores_filtrados if 'setores_filtrados' in globals() else None)
            salvar_dados()

def remover_responsavel_lista():
    sel = lista_setores.curselection()
    if sel:
        idx = sel[0]
        setor = setores_filtrados[idx] if 'setores_filtrados' in globals() else setores[idx]
        setor.remover_responsavel()
        atualizar_lista(setores_filtrados if 'setores_filtrados' in globals() else None)
        salvar_dados()


def filtrar_lista(event=None):
    global setores_filtrados
    filtro = search_var.get().lower()
    setores_filtrados = [s for s in setores if filtro in s.nome.lower() or (s.responsavel and filtro in s.responsavel.lower())]
    atualizar_lista(setores_filtrados)
    
######################################################################################

#Janela principal

root = tk.Tk()
root.title("Gerenciamento de Setores")
root.geometry("500x450")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

#  Aba Criar Setor 
aba_criar = ttk.Frame(notebook)
notebook.add(aba_criar, text="Criar Setor")

tk.Label(aba_criar, text="Nome do Setor:").pack(pady=10)
entry_nome = tk.Entry(aba_criar, width=30)
entry_nome.pack()
tk.Button(aba_criar, text="Criar Setor", command=criar_setor).pack(pady=10)
lbl_criar_status = tk.Label(aba_criar, text="")
lbl_criar_status.pack()

# Aba Mostrar Setores 
aba_mostrar = ttk.Frame(notebook)
notebook.add(aba_mostrar, text="Mostrar Setores")

tk.Label(aba_mostrar, text="Buscar Setor:").pack(pady=5)
search_var = tk.StringVar()
entry_busca = tk.Entry(aba_mostrar, textvariable=search_var, width=40)
entry_busca.pack(pady=5)
lista_setores = tk.Listbox(aba_mostrar, width=60)
lista_setores.pack(pady=10, padx=10, fill='both', expand=True)

entry_busca.bind("<KeyRelease>", filtrar_lista)
lista_setores.bind("<Button-3>", mostrar_menu_contexto)

# Menu de contexto
menu_contexto = tk.Menu(root, tearoff=0)
menu_contexto.add_command(label="Alterar Responsável", command=alterar_responsavel_lista)
menu_contexto.add_command(label="Remover Responsável", command=remover_responsavel_lista)

#  Aba Alterar Responsável 
aba_alterar = ttk.Frame(notebook)
notebook.add(aba_alterar, text="Alterar Setor")

tk.Label(aba_alterar, text="Nome do Setor:").pack(pady=5)
entry_alt_nome = tk.Entry(aba_alterar, width=30)
entry_alt_nome.pack()
tk.Label(aba_alterar, text="Novo Responsável:").pack(pady=5)
entry_alt_responsavel = tk.Entry(aba_alterar, width=30)
entry_alt_responsavel.pack()
tk.Button(aba_alterar, text="Alterar", command=alterar_responsavel).pack(pady=10)
lbl_alt_status = tk.Label(aba_alterar, text="")
lbl_alt_status.pack()

#  Aba Remover Responsável 
aba_remover = ttk.Frame(notebook)
notebook.add(aba_remover, text="Remover Setor")

tk.Label(aba_remover, text="Nome do Setor:").pack(pady=10)
entry_rem_nome = tk.Entry(aba_remover, width=30)
entry_rem_nome.pack()
tk.Button(aba_remover, text="Remover", command=remover_responsavel).pack(pady=10)
lbl_rem_status = tk.Label(aba_remover, text="")
lbl_rem_status.pack()

######################################################################################

carregar_dados()

root.mainloop()

