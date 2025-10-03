# src/session.py

usuario_logado = None

def set_usuario(usuario):
    """Define o usuário logado"""
    global usuario_logado
    usuario_logado = usuario

def get_usuario():
    """Retorna o usuário logado"""
    return usuario_logado

def logout():
    """Desloga o usuário"""
    global usuario_logado
    usuario_logado = None
