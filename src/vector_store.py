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


def criar_banco_vetorial(textos, metadados, tamanho_lote=8, pausa_segundos=12, caminho_salvar=None):
    """
    Gera os embeddings e monta o índice FAISS em lotes pequenos,
    com uma pausa entre eles, para não estourar o limite de requisições
    do tier gratuito da API do Gemini.

    Se caminho_salvar for informado, salva o progresso em disco após
    cada lote, para não perder o trabalho já feito em caso de erro.
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

        if caminho_salvar:
            vectorstore.save_local(caminho_salvar)

        if numero_lote < total_lotes:
            time.sleep(pausa_segundos)

    return vectorstore


def salvar_banco_vetorial(vectorstore, caminho):
    """
    Salva o índice FAISS em disco, para não precisar gerar os embeddings de novo
    toda vez que rodarmos o projeto.
    """
    vectorstore.save_local(caminho)


def carregar_banco_vetorial(caminho):
    """
    Carrega um índice FAISS previamente salvo em disco,
    sem precisar gerar os embeddings novamente.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return FAISS.load_local(
        caminho,
        embeddings,
        allow_dangerous_deserialization=True,
    )


# Bloco de teste
if __name__ == "__main__":
    caminho_indice = "../data/faiss_index"

    print("Carregando banco vetorial salvo...")
    vectorstore = carregar_banco_vetorial(caminho_indice)

    pergunta_teste = "O que é o Godot Engine?"
    resultados = vectorstore.similarity_search(pergunta_teste, k=3)

    print(f"\nPergunta: {pergunta_teste}")
    print(f"Top {len(resultados)} chunks mais relevantes encontrados:\n")

    for i, resultado in enumerate(resultados, start=1):
        print(f"--- Resultado {i} (fonte: {resultado.metadata['fonte']}) ---")
        print(resultado.page_content[:200])
        print()