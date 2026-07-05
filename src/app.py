import streamlit as st


def app():
    st.header("MorFi", help="MorFi: seu aplicativo financeiro")
    st.write("Seu gerenciador financeiro inteligente. ### :green[Sempre à sua maneira]")

    if "mensagens" not in st.session_state:
        st.session_state["mensagens"] = []

    for mensagem in st.session_state["mensagens"]:
        with st.chat_message(mensagem["usuario"]):
            st.write(mensagem["texto"])

    mensagem_usuario = st.chat_input("No que posso te ajudar hoje, Delcio?")

    if mensagem_usuario:
        st.session_state["mensagens"].append({
            "usuario": "user",
            "texto": mensagem_usuario
        })

        st.session_state["mensagens"].append({
            "usuario": "assistant",
            "texto": "O agente de IA do MorFi será adicionado em breve! 🚀"
        })

        st.rerun()

if __name__ == "__main__":
    app()