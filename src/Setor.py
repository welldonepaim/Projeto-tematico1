##falta adicionar o atributo de identificação 

class Setor:
    def __init__(self, nome, responsavel=None):
        self.id= ##adicionar o atributo com incrementação automática
        self.nome = nome
        self.responsavel = responsavel
##to String
    def __str__(self):
        if self.responsavel:
            return f"Id:{self.id},Setor: {self.nome}, Responsável: {self.responsavel}"
        return f"Id{self.id},Setor: {self.nome}, Responsável: (não definido)"

    # Alterar nome do setor
    def alterar_setor(self, novo_nome):
        self.nome = novo_nome

    # Remover setor 
    def remover_setor(self):
        self.nome = None
        self.responsavel = None

    # Adicionar responsável
    def adicionar_responsavel(self, responsavel):
        if self.responsavel:
            print(f"O setor já possui responsável ({self.responsavel}).")
        else:
            self.responsavel = responsavel

    # Remover responsável
    def remover_responsavel(self):
        if self.responsavel:
            print(f"Responsável {self.responsavel} removido.")
            self.responsavel = None
        else:
            print("Este setor não tem responsável definido.")

    # Alterar responsável
    def alterar_responsavel(self, novo_responsavel):
        self.responsavel = novo_responsavel

