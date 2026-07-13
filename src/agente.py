from google import genai
from google.genai import types
from google.genai import errors
from config import GEMINI_API_KEY
from templates import SYSTEM_PROMPT
from pathlib import Path
from utils import (
    obter_logger,
    obter_estilo_usuario,
    construir_contexto_usuario,
    consultar_ultimas_transacoes,
    consultar_produtos_financeiros,
    buscar_historico_atendimento,
    atualizar_carteira_investimentos,
    registrar_nova_transacao,
    gerar_relatorio_financeiro
)

logger = obter_logger("agente")
client = genai.Client(api_key=GEMINI_API_KEY)
CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "data"

def responder_usuario(mensagem_usuario, historico_streamlit):
    try:
        logger.info("Iniciando preparação de contexto para o Gemini.")
        estilo_com, estilo_resp = obter_estilo_usuario(CAMINHO_DADOS)
        prompt_personalizado = SYSTEM_PROMPT.replace("[[ESTILO_COM]]", estilo_com)
        prompt_personalizado = prompt_personalizado.replace("[[ESTILO_RESP]]", estilo_resp)

        contexto_dinamico = construir_contexto_usuario(CAMINHO_DADOS)
        prompt_completo = f"{prompt_personalizado}\n\n{contexto_dinamico}"

        configuracao = types.GenerateContentConfig(
            system_instruction=prompt_completo,
            temperature=0.3,
            tools=[
                consultar_produtos_financeiros,
                buscar_historico_atendimento,
                consultar_ultimas_transacoes,
                atualizar_carteira_investimentos,
                registrar_nova_transacao,
                gerar_relatorio_financeiro
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
        logger.info("Enviando requisição para a API do Google.")
        resposta = chat.send_message(mensagem_usuario)
        logger.info("Resposta recebida com sucesso da API.")
        return resposta.text

    except errors.APIError as erro:
        if erro.code == 429 or "quota" in str(erro).lower() or "exhausted" in str(erro).lower():
            logger.warning("Limite de cota da API do Gemini atingido.")
            return "Atingimos o limite de uso temporário da inteligência artificial. Por favor, aguarde cerca de um minuto e tente enviar sua mensagem novamente."
        logger.error(f"Falha na API do Gemini: {erro}", exc_info=True)
        return "Desculpe, enfrentei uma instabilidade técnica na comunicação. Poderia tentar novamente em instantes?"

    except Exception as erro:
        logger.error(f"Erro inesperado no sistema: {erro}", exc_info=True)
        return "Ocorreu um erro interno no sistema. Tente novamente mais tarde."
