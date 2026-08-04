import streamlit as st
import sys
import os

# Permite importar os módulos da pasta src/ independente de onde o Streamlit for executado
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import carregar_banco_vetorial
from src.rag_agent import responder_pergunta

st.set_page_config(page_title="GameDev-Agent", page_icon="🎮")

st.title("🎮 GameDev-Agent")
st.caption("Assistente de IA especializado em desenvolvimento de jogos, baseado na documentação do Godot Engine.")
with st.sidebar:
    st.header("Sobre o projeto")
    st.markdown(
        """
        O **GameDev-Agent** é um assistente de IA baseado em RAG
        (Retrieval-Augmented Generation), desenvolvido como projeto
        do Challenge Alura + Oracle Next Education (ONE).

        Ele responde perguntas com base em documentos técnicos
        sobre desenvolvimento de jogos.
        """
    )

    st.divider()

    st.subheader("Base de conhecimento")
    st.markdown(
        """
        Este projeto utiliza trechos da documentação oficial do
        **Godot Engine**, licenciada sob
        [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/),
        de autoria de Juan Linietsky, Ariel Manzur e a comunidade Godot.
        """
    )

    st.divider()

    st.subheader("Tecnologias")
    st.markdown(
        """
        - Python
        - LangChain
        - FAISS
        - Google Gemini
        - Streamlit
        """

    )
    st.divider()

    st.markdown("Feito por **Joice Rodrigues** (Tedbukejojo)")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/joicegenerich/)")


@st.cache_resource
def carregar_vectorstore():
    return carregar_banco_vetorial("data/faiss_index")


vectorstore = carregar_vectorstore()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

if "pergunta_sugerida" not in st.session_state:
    st.session_state.pergunta_sugerida = None

# Mostra sugestões de perguntas só quando a conversa ainda não começou
if not st.session_state.mensagens:
    st.markdown("**Experimente perguntar:**")
    perguntas_exemplo = [
        "O que é o Godot Engine?",
        "Qual linguagem de programação o Godot utiliza?",
        "Como organizar as pastas de um projeto no Godot?",
    ]
    colunas = st.columns(len(perguntas_exemplo))
    for coluna, pergunta_exemplo in zip(colunas, perguntas_exemplo):
        with coluna:
            if st.button(pergunta_exemplo):
                st.session_state.pergunta_sugerida = pergunta_exemplo

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta = st.chat_input("Pergunte algo sobre desenvolvimento de jogos com Godot...")

# Se um botão de sugestão foi clicado, usa essa pergunta
if st.session_state.pergunta_sugerida:
    pergunta = st.session_state.pergunta_sugerida
    st.session_state.pergunta_sugerida = None

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando na base de conhecimento..."):
            try:
                resposta, fontes = responder_pergunta(pergunta, vectorstore)

                if "não encontrei" in resposta.lower():
                    texto_final = resposta
                else:
                    texto_final = resposta + f"\n\n*Fontes: {', '.join(fontes)}*"

            except Exception as erro:
                texto_final = (
                    "⚠️ Não foi possível processar sua pergunta no momento. "
                    "Isso pode acontecer se o limite gratuito de uso da API foi atingido. "
                    "Tente novamente em alguns instantes."
                )
                st.caption(f"Detalhes técnicos (para depuração): {erro}")

            st.markdown(texto_final)

    st.session_state.mensagens.append({"role": "assistant", "content": texto_final})