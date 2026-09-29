# modo_agente.py — Um agente escrito "na marra": um LLM que decide quais ferramentas chamar.
#
# IDEIA CENTRAL (para a aula):
#   Um agente é só um LOOP em torno de um LLM:
#
#     1. Mandamos a conversa + a lista de ferramentas para o LLM.
#     2. O LLM responde de um de dois jeitos:
#          a) "quero chamar a ferramenta X com estes argumentos"
#          b) uma resposta final em texto
#     3. Em (a), NÓS executamos a função Python, devolvemos o resultado ao LLM e voltamos ao passo 1.
#        Em (b), terminamos.
#
#   O LLM nunca executa nada sozinho: ele só PEDE. Quem executa é o nosso código.
#   Cada ferramenta, por sua vez, é outra chamada a um LLM (com o seu próprio prompt).
#   Então o agente é "um LLM orquestrador com acesso a outros LLMs".
#
# As ferramentas e o system prompt vêm de agent.py (AgenteEducacional): nada é duplicado aqui.

import os

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Limite de voltas do loop, para o agente não ficar chamando ferramentas para sempre
# (cada volta é uma chamada paga à API).
MAX_VOLTAS = 5

# Semanas que existem no plano_ensino.txt
SEMANA_MIN, SEMANA_MAX = 1, 16

# Nomes dos argumentos que representam "número da semana" nas ferramentas de agent.py
ARGUMENTOS_DE_SEMANA = ("semana", "semana_atual", "tool_input")


# ─────────────────────────────────────────────
# Langfuse (opcional): observabilidade dos passos do agente
# ─────────────────────────────────────────────

def criar_callbacks() -> list:
    """
    Devolve [handler do Langfuse] se as variáveis LANGFUSE_* estiverem definidas.
    Caso contrário (ou se o pacote não estiver instalado), devolve lista vazia
    e o agente funciona normalmente, só que sem enviar traces.
    """
    if not (os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")):
        return []
    try:
        from langfuse.langchain import CallbackHandler
        return [CallbackHandler()]
    except Exception:
        # Pacote ausente ou configuração inválida: seguimos sem observabilidade
        return []


# ─────────────────────────────────────────────
# Execução de UMA ferramenta pedida pelo LLM
# ─────────────────────────────────────────────

def _erro_de_semana(argumentos: dict):
    """
    O LLM pode inventar uma semana que não existe (ex.: 20).
    Devolve uma mensagem de erro clara, ou None se a semana está OK (ou não foi informada).
    A mensagem volta para o LLM, que explica o problema ao aluno.
    """
    for nome in ARGUMENTOS_DE_SEMANA:
        if nome in argumentos:
            try:
                semana = int(argumentos[nome])
            except (TypeError, ValueError):
                return f"Erro: '{argumentos[nome]}' não é um número de semana válido."
            if not SEMANA_MIN <= semana <= SEMANA_MAX:
                return (f"Erro: a semana {semana} não existe. "
                        f"O curso tem as semanas {SEMANA_MIN} a {SEMANA_MAX}.")
    return None


def _executar_ferramenta(ferramentas_por_nome: dict, chamada: dict, config: dict) -> str:
    """Executa a ferramenta pedida pelo LLM e devolve o resultado como texto."""
    nome, argumentos = chamada["name"], chamada["args"]

    if nome not in ferramentas_por_nome:
        return f"Erro: a ferramenta '{nome}' não existe."

    erro = _erro_de_semana(argumentos)
    if erro:
        return erro

    try:
        return str(ferramentas_por_nome[nome].invoke(argumentos, config=config))
    except Exception as e:
        # Se a ferramenta falhar (ex.: API fora do ar), o LLM fica sabendo e pode avisar o aluno
        return f"Erro ao executar '{nome}': {e}"


# ─────────────────────────────────────────────
# O agente em si: o loop
# ─────────────────────────────────────────────

def executar_agente(agente, mensagem: str, historico: list = None) -> tuple:
    """
    Roda o loop do agente para uma mensagem do aluno.

    Parâmetros:
        agente:    instância de AgenteEducacional (de onde vêm llm, tools e system_prompt)
        mensagem:  o que o aluno escreveu
        historico: mensagens anteriores, no formato [{"role": "user"|"assistant", "content": "..."}]

    Retorna (resposta_final, passos), onde "passos" é a lista de ferramentas chamadas:
        [{"ferramenta": "gerar_exercicios", "argumentos": {...}, "resultado": "..."}, ...]
    A interface usa "passos" para mostrar ao aluno o raciocínio do agente.
    """
    config = {"callbacks": criar_callbacks()}

    # 1) Damos ao LLM o "cardápio" de ferramentas (nome + descrição + argumentos)
    llm_com_ferramentas = agente.llm.bind_tools(agente.tools)
    ferramentas_por_nome = {f.name: f for f in agente.tools}

    # 2) Montamos a conversa: system prompt + histórico + mensagem nova
    mensagens = [agente.system_prompt]
    for msg in historico or []:
        classe = HumanMessage if msg["role"] == "user" else AIMessage
        mensagens.append(classe(content=msg["content"]))
    mensagens.append(HumanMessage(content=mensagem))

    passos = []

    for _ in range(MAX_VOLTAS):
        # 3) O LLM decide: pede ferramentas ou responde
        resposta = llm_com_ferramentas.invoke(mensagens, config=config)
        mensagens.append(resposta)

        # Sem pedido de ferramenta = resposta final. Fim do loop.
        if not resposta.tool_calls:
            return resposta.content, passos

        # 4) O LLM pediu ferramentas (pode ser mais de uma): executamos cada uma
        for chamada in resposta.tool_calls:
            resultado = _executar_ferramenta(ferramentas_por_nome, chamada, config)
            passos.append({
                "ferramenta": chamada["name"],
                "argumentos": chamada["args"],
                "resultado": resultado,
            })
            # 5) Devolvemos o resultado ao LLM, identificando qual pedido ele responde
            mensagens.append(ToolMessage(content=resultado, tool_call_id=chamada["id"]))
        # ...e voltamos ao passo 3: o LLM lê os resultados e decide o próximo passo

    return ("Cheguei ao limite de passos sem terminar. "
            "Tente pedir uma coisa de cada vez."), passos


# ─────────────────────────────────────────────
# Para comparar (opcional na aula): o mesmo agente em 1 linha com a biblioteca
# ─────────────────────────────────────────────
#
#   from langchain.agents import create_agent   # requer langchain>=1.0
#   agente_pronto = create_agent(model=agente.llm, tools=agente.tools,
#                                system_prompt=agente.system_prompt.content)
#   agente_pronto.invoke({"messages": [("user", "me dá exercícios da semana 3")]})
#
# Tudo o que escrevemos acima (o loop, o limite de voltas, a execução das ferramentas)
# é o que essa linha faz por baixo dos panos.
