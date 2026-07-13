import json
from pathlib import Path
import streamlit as st
from agente import responder_usuario

def app():
    CAMINHO_DIRETORIO = Path(__file__).resolve().parent.parent
    CAMINHO_JSON = CAMINHO_DIRETORIO / "data" / "perfil_investidor.json"
    AVATAR_MORFI = str(CAMINHO_DIRETORIO / "assets" / "morphi-avatar-ia.png")

    with open(CAMINHO_JSON, "r", encoding="utf-8") as arquivo:
        perfil_investidor = json.load(arquivo)
        avatar_usuario_arquivo = perfil_investidor.get("avatar")

        if avatar_usuario_arquivo:
            caminho_potencial = (CAMINHO_JSON.parent / avatar_usuario_arquivo).resolve()
            if caminho_potencial.exists():
                AVATAR_USUARIO = str(caminho_potencial)
            else:
                AVATAR_USUARIO = "👤"
        else:
            AVATAR_USUARIO = "👤"

    if "historico_mensagens" not in st.session_state:
        st.session_state.historico_mensagens = []
    if "processando" not in st.session_state:
        st.session_state.processando = False

    col_avatar_morfi, col_titulo_pagina = st.columns([1, 6])
    with col_avatar_morfi:
        st.image(AVATAR_MORFI, width=100)

    with col_titulo_pagina:
        st.markdown(
            f"""
            <style>
            .efeito-digitar {{
                display: inline-block;
                overflow: hidden;
                white-space: nowrap;
                border-right: 2px solid #800000;
                vertical-align: bottom;
                width: 0;
                animation: 
                    digitando 3s steps(23, end) forwards,
                    piscando-cursor 0.75s step-end infinite;
            }}
            @keyframes digitando {{
                from {{ width: 0 }}
                to {{ width: 23ch }}
            }}
            @keyframes piscando-cursor {{
                from, to {{ border-color: transparent }}
                50% {{ border-color: #800000 }}
            }}
            </style>

            <h1 style="margin: 0; padding: 0; font-size: 36px; line-height: 1.1;">
                Olá, <span style="color: grey;">{perfil_investidor["nome"]}</span>! Eu sou o <span style="color: #800000;">MorFi</span>
            </h1>
            <p style="margin: 2px 0 0 0; padding: 0; font-size: 20px; color: #31333F;">
                Seu gerenciador financeiro inteligente. 
                <span class="efeito-digitar" style="color: #800000; font-weight: bold;">Sempre à sua maneira...</span>
            </p>
            """, unsafe_allow_html=True
        )

    for mensagem in st.session_state["historico_mensagens"]:
        if mensagem["usuario"] == "user":
            with st.chat_message("user", avatar=AVATAR_USUARIO):
                st.write(mensagem["texto"])
        else:
            with st.chat_message("assistant", avatar=AVATAR_MORFI):
                st.write(mensagem["texto"])

    if len(st.session_state.historico_mensagens) > 0:
        texto_placeholder = "Envie outra mensagem ou tire mais dúvidas..."
    else:
        texto_placeholder = f"No que posso te ajudar hoje, {perfil_investidor['nome']}?"

    mensagem_usuario = st.chat_input(
        texto_placeholder,
        disabled=st.session_state.processando,
        max_chars=200
    )

    if mensagem_usuario:
        st.session_state["historico_mensagens"].append({
            "usuario": "user",
            "texto": mensagem_usuario
        })

        st.session_state.processando = True
        st.rerun()

    if st.session_state.processando:
        ultima_msg = st.session_state["historico_mensagens"][-1]["texto"]

        with st.chat_message("assistant", avatar=AVATAR_MORFI):
            with st.spinner("Pensando..."):
                historico_para_envio = st.session_state["historico_mensagens"][:-1]
                resposta_agente = responder_usuario(ultima_msg, historico_para_envio)
                st.write(resposta_agente)

            st.session_state["historico_mensagens"].append({
                "usuario": "assistant",
                "texto": resposta_agente
            })

            st.session_state.processando = False
            st.rerun()

if __name__ == "__main__":
    app()