# tools.py — Ferramentas do agente educacional expandido

import os
import json
import re
from datetime import datetime
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# ─────────────────────────────────────────────
# Utilitários compartilhados
# ─────────────────────────────────────────────

def _load_plano(plano_path: str = None) -> str:
    """Carrega o plano de ensino a partir do arquivo."""
    if plano_path is None:
        base = os.path.dirname(os.path.abspath(__file__))
        plano_path = os.path.join(base, "plano_ensino.txt")
    with open(plano_path, "r", encoding="utf-8") as f:
        return f.read()


def _get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """Retorna uma instância do LLM configurada."""
    return ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4.1-mini",
        temperature=temperature,
    )


def _semana_conteudo(plano: str, semana: int) -> str:
    """Extrai o conteúdo de uma semana específica do plano."""
    linhas = plano.strip().split("\n")
    conteudo = []
    capturando = False
    for linha in linhas:
        if f"Semana {semana}:" in linha:
            capturando = True
            conteudo.append(linha)
        elif capturando and linha.strip().startswith("Semana "):
            break
        elif capturando:
            conteudo.append(linha)
    return "\n".join(conteudo)


# ─────────────────────────────────────────────
# FERRAMENTA 1 — Gerar Exercícios por Semana
# ─────────────────────────────────────────────

def gerar_exercicios(semana: int) -> str:
    """
    Gera uma lista de 5 exercícios (2 teóricos, 2 práticos, 1 desafio)
    para a semana informada, com base no plano de ensino.
    """
    plano = _load_plano()
    llm = _get_llm(temperature=0.4)

    prompt = PromptTemplate.from_template(
        """
        Você é um assistente educacional de uma faculdade de tecnologia.
        Seus alunos estão nos primeiros semestres de Ciência de Dados ou Banco de Dados.

        Plano de ensino completo:
        {plano}

        Com base no plano acima, gere uma lista de exercícios para a **Semana {semana}**.

        Estrutura obrigatória da resposta:
        1. Inicie com um parágrafo explicando as subcompetências da semana e sua importância.
        2. Liste exatamente 5 exercícios numerados:
           - 2 exercícios marcados com **(Teórico)**
           - 2 exercícios marcados com **(Prático)**
           - 1 exercício marcado com **(Desafio)** — especialmente desafiador
        3. Finalize recomendando que o aluno busque o **monitor** em caso de dúvidas.

        Regras:
        - Nunca inclua conteúdo de semanas futuras.
        - Tudo deve ser escrito em **Português do Brasil**.
        - Seja claro, didático e encorajador.
        """
    )

    chain = prompt | llm
    return chain.invoke({"semana": semana, "plano": plano}).content


# ─────────────────────────────────────────────
# FERRAMENTA 2 — Resumo de Conteúdo da Semana
# ─────────────────────────────────────────────

def resumir_semana(semana: int) -> str:
    """
    Gera um resumo didático completo do conteúdo da semana informada,
    com explicações, exemplos de código Python e dicas de estudo.
    """
    plano = _load_plano()
    conteudo_semana = _semana_conteudo(plano, semana)
    llm = _get_llm(temperature=0.3)

    prompt = PromptTemplate.from_template(
        """
        Você é um professor de programação experiente e didático.
        Seus alunos são iniciantes em Python, cursando Ciência de Dados ou Banco de Dados.

        Conteúdo da Semana {semana} do plano de ensino:
        {conteudo}

        Crie um **resumo completo e didático** desta semana contendo:

        ## 📚 Resumo da Semana {semana}

        ### O que você vai aprender
        (Explique em linguagem simples o que será estudado e por que é importante)

        ### Conceitos-chave
        (Para cada subcompetência da semana, explique o conceito com clareza)

        ### Exemplos práticos em Python
        (Forneça pelo menos 2 exemplos de código Python comentados, usando blocos ```python```)

        ### Dicas de estudo
        (3 a 5 dicas práticas para fixar o conteúdo desta semana)

        ### Conexão com semanas anteriores
        (Explique como este conteúdo se conecta com o que foi visto antes — se for semana 1, pule este item)

        Escreva tudo em **Português do Brasil**, de forma clara, encorajadora e acessível para iniciantes.
        """
    )

    chain = prompt | llm
    return chain.invoke({"semana": semana, "conteudo": conteudo_semana}).content


# ─────────────────────────────────────────────
# FERRAMENTA 3 — Corrigir Exercício do Aluno
# ─────────────────────────────────────────────

def corrigir_exercicio(semana: int, enunciado: str, resposta_aluno: str) -> str:
    """
    Corrige a resposta de um aluno para um exercício, fornecendo
    feedback detalhado, nota e sugestões de melhoria.
    """
    plano = _load_plano()
    conteudo_semana = _semana_conteudo(plano, semana)
    llm = _get_llm(temperature=0.2)

    prompt = PromptTemplate.from_template(
        """
        Você é um professor corretor de exercícios de programação Python.
        Seja justo, detalhado e encorajador na sua correção.

        Contexto da semana {semana}:
        {conteudo_semana}

        Enunciado do exercício:
        {enunciado}

        Resposta do aluno:
        {resposta_aluno}

        Faça uma correção completa seguindo esta estrutura:

        ## ✅ Correção do Exercício

        ### Análise da Resposta
        (Analise o que o aluno fez corretamente e o que precisa melhorar)

        ### Nota: X/10
        (Atribua uma nota de 0 a 10 com justificativa clara)

        ### Erros encontrados
        (Liste os erros, se houver, com explicação didática de cada um)

        ### Solução sugerida
        (Mostre uma solução correta e bem comentada em bloco ```python```)

        ### Pontos positivos
        (Destaque o que o aluno fez bem, mesmo que parcialmente)

        ### Próximos passos
        (Sugira como o aluno pode melhorar e o que estudar a seguir)

        Escreva tudo em **Português do Brasil**. Seja encorajador e construtivo.
        Se a resposta não for código Python, adapte a correção para o tipo de exercício (teórico).
        """
    )

    chain = prompt | llm
    return chain.invoke({
        "semana": semana,
        "conteudo_semana": conteudo_semana,
        "enunciado": enunciado,
        "resposta_aluno": resposta_aluno,
    }).content


# ─────────────────────────────────────────────
# FERRAMENTA 4 — Plano de Estudos Personalizado
# ─────────────────────────────────────────────

def gerar_plano_estudos(semana_atual: int, horas_por_dia: int, dificuldades: str) -> str:
    """
    Gera um plano de estudos personalizado para o aluno com base
    na semana atual, horas disponíveis e dificuldades relatadas.
    """
    plano = _load_plano()
    llm = _get_llm(temperature=0.4)

    prompt = PromptTemplate.from_template(
        """
        Você é um orientador educacional especialista em programação para iniciantes.

        Plano de ensino completo:
        {plano}

        Informações do aluno:
        - Semana atual: {semana_atual}
        - Horas disponíveis por dia para estudo: {horas_por_dia}h
        - Dificuldades relatadas: {dificuldades}

        Crie um **plano de estudos semanal personalizado** para este aluno:

        ## 📅 Plano de Estudos Personalizado

        ### Diagnóstico
        (Analise as dificuldades do aluno e o que precisa de atenção especial)

        ### Plano da semana (dia a dia)
        (Distribua as atividades de estudo nos dias da semana, respeitando as {horas_por_dia}h/dia disponíveis)
        Use o formato:
        - **Segunda-feira** (Xh): [atividade]
        - **Terça-feira** (Xh): [atividade]
        ... e assim por diante

        ### Metas da semana
        (Liste 3 metas concretas e mensuráveis para esta semana)

        ### Dica motivacional
        (Uma mensagem de incentivo personalizada para o aluno)

        Escreva tudo em **Português do Brasil**. Seja realista com o tempo disponível e encorajador.
        """
    )

    chain = prompt | llm
    return chain.invoke({
        "plano": plano,
        "semana_atual": semana_atual,
        "horas_por_dia": horas_por_dia,
        "dificuldades": dificuldades,
    }).content


# ─────────────────────────────────────────────
# FERRAMENTA 5 — Quiz Rápido de Verificação
# ─────────────────────────────────────────────

def gerar_quiz(semana: int, num_questoes: int = 5) -> str:
    """
    Gera um quiz de múltipla escolha para verificar o aprendizado
    da semana informada, com gabarito ao final.
    """
    plano = _load_plano()
    conteudo_semana = _semana_conteudo(plano, semana)
    llm = _get_llm(temperature=0.5)

    prompt = PromptTemplate.from_template(
        """
        Você é um professor criando um quiz de verificação de aprendizado.

        Conteúdo da Semana {semana}:
        {conteudo}

        Crie um quiz com **{num_questoes} questões de múltipla escolha** sobre o conteúdo desta semana.

        Formato de cada questão:
        **Questão X:** [enunciado da questão]
        a) [opção A]
        b) [opção B]
        c) [opção C]
        d) [opção D]

        Após todas as questões, adicione:

        ---
        ## 🔑 Gabarito
        1. [letra correta] — [breve explicação]
        2. [letra correta] — [breve explicação]
        ... e assim por diante

        Regras:
        - As questões devem cobrir diferentes aspectos do conteúdo da semana.
        - Inclua questões conceituais e de interpretação de código Python.
        - Apenas uma opção deve ser correta por questão.
        - Tudo em **Português do Brasil**.
        - Seja claro e objetivo nos enunciados.
        """
    )

    chain = prompt | llm
    return chain.invoke({
        "semana": semana,
        "conteudo": conteudo_semana,
        "num_questoes": num_questoes,
    }).content


# ─────────────────────────────────────────────
# FERRAMENTA 6 — Chat Livre com o Agente
# ─────────────────────────────────────────────

def chat_com_agente(pergunta: str, historico: list = None) -> str:
    """
    Responde perguntas livres do aluno sobre programação Python,
    mantendo contexto do histórico da conversa.
    """
    plano = _load_plano()
    llm = _get_llm(temperature=0.5)

    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    system_msg = SystemMessage(content=f"""
        Você é o **Prof. Py**, um assistente educacional especialista em Python para iniciantes.
        Você apoia alunos de Ciência de Dados e Banco de Dados em seus primeiros semestres.
        
        Plano de ensino da disciplina (para contexto):
        {plano}
        
        Diretrizes:
        - Responda sempre em **Português do Brasil**.
        - Seja didático, paciente e encorajador.
        - Use exemplos de código quando relevante (blocos ```python```).
        - Se a pergunta for sobre um tópico fora do plano de ensino, responda assim mesmo, mas mencione se é conteúdo avançado.
        - Se não souber a resposta, diga honestamente e sugira onde o aluno pode buscar ajuda.
        - Recomende o monitor quando a dúvida for complexa ou precisar de acompanhamento presencial.
    """)

    messages = [system_msg]

    if historico:
        for msg in historico:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=pergunta))

    response = llm.invoke(messages)
    return response.content


