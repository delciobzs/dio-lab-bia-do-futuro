from google import genai
from google.genai import types
from google.genai import errors
from config import GEMINI_API_KEY
from templates import SYSTEM_PROMPT
from utils import (
    obter_estilo_usuario,
    construir_contexto_usuario,
    consultar_ultimas_transacoes,
    consultar_produtos_financeiros,
    buscar_historico_atendimento,
    atualizar_carteira_investimentos,
    registrar_nova_transacao
)


client = genai.Client(api_key=GEMINI_API_KEY)

def responder_usuario(mensagem_usuario, historico_streamlit):
    try:
        # TODO: adicionar log de inicio da preparação de contexto
        estilo_com, estilo_resp = "Direto e profissional", "detalhado" #obter_estilo_usuario()
        prompt_personalizado = SYSTEM_PROMPT.replace("[[ESTILO_COM]]", estilo_com)
        prompt_personalizado = prompt_personalizado.replace("[[ESTILO_RESP]]", estilo_resp)

        contexto_dinamico = construir_contexto_usuario()
        prompt_completo = f"{prompt_personalizado}\n\n{contexto_dinamico}"

        configuracao = types.GenerateContentConfig(
            system_instruction=prompt_completo,
            temperature=0.3,
            tools=[
                consultar_produtos_financeiros,
                buscar_historico_atendimento,
                consultar_ultimas_transacoes,
                atualizar_carteira_investimentos,
                registrar_nova_transacao
            ]
        )

        historico_gemini = []
       
        for msg in historico_streamlit:
            # adaptar o histórico do streamlit pra gemini
            papel = "user" if msg["usuario"] == "user" else "model"
            historico_gemini.append(
                types.Content(
                    role=papel,
                    parts=[types.Part.from_text(text=msg["texto"])]
                )
            )
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=configuracao,
            history=historico_gemini
        )
        # TODO: adicionar log de chamada de API
        resposta = chat.send_message(mensagem_usuario)
        # TODO: adicionar log de reposta de API
        return resposta.text

    except errors.APIError as erro:
        if erro.code == 429 or "quota" in str(erro).lower() or "exhausted" in str(erro).lower():
            # TODO: adicionar log de limite de API
            return "Atingimos o limite de uso temporário da inteligência artificial. Por favor, aguarde cerca de um minuto e tente enviar sua mensagem novamente."
        # TODO: adicionar log de falhas de API
        return "Desculpe, enfrentei uma instabilidade técnica na comunicação. Poderia tentar novamente em instantes?"

    except Exception as erro:
        # TODO: adicionar log de falhas de código
        return "Ocorreu um erro interno no sistema. Tente novamente mais tarde."
