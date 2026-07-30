from langchain_text_splitters import RecursiveCharacterTextSplitter

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


# Bloco de teste
if __name__ == "__main__":
    import sys
    sys.path.append("..")  # permite importar o document_loader que está fora desta pasta
    from src.document_loader import carregar_todos_documentos

    documentos = carregar_todos_documentos("../data/documentos")

    for nome_arquivo, texto in documentos.items():
        chunks = dividir_em_chunks(texto)
        print(f"{nome_arquivo}: {len(texto)} caracteres → {len(chunks)} chunks")