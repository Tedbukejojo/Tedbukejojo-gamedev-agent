import sys
sys.path.append("..")

from src.document_loader import carregar_todos_documentos
from src.vector_store import dividir_em_chunks, criar_banco_vetorial, salvar_banco_vetorial

documentos = carregar_todos_documentos("../data/documentos")

todos_textos = []
todos_metadados = []

for nome_arquivo, texto in documentos.items():
    chunks = dividir_em_chunks(texto)
    for chunk in chunks:
        todos_textos.append(chunk)
        todos_metadados.append({"fonte": nome_arquivo})

print(f"Total de chunks a serem transformados em embeddings: {len(todos_textos)}")

vectorstore = criar_banco_vetorial(
    todos_textos,
    todos_metadados,
    caminho_salvar="../data/faiss_index",
)
salvar_banco_vetorial(vectorstore, "../data/faiss_index")

print("Banco vetorial recriado e salvo com sucesso!")