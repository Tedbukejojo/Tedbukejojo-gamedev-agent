import streamlit as st
import sys
import os

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


def montar_historico_recente(mensagens, max_turnos=3):
    """
    Converte o histórico de mensagens do Streamlit (formato role/content)
    em pares pergunta/resposta, limitado aos últimos turnos, para
    alimentar a memória de curto prazo do agente.
    """
    turnos = []
    pergunta_pendente = None

    for mensagem in mensagens:
        if mensagem["role"] == "user":
            pergunta_pendente = mensagem["content"]
        elif mensagem["role"] == "assistant" and pergunta_pendente is not None:
            resposta_limpa = mensagem["content"].split("\n\n*Fontes:")[0]
            turnos.append({"pergunta": pergunta_pendente, "resposta": resposta_limpa})
            pergunta_pendente = None

    return turnos[-max_turnos:]


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

if st.session_state.pergunta_sugerida:
    pergunta = st.session_state.pergunta_sugerida
    st.session_state.pergunta_sugerida = None

if pergunta:
    historico = montar_historico_recente(st.session_state.mensagens)

    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando na base de conhecimento..."):
            try:
                resposta, fontes = responder_pergunta(pergunta, vectorstore, historico=historico)

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