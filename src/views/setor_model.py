class Setor:
    _id_counter = 1

    def __init__(self, nome, responsavel=None):
        self.id = Setor._id_counter
        Setor._id_counter += 1
        self.nome = nome
        self.responsavel = responsavel

    def __str__(self):
        if self.responsavel:
            return f"Id:{self.id}, Setor: {self.nome}, Responsável: {self.responsavel}"
        return f"Id:{self.id}, Setor: {self.nome}, Responsável: (não definido)"

    def alterar_responsavel(self, novo_responsavel):
        self.responsavel = novo_responsavel

    def remover_responsavel(self):
        self.responsavel = None

    def alterar_nome(self, novo_nome):
        self.nome = novo_nome

# ===== Aba Setor =====
