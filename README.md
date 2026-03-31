# 🎓 Prof. Py — Agente Educacional Inteligente

> Evolução do **PG-LLM-Agent** original para um agente educacional completo com múltiplas ferramentas, interface moderna e suporte abrangente ao aluno de programação Python.

---

## 📋 Visão Geral

O **Prof. Py** é um agente educacional baseado em LLM (GPT-4.1-mini) construído com LangChain e Streamlit. Ele foi projetado para apoiar alunos dos primeiros semestres de **Ciência de Dados** e **Banco de Dados** no aprendizado de Python.

### O que mudou em relação ao projeto original?

| Capacidade | Original | Expandido |
|---|---|---|
| Geração de exercícios por semana | ✅ | ✅ (melhorado) |
| Resumo didático da semana | ❌ | ✅ |
| Correção de exercícios com nota | ❌ | ✅ |
| Quiz de múltipla escolha | ❌ | ✅ |
| Plano de estudos personalizado | ❌ | ✅ |
| Chat livre com o agente | ❌ | ✅ |
| Análise de progresso do aluno | ❌ | ✅ |
| Interface multi-abas moderna | ❌ | ✅ |
| Histórico de conversa no chat | ❌ | ✅ |
| Controle de progresso na sidebar | ❌ | ✅ |

---

## 🚀 Funcionalidades

### 1. 📝 Gerador de Exercícios
Gera 5 exercícios por semana: 2 teóricos, 2 práticos e 1 desafio, com base no plano de ensino.

### 2. 📚 Resumo Didático da Semana
Gera um resumo completo com:
- Explicação das subcompetências
- Exemplos de código Python comentados
- Dicas de estudo
- Conexão com semanas anteriores

### 3. ✅ Correção de Exercícios
Cole o enunciado e sua resposta para receber:
- Análise detalhada da resposta
- Nota de 0 a 10 com justificativa
- Lista de erros com explicações didáticas
- Solução sugerida comentada
- Pontos positivos e próximos passos

### 4. 🧩 Quiz de Verificação
Gera questões de múltipla escolha com gabarito oculto para autoavaliação.

### 5. 📅 Plano de Estudos Personalizado
Cria um plano semanal adaptado às horas disponíveis e dificuldades do aluno.

### 6. 💬 Chat com Prof. Py
Chat livre com histórico de conversa para tirar dúvidas sobre Python e programação.

### 7. 📊 Análise de Progresso
Relatório de evolução baseado nas semanas concluídas e dificuldades reportadas.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.11+
- Chave de API da OpenAI

### Passos

```bash
# 1. Clone ou extraia o projeto
cd PG-LLM-Agent-expanded

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure a chave da API
cp .env.example .env
# Edite o arquivo .env e adicione sua OPENAI_API_KEY

# 4. Execute a aplicação
cd src/agent
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

---

## 🏗️ Arquitetura

```
PG-LLM-Agent-expanded/
├── src/
│   └── agent/
│       ├── agent.py          # Classe principal do agente (AgenteEducacional)
│       ├── tools.py          # Ferramentas individuais do agente
│       ├── app.py            # Interface Streamlit multi-abas
│       └── plano_ensino.txt  # Plano de ensino da disciplina
├── requirements.txt
├── .env.example
└── README.md
```

### Fluxo de dados

```
Usuário (Streamlit UI)
        ↓
  AgenteEducacional (agent.py)
        ↓
  Ferramentas (tools.py)
        ↓
  LangChain PromptTemplate + ChatOpenAI (GPT-4.1-mini)
        ↓
  Resposta formatada em Markdown
```

---

## 📖 Plano de Ensino

O agente cobre as 9 semanas do plano de ensino original:

| Semana | Conteúdo Principal |
|---|---|
| 1 | Introdução à programação, Hello World |
| 2 | Variáveis e atribuição |
| 3 | Tipos de dados: int, float, boolean, strings |
| 4 | Strings: criação, concatenação, replicação, funções |
| 5 | Strings: operadores, funções, input() |
| 6 | Condicionais e operadores booleanos |
| 7 | Condicionais compostas e ramificações |
| 8 | Loops for e while, função range() |
| 9 | Listas: criação, concatenação, iteração |

---

## 🔧 Tecnologias

- **LangChain** — Orquestração do agente e ferramentas
- **OpenAI GPT-4.1-mini** — Modelo de linguagem
- **Streamlit** — Interface web interativa
- **Python-dotenv** — Gerenciamento de variáveis de ambiente
- **Pydantic** — Validação de schemas das ferramentas

---

## 👥 Créditos

Projeto expandido a partir do **PG-LLM-Agent** original, desenvolvido como projeto educacional para suporte a alunos de programação Python. O projeto foi expandido com auxílio da ferramenta Manus, e parte da razão por trás deste projeto foi entender melhor essa ferramenta e como melhor utilizá-la.
