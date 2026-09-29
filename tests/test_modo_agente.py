# Testes do modo agente SEM chamar a API real: o LLM é substituído por um modelo falso
# que devolve respostas pré-definidas (incluindo pedidos de ferramenta).
#
# Rodar (na raiz do projeto):  python -m pytest tests -q

import os
import sys

os.environ.setdefault("OPENAI_API_KEY", "chave-falsa-para-testes")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "agent"))

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

import tools as tools_mod
import modo_agente
from agent import AgenteEducacional


class LLMFalso(GenericFakeChatModel):
    """LLM de mentira: devolve as mensagens da lista, em ordem, e aceita bind_tools."""

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, *args, **kwargs):
        LLMFalso.mensagens_recebidas = list(messages)  # para conferir o que o LLM viu
        return super()._generate(messages, *args, **kwargs)


def pedido(nome, args, id_="1"):
    return AIMessage(content="", tool_calls=[{"name": nome, "args": args, "id": id_}])


def montar_agente(monkeypatch, respostas_orquestrador, resposta_ferramentas="[texto da ferramenta]"):
    # As ferramentas de tools.py chamam _get_llm(): trocamos por um LLM falso
    monkeypatch.setattr(tools_mod, "_get_llm",
                        lambda temperature=0.3: LLMFalso(messages=iter([AIMessage(content=resposta_ferramentas)] * 20)))
    agente = AgenteEducacional()
    agente.llm = LLMFalso(messages=iter(respostas_orquestrador))
    return agente


def test_resposta_direta_sem_ferramenta(monkeypatch):
    agente = montar_agente(monkeypatch, [AIMessage(content="Oi! Como posso ajudar?")])
    resposta, passos = modo_agente.executar_agente(agente, "oi")
    assert resposta == "Oi! Como posso ajudar?"
    assert passos == []


def test_duas_ferramentas_em_sequencia(monkeypatch):
    # "me dá exercícios da semana 3 e depois corrige a minha resposta"
    agente = montar_agente(monkeypatch, [
        pedido("gerar_exercicios", {"tool_input": "3"}, "a"),
        pedido("corrigir_exercicio", {"semana": 3, "enunciado": "Concatene 'a' e 'b'",
                                      "resposta_aluno": "print('a' + 'b')"}, "b"),
        AIMessage(content="Pronto! Exercícios gerados e resposta corrigida."),
    ])
    resposta, passos = modo_agente.executar_agente(agente, "exercícios da semana 3 e corrija minha resposta")
    assert [p["ferramenta"] for p in passos] == ["gerar_exercicios", "corrigir_exercicio"]
    assert passos[0]["argumentos"] == {"tool_input": "3"}
    assert passos[1]["argumentos"]["semana"] == 3
    assert passos[0]["resultado"] == "[texto da ferramenta]"  # ferramenta real rodou (com LLM falso)
    assert resposta.startswith("Pronto")


def test_semana_inexistente_vira_erro_claro(monkeypatch):
    agente = montar_agente(monkeypatch, [
        pedido("gerar_quiz", {"tool_input": "20"}),
        AIMessage(content="A semana 20 não existe."),
    ])
    _, passos = modo_agente.executar_agente(agente, "quiz da semana 20")
    assert "não existe" in passos[0]["resultado"]
    assert "[texto da ferramenta]" not in passos[0]["resultado"]  # a ferramenta nem foi chamada


def test_ferramenta_inexistente_nao_quebra(monkeypatch):
    agente = montar_agente(monkeypatch, [pedido("analisar_progresso", {}), AIMessage(content="ok")])
    resposta, passos = modo_agente.executar_agente(agente, "analise meu progresso")
    assert "não existe" in passos[0]["resultado"]
    assert resposta == "ok"


def test_limite_de_voltas(monkeypatch):
    agente = montar_agente(monkeypatch, [pedido("gerar_quiz", {"tool_input": "1"}, str(i)) for i in range(20)])
    resposta, passos = modo_agente.executar_agente(agente, "quiz")
    assert len(passos) == modo_agente.MAX_VOLTAS
    assert "limite" in resposta


def test_historico_e_enviado_ao_llm(monkeypatch):
    agente = montar_agente(monkeypatch, [AIMessage(content="ok")])
    historico = [{"role": "user", "content": "meu nome é Ana"}, {"role": "assistant", "content": "Oi Ana"}]
    modo_agente.executar_agente(agente, "qual meu nome?", historico)
    vistas = LLMFalso.mensagens_recebidas
    assert vistas[0].content.strip().startswith("Você é um tutor")  # system prompt de agent.py
    assert [m.content for m in vistas][-3:] == ["meu nome é Ana", "Oi Ana", "qual meu nome?"]


def test_langfuse_desligado_sem_variaveis(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    assert modo_agente.criar_callbacks() == []


def test_langfuse_ligado_com_variaveis(monkeypatch):
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-falsa")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-falsa")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:9")  # nada é enviado no teste
    callbacks = modo_agente.criar_callbacks()
    assert len(callbacks) == 1


def test_langfuse_pacote_ausente_nao_quebra(monkeypatch):
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-falsa")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-falsa")
    monkeypatch.setitem(sys.modules, "langfuse.langchain", None)  # simula pacote não instalado
    assert modo_agente.criar_callbacks() == []
