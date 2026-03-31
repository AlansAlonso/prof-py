# agent.py — Agente educacional expandido com múltiplas ferramentas

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool, StructuredTool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import Optional, List

from tools import (
    gerar_exercicios,
    resumir_semana,
    corrigir_exercicio,
    gerar_plano_estudos,
    gerar_quiz,
    chat_com_agente,
    _load_plano,
)

load_dotenv()


# ─────────────────────────────────────────────
# Schemas para ferramentas com múltiplos inputs
# ─────────────────────────────────────────────

class CorrigirExercicioInput(BaseModel):
    semana: int = Field(description="Número da semana do curso (1-16)")
    enunciado: str = Field(description="Enunciado completo do exercício que o aluno respondeu")
    resposta_aluno: str = Field(description="Resposta ou código enviado pelo aluno")


class PlanoEstudosInput(BaseModel):
    semana_atual: int = Field(description="Semana atual do aluno no curso (1-16)")
    horas_por_dia: int = Field(description="Quantidade de horas disponíveis por dia para estudar")
    dificuldades: str = Field(description="Descrição das principais dificuldades ou tópicos que o aluno não entendeu bem")




# ─────────────────────────────────────────────
# Classe principal do Agente Educacional
# ─────────────────────────────────────────────

class AgenteEducacional:
    """
    Agente educacional completo para suporte a alunos de programação Python.
    Possui ferramentas para geração de exercícios, resumos, correção,
    quiz, plano de estudos, chat livre e análise de progresso.
    """

    def __init__(self):

        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1-mini",
            temperature=0.3,
        )

        self.system_prompt = SystemMessage(
            content="""
Você é um tutor educacional especializado em ensinar Python para iniciantes.

Seu objetivo é ajudar estudantes a aprender programação de forma clara,
progressiva e encorajadora.

Sempre:
- explique conceitos de forma didática
- use exemplos simples em Python
- incentive a prática
- destaque erros comuns de iniciantes
- adapte sua linguagem para alunos iniciantes

Use ferramentas apenas quando necessário para gerar exercícios,
corrigir respostas ou analisar progresso do aluno.
"""
        )

        self.plano = _load_plano()
        self.tools = self._build_tools()

    def _build_tools(self):
        """Constrói a lista de ferramentas disponíveis para o agente."""

        return [

            Tool(
                name="gerar_exercicios",
                func=lambda semana: gerar_exercicios(int(semana)),
                description=(
                    "Gera exercícios para prática do conteúdo de uma semana específica do curso de Python.\n\n"
                    "A saída deve conter exatamente 5 exercícios organizados da seguinte forma:\n"
                    "- 2 exercícios conceituais (interpretação ou explicação)\n"
                    "- 2 exercícios práticos (pequenos programas em Python)\n"
                    "- 1 exercício desafio que combine múltiplos conceitos.\n\n"
                    "Use esta ferramenta quando o aluno pedir exercícios, tarefas, prática ou desafios "
                    "sobre o conteúdo de uma semana específica.\n\n"
                    "Entrada: número da semana (1-16)."
                ),
            ),

            Tool(
                name="resumir_semana",
                func=lambda semana: resumir_semana(int(semana)),
                description=(
                    "Gera um resumo didático do conteúdo de uma semana do curso de Python.\n\n"
                    "O resumo deve:\n"
                    "- explicar os conceitos principais\n"
                    "- incluir pequenos exemplos de código Python\n"
                    "- destacar erros comuns de iniciantes\n"
                    "- sugerir maneiras de praticar o conteúdo.\n\n"
                    "Use esta ferramenta quando o aluno pedir explicação, revisão ou resumo "
                    "de uma semana específica do curso.\n\n"
                    "Entrada: número da semana (1-16)."
                ),
            ),

            StructuredTool.from_function(
                func=corrigir_exercicio,
                name="corrigir_exercicio",
                description=(
                    "Corrige a resposta de um aluno para um exercício de programação.\n\n"
                    "A correção deve incluir:\n"
                    "- avaliação da lógica da solução\n"
                    "- identificação de erros conceituais ou de sintaxe\n"
                    "- sugestões claras de melhoria\n"
                    "- uma nota ou avaliação qualitativa do desempenho.\n\n"
                    "Use esta ferramenta quando o aluno pedir correção de código, "
                    "feedback de exercício ou avaliação de resposta."
                ),
                args_schema=CorrigirExercicioInput,
            ),

            StructuredTool.from_function(
                func=gerar_plano_estudos,
                name="gerar_plano_estudos",
                description=(
                    "Cria um plano de estudos personalizado para um aluno de Python.\n\n"
                    "O plano não deve recomendar cursos e ferramentas externas.\n\n"
                    "O plano deve considerar:\n"
                    "- semana atual do curso\n"
                    "- horas disponíveis por dia\n"
                    "- dificuldades relatadas pelo aluno.\n\n"
                    "A resposta deve organizar o plano em etapas ou dias de estudo "
                    "e incluir sugestões práticas de exercícios.\n\n"
                    "Use esta ferramenta quando o aluno pedir ajuda para organizar "
                    "seus estudos ou montar um cronograma de aprendizado."
                ),
                args_schema=PlanoEstudosInput,
            ),

            Tool(
                name="gerar_quiz",
                func=lambda semana: gerar_quiz(int(semana)),
                description=(
                    "Gera um quiz para revisão do conteúdo de uma semana do curso de Python.\n\n"
                    "O quiz deve conter:\n"
                    "- 5 questões de múltipla escolha\n"
                    "- 4 alternativas por questão\n"
                    "- indicação da resposta correta ao final.\n\n"
                    "Use esta ferramenta quando o aluno quiser testar conhecimento, "
                    "fazer revisão ou praticar com perguntas sobre uma semana específica do curso.\n\n"
                    "Entrada: número da semana (1-16)."
                ),
            ),

        ]


    # ── Métodos diretos (sem ReAct loop) para uso na UI ──

    def gerar_exercicios(self, semana: int) -> str:
        return gerar_exercicios(semana)

    def resumir_semana(self, semana: int) -> str:
        return resumir_semana(semana)

    def corrigir_exercicio(self, semana: int, enunciado: str, resposta_aluno: str) -> str:
        return corrigir_exercicio(semana, enunciado, resposta_aluno)

    def gerar_plano_estudos(self, semana_atual: int, horas_por_dia: int, dificuldades: str) -> str:
        return gerar_plano_estudos(semana_atual, horas_por_dia, dificuldades)

    def gerar_quiz(self, semana: int) -> str:
        return gerar_quiz(semana)

    def chat(self, pergunta: str, historico: list = None) -> str:
        return chat_com_agente(pergunta, historico)

    def analisar_progresso(self, semanas_concluidas: list, dificuldades_por_semana: dict) -> str:
        return analisar_progresso(semanas_concluidas, dificuldades_por_semana)