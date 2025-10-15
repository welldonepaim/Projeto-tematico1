import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
# feito em aula , em curto tempo , com a inteção de pegar as informações que são disponibilizadas no sistema tasy

##ainda não foram configurados os campos e nem selecionados.
class AbaPlanejamento:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Planejamento")

        self.entries = {}

        self._montar_formulario()
        self._montar_botoes()

    # ----------------- Montagem do formulário -----------------
    def _montar_formulario(self):
        labels = [
            ("Estabelecimento", "Hospital Geral de Cxs do Sul"),
            ("Descrição", ""),
            ("Contador", ""),
            ("Frequência", ""),
            ("Dias previstos execução", ""),
            ("Dias geração", ""),
            ("Data inicial", ""),
            ("Regra data inicial", "Fixa - Data inicial do planejamento"),
            ("Prioridade", "Alta"),
            ("Pessoa solicitante", "285363 - Willian Paim da Silva"),
            ("Equipamento específico", "Dano"),
            ("Setor do equipamento", ""),
            ("Solicitante da ordem serviço", "Solicitante informado na regra da preventiva"),
            ("Usuário previsto", ""),
            ("Usuário início nas preventivas", ""),
            ("Perfil", ""),
            ("Planejamento superior", ""),
            ("Planejamento", ""),
            ("Trabalho", ""),
            ("Estágio", ""),
            ("Dias sobreposição", ""),
            ("Tipo ordem cliente", ""),
            ("Grupo suporte", "")
        ]

        for i, (label_text, default) in enumerate(labels):
            tb.Label(self.frame, text=label_text + ":", anchor="w").grid(row=i, column=0, padx=5, pady=5, sticky="w")

            # Campo de data
            if label_text == "Data inicial":
                entry = tb.DateEntry(self.frame, dateformat="%d/%m/%Y")
                entry.set_date(datetime.today().date())
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

            # Combobox para opções pré-definidas
            elif label_text in ["Frequência", "Setor do equipamento", "Usuário previsto", "Perfil",
                                "Planejamento superior", "Planejamento", "Trabalho", "Estágio",
                                "Tipo ordem cliente", "Grupo suporte"]:
                combo = tb.Combobox(self.frame, values=["---"], state="readonly")
                combo.set("---")
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.entries[label_text] = combo

            # Campo de texto simples
            else:
                entry = tb.Entry(self.frame)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                if default:
                    entry.insert(0, default)
                    entry.configure(state="readonly")  # bloqueia campos fixos
                self.entries[label_text] = entry

        self.frame.columnconfigure(1, weight=1)

    # ----------------- Botões -----------------
    def _montar_botoes(self):
        frame_botoes = tb.Frame(self.frame)
        frame_botoes.grid(row=23, column=0, columnspan=2, pady=15, sticky="ew")

        tb.Button(frame_botoes, text="Salvar Planejamento", bootstyle=SUCCESS, command=self.salvar).pack(side=LEFT, expand=True, fill="x", padx=5)
        tb.Button(frame_botoes, text="Limpar", bootstyle=SECONDARY, command=self.limpar_formulario).pack(side=LEFT, expand=True, fill="x", padx=5)

    # ----------------- Funções básicas -----------------
    def salvar(self):
        # Aqui entrará sua lógica de integração com o banco (DAO)
        dados = {campo: entry.get() for campo, entry in self.entries.items()}
        print("Planejamento salvo:", dados)

    def limpar_formulario(self):
        for campo, entry in self.entries.items():
            if isinstance(entry, tb.Entry):
                if entry.cget("state") != "readonly":
                    entry.delete(0, "end")
            elif isinstance(entry, tb.Combobox):
                entry.set("---")
            elif isinstance(entry, tb.DateEntry):
                entry.set_date(datetime.today().date())

# ----------------- Teste isolado -----------------
if __name__ == "__main__":
    root = tb.Window(title="Planejamento", themename="superhero", size=(800, 700))
    notebook = tb.Notebook(root)
    notebook.pack(fill="both", expand=True)

    AbaPlanejamento(notebook)

    root.mainloop()
