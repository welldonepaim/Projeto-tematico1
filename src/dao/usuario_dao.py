from src.model.usuario import Usuario
from src.dao import db

def listar_usuarios():
    rows = db.listar_usuarios()
    return [Usuario(*row) for row in rows]

def inserir_usuario(usuario: Usuario):
    return db.inserir_usuario(usuario.nome, usuario.login, usuario.senha,
                              usuario.perfil, usuario.contato, usuario.status)

def atualizar_usuario(usuario: Usuario):
    return db.atualizar_usuario(usuario.id, usuario.nome, usuario.login, usuario.senha,
                                usuario.perfil, usuario.contato, usuario.status)

def excluir_usuario(usuario_id):
    return db.excluir_usuario(usuario_id)
