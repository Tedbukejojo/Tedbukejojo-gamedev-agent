from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def montar_prompt(pergunta, chunks_relevantes, historico=None):
    """
    Monta o texto (prompt) que será enviado ao Gemini,
    combinando os trechos encontrados, o histórico recente da conversa
    e a pergunta do usuário.
    """
    contexto = "\n\n---\n\n".join(chunk.page_content for chunk in chunks_relevantes)

    secao_historico = ""
    if historico:
        linhas = []
        for turno in historico:
            linhas.append(f"Usuário: {turno['pergunta']}")
            linhas.append(f"Assistente: {turno['resposta']}")
        secao_historico = (
            "Histórico recente da conversa (use apenas para entender o "
            "contexto da pergunta, NÃO como fonte de informação):\n"
            + "\n".join(linhas) + "\n\n"
        )

    prompt = f"""Você é um assistente especializado em desenvolvimento de jogos.
Responda à pergunta do usuário utilizando APENAS as informações do contexto abaixo.
Se a resposta não estiver no contexto, diga claramente que não encontrou essa informação na base de conhecimento — não invente respostas.

{secao_historico}Contexto:
{contexto}

Pergunta: {pergunta}

Resposta:"""

    return prompt


def extrair_texto_resposta(resposta):
    """
    Extrai apenas o texto da resposta do Gemini, ignorando
    metadados internos como assinaturas de raciocínio.
    """
    conteudo = resposta.content

    if isinstance(conteudo, str):
        return conteudo

    partes_texto = [
        bloco["text"] for bloco in conteudo
        if isinstance(bloco, dict) and bloco.get("type") == "text"
    ]
    return "".join(partes_texto)


def responder_pergunta(pergunta, vectorstore, k=3, historico=None):
    """
    Fluxo completo do RAG: busca os chunks relevantes (usando também
    a pergunta anterior, se houver, para melhorar buscas de seguimento),
    monta o prompt com histórico e gera a resposta com o Gemini.
    """
    consulta_busca = pergunta
    if historico:
        ultima_pergunta = historico[-1]["pergunta"]
        consulta_busca = f"{ultima_pergunta} {pergunta}"

    chunks_relevantes = vectorstore.similarity_search(consulta_busca, k=k)
    prompt = montar_prompt(pergunta, chunks_relevantes, historico=historico)

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
    resposta = llm.invoke(prompt)

    texto_resposta = extrair_texto_resposta(resposta)
    fontes = {chunk.metadata["fonte"] for chunk in chunks_relevantes}

    return texto_resposta, fontes


# Bloco de teste
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from src.vector_store import carregar_banco_vetorial

    vectorstore = carregar_banco_vetorial("../data/faiss_index")

    pergunta_teste = "O que é o Godot Engine?"
    resposta, fontes = responder_pergunta(pergunta_teste, vectorstore)

    print(f"Pergunta: {pergunta_teste}\n")
    print(f"Resposta: {resposta}\n")
    print(f"Fontes consultadas: {fontes}")