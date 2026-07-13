import json
import pandas as pd
from datetime import datetime
from pathlib import Path

CAMINHO_BASE = Path(__file__).resolve().parent.parent
CAMINHO_LOGS = CAMINHO_BASE / "logs"
#CAMINHO_DADOS = CAMINHO_BASE / "data"
CAMINHO_HISTORICO = CAMINHO_BASE / "historico_chats"

CAMINHO_LOGS.mkdir(parents=True, exist_ok=True)
CAMINHO_HISTORICO.mkdir(parents=True, exist_ok=True)
ARQUIVO_SISTEMA = CAMINHO_LOGS / "sistema.log"
ARQUIVO_AUDITORIA = CAMINHO_HISTORICO / "auditoria_chat.jsonl"

# Função para persistir histórico de mensagem
def registrar_auditoria(papel: str, texto: str):
    """Salva a mensagem num arquivo jsonl com timestamp preciso (ISO 8601 com fuso horário)."""
    timestamp_preciso = datetime.now().astimezone().isoformat()

    registro = {
        "data_hora": timestamp_preciso,
        "papel": papel,
        "mensagem": texto
    }

    with open(ARQUIVO_AUDITORIA, "a", encoding="utf-8") as arquivo_log:
        arquivo_log.write(json.dumps(registro, ensure_ascii=False) + "\n")

# Funções de contexto do usuário
def obter_estilo_usuario(caminho_dados: Path) -> tuple:
    """
    Lê a idade do arquivo de perfil, calcula o ano de nascimento
    e define os estilos de comunicação e resposta baseados em gerações.
    """
    caminho_arquivo = caminho_dados / "perfil_investidor.json"

    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        perfil = json.load(arquivo)

    # assume 35 como fallback se o campo estiver ausente
    idade = perfil.get("idade", 35)

    ano_atual = datetime.now().year
    ano_nascimento = ano_atual - idade

    # Lógica Geracional
    if 1946 <= ano_nascimento <= 1964:  # Baby Boomers
        estilo_com_geracao = "Comunicação formal, direta, estruturada e detalhista."
        estilo_resp_geracao = "Passo a passo mais detalhado e com mais etapas com linguagem acessível. Evitar jargões em inglês, fornecer instruções passo a passo explícitas e confirmar ações importantes antes de executá-las."

    elif 1965 <= ano_nascimento <= 1980:  # Geração X
        estilo_com_geracao = "Pragmática, direto ao ponto. Evitam rodeios e valorizam a autonomia ('me diga o que precisa e eu faço')."
        estilo_resp_geracao = "Ser eficiente, apresentar opções claras e diretas, utilizando um tom profissional sem a necessidade de excessiva formalidade."

    elif 1981 <= ano_nascimento <= 1996:  # Geração Y / Millennials
        estilo_com_geracao = "Misturam o formal e o informal."
        estilo_resp_geracao = "Pode usar tom conversacional, emojis contextuais e fluxos rápidos. Não ser repetitivo."

    elif 1997 <= ano_nascimento <= 2009:  # Geração Z (fechando em 2009 para não chocar com a Alpha)
        estilo_com_geracao = "Use emojis, comunicação informal."
        estilo_resp_geracao = "Linguagem casual, processar áudio ou texto de forma intercambiável e entregar respostas curtas que vão direto ao ponto central da interação."

    elif ano_nascimento >= 2010:  # Geração Alpha
        estilo_com_geracao = "A comunicação é fluida e informal."
        estilo_resp_geracao = "Direto."

    else:  # Fallback para nascidos antes de 1946
        estilo_com_geracao = "Comunicação extremamente respeitosa e formal."
        estilo_resp_geracao = "Linguagem clara, paciente, sem gírias e muito detalhada."

    # Caso o estilo de comunicação vá pro json no futuro por escolha do usuário
    estilo_com = perfil.get("estilo_comunicacao", estilo_com_geracao)
    estilo_resp = perfil.get("estilo_resposta", estilo_resp_geracao)

    return estilo_com, estilo_resp

def construir_contexto_usuario(caminho_dados: Path) -> str:
    """Lê os arquivos de dados do usuário e monta um bloco de texto estruturado."""
    with open(caminho_dados / "perfil_investidor.json", "r", encoding="utf-8") as arquivo:
        perfil = json.load(arquivo)

    df_transacoes = pd.read_csv(caminho_dados / "transacoes.csv")
    receitas = df_transacoes[df_transacoes['tipo'] == 'entrada']['valor'].sum()
    despesas = df_transacoes[df_transacoes['tipo'] == 'saida']['valor'].sum()

    metas_texto = ""
    for meta in perfil.get("metas", []):
        metas_texto += f"- {meta['meta']}: R$ {meta['valor_necessario']:.2f} (Prazo: {meta['prazo']})\n"

    carteira_texto = ""
    carteira = perfil.get("carteira", {})
    if carteira:
        for ativo, val in carteira.items():
            carteira_texto += f"- {ativo}: R$ {val:.2f}\n"
    else:
        carteira_texto = "Sua carteira está vazia no momento.\n"

    contexto = f"""
        [DADOS DO USUÁRIO ATUAL]
        Nome: {perfil['nome']}
        Idade: {perfil.get('idade', 'Não informada')} anos
        Perfil de Investidor: {perfil['perfil_investidor']}

        [RESUMO FINANCEIRO]
        Renda Mensal: R$ {perfil['renda_mensal']:.2f}
        Patrimônio Total: R$ {perfil['patrimonio_total']:.2f}
        Reserva de Emergência Atual: R$ {perfil['reserva_emergencia_atual']:.2f}

        [FLUXO DE CAIXA DO MÊS]
        Total de Entradas: R$ {receitas:.2f}
        Total de Saídas: R$ {despesas:.2f}

        [METAS E PLANEJAMENTO DE SONHOS]
        {metas_texto}

        [CARTEIRA DE INVESTIMENTOS ATUAL]
        {carteira_texto}
        """

    return contexto
# Funções para chamadas do agente
def buscar_historico_atendimento(tema: str = "") -> str:
    """
        Busca o histórico de chamados/atendimentos do cliente.
        Pode filtrar por um tema específico (ex: CDB, Tesouro). Se o tema for vazio (""), retorna os últimos atendimentos gerais.
        """

    caminho_arquivo = CAMINHO_DADOS / "historico_atendimento.csv"

    if not caminho_arquivo.exists():
        return "Erro: Arquivo de histórico de atendimento não encontrado no sistema."

    df_historico = pd.read_csv(caminho_arquivo)

    if tema and tema.strip():
        df_filtrado = df_historico[df_historico['tema'].str.lower().str.contains(tema.lower())]
    else:
        df_filtrado = df_historico.tail()

    if df_filtrado.empty:
        return f"Nenhum ticket de atendimento encontrado para o tema: {tema}."

    resultado_texto = "Histórico de tickets encontrados:\n"
    for _, linha in df_filtrado.iterrows():
        status = "Resolvido" if str(linha['resolvido']).lower() == "sim" else "Pendente"
        resultado_texto += f"- Data: {linha['data']} | Tema: {linha['tema']} | Status: {status} | Resumo: {linha['resumo']}\n"

    return resultado_texto

def consultar_ultimas_transacoes() -> str:
    """Consulta o extrato detalhado, gastos e as últimas movimentações financeiras do usuário."""

    caminho_arquivo = CAMINHO_DADOS / "transacoes.csv"

    if not caminho_arquivo.exists():
        return "Erro: Arquivo de transações não encontrado no sistema."


    df_transacoes = pd.read_csv(caminho_arquivo)
    resultado_texto = "Últimas transações do usuário:\n"

    for _, linha in df_transacoes.tail(30).iterrows():
        resultado_texto += f"- {linha['data']} | {linha['descricao']} ({linha['categoria']}): R$ {linha['valor']:.2f} [{linha['tipo']}]\n"

    return resultado_texto

def consultar_produtos_financeiros(risco: str) -> str: # receberá risco ou perfil do investidor
    """Consulta o catálogo de produtos financeiros disponíveis filtrando pelo nível de risco (baixo, medio, alto)."""

    caminho_arquivo = CAMINHO_DADOS / "produtos_financeiros.json"

    if not caminho_arquivo.exists():
        return "Erro: Arquivo de catálogo de produtos financeiros não encontrado no sistema."

    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        produtos = json.load(arquivo)

    produtos_filtrados = [p for p in produtos if p.get("risco", "").lower() == risco.lower()]

    if not produtos_filtrados:
        return f"Nenhum produto encontrado para o nível de risco: {risco}."

    resultado_texto = f"Produtos da corretora com risco '{risco}':\n"
    for p in produtos_filtrados:
        resultado_texto += f"- {p['nome']} (Categoria: {p['categoria']}) | Rentabilidade: {p['rentabilidade']} | Aporte Mínimo: R$ {p['aporte_minimo']:.1f} | Indicado para: {p['indicado_para']}\n"

    return resultado_texto

def atualizar_carteira_investimentos(ativo: str, valor: float, operacao: str) -> str:
    # TODO: atualizar a carteira de investimentos do usuário (pensar em adicionar preço compra e venda, quantidade, data, tipo_operacao)
    """
        Atualiza a carteira do usuário no perfil_investidor.json.
        ativo: Nome da ação/investimento (ex: 'PETR4', 'Tesouro').
        valor: Valor financeiro em Reais da operação.
        operacao: 'compra' (adiciona) ou 'venda' (subtrai).
        """
    caminho_arquivo = CAMINHO_DADOS / "perfil_investidor.json"

    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        perfil = json.load(arquivo)

    if "carteira" not in perfil:
        perfil["carteira"] = {}

    saldo_atual = perfil["carteira"].get(ativo, 0.0)

    if operacao.lower() == "compra":
        perfil["carteira"][ativo] = saldo_atual + valor
    elif operacao.lower() == "venda":
        perfil["carteira"][ativo] = max(0.0, saldo_atual - valor)

    # Atualiza o patrimônio somando a nova carteira
    perfil["patrimonio_total"] = sum(perfil["carteira"].values()) + perfil.get("reserva_emergencia_atual", 0.0)

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(perfil, arquivo, indent=2, ensure_ascii=False)

    novo_saldo = perfil["carteira"][ativo]
    return f"Sucesso: {operacao} de {ativo} registrada. Novo saldo: R$ {novo_saldo:.1f}."

def registrar_nova_transacao(descricao: str, categoria: str, valor: float, tipo: str) -> str:
    """
        Registra um novo gasto ou receita manualmente no extrato (transacoes.csv).
        tipo: deve ser obrigatoriamente 'entrada' ou 'saida'.
        """
    caminho_arquivo = CAMINHO_DADOS / "transacoes.csv"

    nova_linha = pd.DataFrame([{
        "data": datetime.now().strftime("%Y-%m-%d"),
        "descricao": descricao,
        "categoria": categoria,
        "valor": float(valor),
        "tipo": tipo.lower()
    }])

    if not caminho_arquivo.exists():
        nova_linha.to_csv(caminho_arquivo, index=False)
    else:
        nova_linha.to_csv(caminho_arquivo, mode='a', header=False, index=False)

    return f"Transação '{descricao}' de R$ {valor:.1f} ({tipo}) adicionada ao CSV."


def gerar_relatorio_financeiro() -> str:
    """
    Acione esta função EXCLUSIVAMENTE quando o usuário pedir um relatório financeiro,
    resumo geral das contas ou análise da saúde financeira.
    """
    
    template_instrucao = """
    [INSTRUÇÃO DE FORMATAÇÃO PARA A RESPOSTA ATUAL]
    O usuário solicitou o Relatório Financeiro. Leia os dados financeiros presentes no seu contexto e 
    estruture sua resposta EXATAMENTE com os 5 tópicos abaixo, mantendo o Estilo de Comunicação do usuário:

    1. Resumo Financeiro Atual (Renda, Patrimônio, Reserva).
    2. Fluxo de Caixa do Mês (Entradas, Saídas, Saldo Livre e análise se está positivo/negativo).
    3. Metas e Planejamento de Sonhos (Liste as metas, valor atual, quanto falta, e a porcentagem atingida. Calcule e diga em quantos meses a meta será batida caso o Saldo Livre seja direcionado a ela).
    4. Carteira de Investimentos Atual (Ativos e Análise).
    5. Saúde Financeira e Recomendações (Insights de economia e dicas de investimentos baseadas no perfil).
    """

    return template_instrucao

# TODO: criar funções individuais para editar e remover dados não obrigatórios, como:
# Meta, transações adicionadas...

# TODO: estudar forma de reduzir o system prompt fazendo igual a função de gerar relatório financeiro
# TODO: Função pra enviar relatório por email, talvez com dados estruturados num arquivo


