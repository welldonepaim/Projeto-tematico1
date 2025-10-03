class Usuario:
    def __init__(self, id=None, nome="", login="", senha="", perfil="", contato="", status="Ativo"):
        self.id = id
        self.nome = nome
        self.login = login
        self.senha = senha
        self.perfil = perfil
        self.contato = contato
        self.status = status

    def is_admin(self):
        return self.perfil == "Administrador"

    def is_gestor(self):
        return self.perfil == "Gestor"

    def is_active(self):
        return self.status == "Ativo"
