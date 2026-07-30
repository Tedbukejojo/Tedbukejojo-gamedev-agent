from pypdf import PdfReader
import os

def carregar_texto_pdf(caminho_arquivo):
    """
    Lê um arquivo PDF e retorna todo o texto extraído como uma única string.
    """
    leitor = PdfReader(caminho_arquivo)
    texto_completo = ""

    for pagina in leitor.pages:
        texto_completo += pagina.extract_text()

    return texto_completo


# Bloco de teste: só roda quando executamos este arquivo diretamente
def carregar_todos_documentos(pasta_documentos):
    """
    Percorre uma pasta, lê todos os arquivos PDF encontrados
    e retorna um dicionário: {nome_do_arquivo: texto_extraido}
    """
    documentos = {}

    for nome_arquivo in os.listdir(pasta_documentos):
        if nome_arquivo.endswith(".pdf"):
            caminho_completo = os.path.join(pasta_documentos, nome_arquivo)
            texto = carregar_texto_pdf(caminho_completo)
            documentos[nome_arquivo] = texto
            print(f"Lido: {nome_arquivo} ({len(texto)} caracteres)")

    return documentos

if __name__ == "__main__":
    pasta = "../data/documentos"
    todos_documentos = carregar_todos_documentos(pasta)

    print(f"\nTotal de documentos carregados: {len(todos_documentos)}")

