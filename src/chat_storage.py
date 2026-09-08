import sqlite3
import uuid
from datetime import datetime

CAMINHO_BANCO = "data/conversas.db"


def obter_conexao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """
    Cria as tabelas do banco de dados, caso ainda não existam.
    Seguro para chamar toda vez que a aplicação iniciar.
    """
    conexao = obter_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS conversas (
                                                            id TEXT PRIMARY KEY,
                                                            titulo TEXT NOT NULL,
                                                            criada_em TEXT NOT NULL
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS mensagens (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            conversa_id TEXT NOT NULL,
                                                            role TEXT NOT NULL,
                                                            conteudo TEXT NOT NULL,
                                                            criada_em TEXT NOT NULL,
                                                            FOREIGN KEY (conversa_id) REFERENCES conversas (id)
                       )
                   """)

    conexao.commit()
    conexao.close()


def criar_nova_conversa():
    """
    Cria uma nova conversa vazia no banco e retorna seu ID único.
    """
    conversa_id = str(uuid.uuid4())
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO conversas (id, titulo, criada_em) VALUES (?, ?, ?)",
        (conversa_id, "Nova conversa", datetime.now().isoformat()),
    )
    conexao.commit()
    conexao.close()
    return conversa_id


def salvar_mensagem(conversa_id, role, conteudo):
    """
    Salva uma mensagem (do usuário ou do assistente) associada a uma conversa.
    Na primeira pergunta do usuário, também define o título da conversa.
    """
    conexao = obter_conexao()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO mensagens (conversa_id, role, conteudo, criada_em) VALUES (?, ?, ?, ?)",
        (conversa_id, role, conteudo, datetime.now().isoformat()),
    )

    if role == "user":
        cursor.execute(
            "SELECT COUNT(*) as total FROM mensagens WHERE conversa_id = ? AND role = 'user'",
            (conversa_id,),
        )
        total_perguntas = cursor.fetchone()["total"]
        if total_perguntas == 1:
            titulo = conteudo[:50] + ("..." if len(conteudo) > 50 else "")
            cursor.execute(
                "UPDATE conversas SET titulo = ? WHERE id = ?",
                (titulo, conversa_id),
            )

    conexao.commit()
    conexao.close()


def listar_conversas():
    """
    Retorna todas as conversas salvas, da mais recente para a mais antiga.
    """
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, criada_em FROM conversas ORDER BY criada_em DESC")
    conversas = cursor.fetchall()
    conexao.close()
    return [dict(c) for c in conversas]


def carregar_mensagens(conversa_id):
    """
    Retorna todas as mensagens de uma conversa específica, em ordem cronológica.
    """
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT role, conteudo FROM mensagens WHERE conversa_id = ? ORDER BY id ASC",
        (conversa_id,),
    )
    mensagens = cursor.fetchall()
    conexao.close()
    return [{"role": m["role"], "content": m["conteudo"]} for m in mensagens]