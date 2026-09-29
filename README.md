# 🎓 Prof. Py — Agente Educacional para Python

O **Prof. Py** é um tutor de Python para alunos dos primeiros semestres de **Ciência de Dados** e **Banco de Dados**. Ele usa um modelo de linguagem da OpenAI (GPT-4.1-mini) com LangChain e uma interface em Streamlit, e trabalha em cima do plano de ensino da disciplina (16 semanas).

O app tem duas formas de uso, lado a lado:

- **Abas com botões (workflow):** você escolhe a semana, clica no botão e o programa chama sempre a mesma função.
- **Modo agente:** você escreve livremente e o próprio modelo decide quais ferramentas usar.

---

## 🚀 Como usar

Escolha sua **semana atual** na barra lateral. As cinco primeiras abas usam essa semana.

### 📝 Exercícios
Clique em **Gerar Exercícios** para receber 5 exercícios da semana: 2 teóricos, 2 práticos e 1 desafio.

### 📚 Resumo
Clique em **Gerar Resumo** para receber o conteúdo da semana explicado, com exemplos de código comentados, dicas de estudo e a conexão com semanas anteriores.

### ✅ Correção
Cole o **enunciado** e a **sua resposta**, e clique em **Corrigir**. Você recebe análise, nota de 0 a 10, erros explicados, solução sugerida e próximos passos.

### 🧩 Quiz
Clique em **Gerar Quiz** para receber 5 questões de múltipla escolha, com gabarito no final.

### 📅 Plano
Informe as **horas por dia** e suas **dificuldades**, e clique em **Gerar Plano**. Você recebe um plano de estudos dia a dia.

### 🤖 Modo agente
Um chat livre em que **você não escolhe a ferramenta: o modelo escolhe**.

1. Escreva o pedido na caixa de baixo, como falaria com uma pessoa.
2. Espere o "O agente está decidindo...".
3. Veja o resultado:
   - Cada **🔧 ferramenta(argumentos)** é uma ferramenta que o agente decidiu chamar. Clique nela para ver o resultado.
   - Abaixo aparece a resposta final.

Exemplos de pedidos:

| Você quer | Escreva |
|---|---|
| Exercícios | *me dá exercícios da semana 3* |
| Resumo | *resume a semana 5 pra mim* |
| Quiz | *faz um quiz da semana 7* |
| Correção | *corrija: enunciado: somar dois números. Resposta: `print(2+3)`. Semana 2* |
| Plano de estudos | *monta um plano: estou na semana 6, tenho 2 horas por dia e não entendo o for* |
| Vários pedidos | *exercícios da semana 3 e um quiz da semana 4* |
| Dúvida livre | *o que é uma variável?* (responde sem usar ferramenta) |

Dicas:
- **Diga a semana na mensagem.** O modo agente não usa a semana da barra lateral.
- **Na correção, envie tudo junto:** enunciado, resposta e semana.
- As semanas vão de **1 a 16**. Fora disso, o agente avisa que a semana não existe.
- A conversa tem memória enquanto a página estiver aberta. Recarregar a página apaga o histórico.

---

## 🛠️ Instalação e execução

### Pré-requisitos
- Python 3.11 ou superior
- Chave de API da OpenAI, com crédito na conta

### Passos

```bash
# 1. Entre na pasta do projeto
cd prof-py

# 2. Instale as dependências
python -m pip install -r requirements.txt

# 3. Configure a chave da API
cp .env.example .env        # no Windows (PowerShell): copy .env.example .env
# Edite o .env e coloque sua chave em OPENAI_API_KEY

# 4. Execute a aplicação
cd src/agent
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`. Se você mudar o `.env`, reinicie o Streamlit.

### Langfuse (opcional)
Para acompanhar os passos do modo agente no [Langfuse](https://langfuse.com), defina no `.env`:

```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

Sem essas variáveis, tudo funciona normalmente, só sem o envio de traces.

### Testes
Os testes não chamam a API real (usam um modelo falso):

```bash
python -m pip install pytest
python -m pytest tests -q
```

---

## 🏗️ Arquitetura

```
prof-py/
├── src/
│   └── agent/
│       ├── app.py            # Interface Streamlit (abas e modo agente)
│       ├── agent.py          # Classe AgenteEducacional: LLM, system prompt e ferramentas
│       ├── tools.py          # As ferramentas: cada uma é um prompt + chamada ao LLM
│       ├── modo_agente.py    # Loop do agente (o LLM escolhe as ferramentas)
│       └── plano_ensino.txt  # Plano de ensino da disciplina
├── tests/                    # Testes do modo agente
├── requirements.txt
├── .env.example
└── README.md
```

### Como os dois modos funcionam

```
Abas com botões (workflow)          Modo agente
──────────────────────────          ───────────
Aluno clica no botão                Aluno escreve uma mensagem
        ↓                                   ↓
O código chama a função             O LLM decide qual ferramenta chamar
        ↓                                   ↓
Ferramenta (prompt + LLM)           O código executa a ferramenta (prompt + LLM)
        ↓                                   ↓
Resposta em Markdown                O resultado volta ao LLM, que decide o
                                    próximo passo ou responde (máx. 5 voltas)
```

O loop do modo agente está em [`modo_agente.py`](src/agent/modo_agente.py), escrito à mão e comentado em português.

---

## 📖 Plano de ensino

O agente cobre as 16 semanas de `src/agent/plano_ensino.txt`:

| Semana | Conteúdo principal |
|---|---|
| 1 | Introdução à programação, Hello World, print() |
| 2 | Variáveis, tipos básicos e operadores matemáticos |
| 3 | Strings: aspas, concatenação, replicação e métodos |
| 4 | input(), conversão de tipos e validação de entradas |
| 5 | Condicionais (if/elif/else) e operadores booleanos |
| 6 | Loops for e while, função range() |
| 7 | Listas: criação, acesso, iteração, adicionar e remover |
| 8 | Dicionários: chaves, valores e iteração |
| 9 | Funções: parâmetros, retorno e valores padrão |
| 10 | Múltiplas funções, módulos, imports e docstrings |
| 11 | Leitura e escrita de arquivos de texto |
| 12 | JSON e conversão de/para dicionários |
| 13 | APIs e requisições HTTP com requests |
| 14 | Web Services, REST, endpoints e métodos HTTP |
| 15 | Servidor simples com FastAPI (GET e POST) |
| 16 | Web service completo (listar, inserir, atualizar, remover) |

---

## 🔧 Tecnologias

- **LangChain** — Prompts, ferramentas e mensagens
- **OpenAI GPT-4.1-mini** — Modelo de linguagem
- **Streamlit** — Interface web
- **Python-dotenv** — Variáveis de ambiente
- **Pydantic** — Schemas das ferramentas
- **Langfuse** (opcional) — Observabilidade do modo agente

---

## 👥 Créditos

Projeto educacional para apoio a alunos de programação Python, expandido a partir do **PG-LLM-Agent** original. Parte da expansão foi feita com a ferramenta Manus, também como forma de entender melhor essa ferramenta e como usá-la.
