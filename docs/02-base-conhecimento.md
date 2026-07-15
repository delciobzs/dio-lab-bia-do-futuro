# Base de Conhecimento

## Dados Utilizados

Foram utilizados os quatro arquivos mockados disponíveis na pasta `data/`, sem substituição por datasets externos:
| Arquivo                     | Formato | Utilização no Agente                                                                                                                                                                                                         |
| --------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `perfil_investidor.json`    | JSON    | Base do contexto do usuário: nome, idade, profissão, renda, patrimônio, perfil de risco, reserva de emergência, metas e carteira de investimentos. Também define o estilo de comunicação (via cálculo geracional pela idade) |
| `transacoes.csv`            | CSV     | Calcula entradas/saídas do mês (fluxo de caixa) e alimenta a ferramenta `consultar_ultimas_transacoes`; também recebe novos registros via `registrar_nova_transacao`                                                         |
| `historico_atendimento.csv` | CSV     | Consultado sob demanda pela ferramenta `buscar_historico_atendimento`, filtrando por tema (ex: CDB, Tesouro Selic) ou retornando os últimos atendimentos                                                                     |
| `produtos_financeiros.json` | JSON    | Consultado pela ferramenta `consultar_produtos_financeiros`, filtrando por nível de risco (baixo/médio/alto) compatível com o perfil do cliente                                                                              |
---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

O `perfil_investidor.json` foi expandido com um campo dinâmico `carteira` (dicionário de ativo → valor investido), que é criado e atualizado em tempo real pela ferramenta `atualizar_carteira_investimentos` conforme o usuário registra compras/vendas na conversa. O `patrimonio_total` também passou a ser recalculado automaticamente como a soma da carteira mais a reserva de emergência, em vez de ser um valor fixo. O `transacoes.csv` recebe novas linhas em tempo real via `registrar_nova_transacao`, mantendo o extrato sempre atualizado.
Criei também imagens pra representar o usuário fictício e um avatar para o agente, respectivamente `joao-silva-ia.pn` e `morfi-avatar-ia.png` na pasta `assets/`.

---

## Estratégia de Integração

### Como os dados são carregados?
Os dados são lidos do disco (JSON/CSV, via `pandas` e `json`) a cada nova mensagem do usuário, dentro de `responder_usuario()` em `agente.py`. Isso garante que o contexto enviado ao modelo reflita o estado mais recente dos arquivos (por exemplo, após uma transação ter sido registrada na própria conversa). Além do contexto estático montado no início da requisição, o modelo também pode consultar os dados dinamicamente durante a conversa por meio de function calling (as ferramentas leem o CSV/JSON no momento em que são acionadas).

### Como os dados são usados no prompt?

> Os dados vão no system prompt? São consultados dinamicamente?

Um resumo do perfil, do fluxo de caixa do mês, das metas e da carteira é montado como texto (função `construir_contexto_usuario`) e anexado ao `system_instruction` enviado ao Gemini a cada chamada. Isso dá ao agente uma "visão geral" imediata do cliente sem precisar chamar uma ferramenta. Informações mais detalhadas ou específicas (extrato completo, catálogo de produtos, histórico de tickets) são consultadas dinamicamente por function calling, apenas quando o assunto da conversa exige.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
[DADOS DO USUÁRIO ATUAL]
Nome: João Silva
Idade: 32 anos
Perfil de Investidor: moderado

[RESUMO FINANCEIRO]
Renda Mensal: R$ 5000.00
Patrimônio Total: R$ 15000.00
Reserva de Emergência Atual: R$ 10000.00

[FLUXO DE CAIXA DO MÊS]
Total de Entradas: R$ 5000.00
Total de Saídas: R$ 2489.90

[METAS E PLANEJAMENTO DE SONHOS]
- Completar reserva de emergência: R$ 15000.00 (Prazo: 2026-06)
- Entrada do apartamento: R$ 50000.00 (Prazo: 2027-12)

[CARTEIRA DE INVESTIMENTOS ATUAL]
Sua carteira está vazia no momento.
...
```
