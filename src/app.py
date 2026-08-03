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


@st.cache_resource
def carregar_vectorstore():
    return carregar_banco_vetorial("data/faiss_index")


vectorstore = carregar_vectorstore()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta = st.chat_input("Pergunte algo sobre desenvolvimento de jogos com Godot...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando na base de conhecimento..."):
            resposta, fontes = responder_pergunta(pergunta, vectorstore)
            texto_final = resposta + f"\n\n*Fontes: {', '.join(fontes)}*"
            st.markdown(texto_final)

    st.session_state.mensagens.append({"role": "assistant", "content": texto_final})