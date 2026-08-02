from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import time


def dividir_em_chunks(texto, tamanho_chunk=1000, sobreposicao=100):
    """
    Divide um texto longo em pedaços menores (chunks),
    mantendo uma pequena sobreposição entre eles para não perder contexto nas bordas.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=tamanho_chunk,
        chunk_overlap=sobreposicao,
    )
    return splitter.split_text(texto)


load_dotenv()


def criar_banco_vetorial(textos, metadados, tamanho_lote=10, pausa_segundos=6):
    """
    Gera os embeddings e monta o índice FAISS em lotes pequenos,
    com uma pausa entre eles, para não estourar o limite de requisições
    do tier gratuito da API do Gemini.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = None

    total_lotes = (len(textos) - 1) // tamanho_lote + 1

    for i in range(0, len(textos), tamanho_lote):
        lote_textos = textos[i:i + tamanho_lote]
        lote_metadados = metadados[i:i + tamanho_lote]
        numero_lote = i // tamanho_lote + 1

        print(f"Processando lote {numero_lote}/{total_lotes} ({len(lote_textos)} chunks)...")

        if vectorstore is None:
            vectorstore = FAISS.from_texts(lote_textos, embeddings, metadatas=lote_metadados)
        else:
            vectorstore.add_texts(lote_textos, metadatas=lote_metadados)

        if numero_lote < total_lotes:
            time.sleep(pausa_segundos)

    return vectorstore


def salvar_banco_vetorial(vectorstore, caminho):
    """
    Salva o índice FAISS em disco, para não precisar gerar os embeddings de novo
    toda vez que rodarmos o projeto.
    """
    vectorstore.save_local(caminho)


# Bloco de teste
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from src.document_loader import carregar_todos_documentos

    documentos = carregar_todos_documentos("../data/documentos")

    todos_textos = []
    todos_metadados = []

    for nome_arquivo, texto in documentos.items():
        chunks = dividir_em_chunks(texto)
        for chunk in chunks:
            todos_textos.append(chunk)
            todos_metadados.append({"fonte": nome_arquivo})

    print(f"Total de chunks a serem transformados em embeddings: {len(todos_textos)}")

    vectorstore = criar_banco_vetorial(todos_textos, todos_metadados)
    salvar_banco_vetorial(vectorstore, "../data/faiss_index")

    print("Banco vetorial criado e salvo com sucesso!")