# app.py — Interface Streamlit do Agente Educacional Expandido

import os
import sys
import streamlit as st
from datetime import datetime

# Garante que o diretório do agente está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import AgenteEducacional
from modo_agente import executar_agente

# ─────────────────────────────────────────────
# Configuração da página
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Prof. Py — Agente Educacional",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Inicialização do estado da sessão
# ─────────────────────────────────────────────

if "semana_selecionada" not in st.session_state:
    st.session_state.semana_selecionada = 1
if "semanas_concluidas" not in st.session_state:
    st.session_state.semanas_concluidas = []
if "agente_historico" not in st.session_state:
    st.session_state.agente_historico = []  # histórico próprio do Modo agente

# ─────────────────────────────────────────────
# CSS customizado
# ─────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #e94560;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 800;
    }
    .main-header p {
        color: #a8b2d8;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    .sidebar-info {
        background: #1e2a3a;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: #a8b2d8;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar — Configurações
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    st.markdown("### 📅 Semana Atual")
    
    # Seletor de semana
    semana_global = st.selectbox(
        "Selecione sua semana:",
        options=list(range(1, 17)),
        index=st.session_state.semana_selecionada - 1,
        key="semana_global_select"
    )

    # Lógica de progresso automático
    if semana_global != st.session_state.semana_selecionada:
        st.session_state.semana_selecionada = semana_global
        # Marca todas as semanas anteriores como concluídas
        st.session_state.semanas_concluidas = list(range(1, semana_global))
        st.rerun()

    st.markdown("---")

    st.markdown("### 📊 Meu Progresso")
    
    # Multiselect manual
    semanas_concluidas = st.multiselect(
        "Semanas concluídas:",
        options=list(range(1, 17)),
        default=st.session_state.semanas_concluidas,
        key=f"manual_progress_{st.session_state.semana_selecionada}" # Chave dinâmica para forçar atualização
    )
    
    # Sincroniza se o usuário mudar manualmente
    if semanas_concluidas != st.session_state.semanas_concluidas:
        st.session_state.semanas_concluidas = semanas_concluidas
        st.rerun()

    progresso_pct = len(st.session_state.semanas_concluidas) / 16 * 100
    st.progress(int(progresso_pct), text=f"Progresso: {progresso_pct:.0f}%")

    st.markdown("---")
    st.markdown("""
    <div class="sidebar-info">
    <strong>🤖 Capacidades do Agente:</strong><br><br>
    📝 Geração de exercícios<br>
    📚 Resumo de conteúdo<br>
    ✅ Correção de exercícios<br>
    🧩 Quiz de verificação<br>
    📅 Plano de estudos<br>
    🤖 Modo agente<br>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Conteúdo Principal
# ─────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def carregar_agente():
    return AgenteEducacional()

st.markdown("""
<div class="main-header">
    <h1>🎓 Prof. Py</h1>
    <p>Agente Educacional Inteligente para Programação em Python</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📝 Exercícios", "📚 Resumo", "✅ Correção", "🧩 Quiz", "📅 Plano", "🤖 Modo agente",
])

semana_atual = st.session_state.semana_selecionada

# ABA 0: Exercícios
with tabs[0]:
    st.markdown(f"## 📝 Exercícios — Semana {semana_atual}")
    if st.button("🧠 Gerar Exercícios", type="primary", key="btn_ex"):
        with st.spinner("Gerando..."):
            st.markdown(carregar_agente().gerar_exercicios(semana_atual))

# ABA 1: Resumo
with tabs[1]:
    st.markdown(f"## 📚 Resumo — Semana {semana_atual}")
    if st.button("📖 Gerar Resumo", type="primary", key="btn_res"):
        with st.spinner("Gerando..."):
            st.markdown(carregar_agente().resumir_semana(semana_atual))

# ABA 2: Correção
with tabs[2]:
    st.markdown("## ✅ Correção de Exercícios")
    enunciado = st.text_area("Enunciado:", height=100, key="cor_enun")
    resposta = st.text_area("Sua Resposta:", height=150, key="cor_resp")
    if st.button("🔍 Corrigir", type="primary", key="btn_cor"):
        if enunciado and resposta:
            with st.spinner("Corrigindo..."):
                st.markdown(carregar_agente().corrigir_exercicio(semana_atual, enunciado, resposta))

# ABA 3: Quiz
with tabs[3]:
    st.markdown(f"## 🧩 Quiz — Semana {semana_atual}")
    if st.button("🎯 Gerar Quiz", type="primary", key="btn_quiz"):
        with st.spinner("Gerando..."):
            st.markdown(carregar_agente().gerar_quiz(semana_atual))

# ABA 4: Plano
with tabs[4]:
    st.markdown("## 📅 Plano de Estudos")
    horas = st.slider("Horas/dia:", 1, 8, 2, key="plano_horas")
    difs = st.text_area("Dificuldades:", placeholder="O que está difícil?", key="plano_difs")
    if st.button("📅 Gerar Plano", type="primary", key="btn_plano"):
        with st.spinner("Gerando..."):
            st.markdown(carregar_agente().gerar_plano_estudos(semana_atual, horas, difs or "Nenhuma"))

# ABA 5: Modo agente
# Diferente das abas anteriores (onde o CÓDIGO decide qual função chamar, um workflow),
# aqui quem decide é o LLM: ele lê a mensagem e escolhe as ferramentas (ver modo_agente.py).
def mostrar_passos(passos):
    """Mostra cada ferramenta que o agente decidiu chamar, com os argumentos usados."""
    for passo in passos:
        argumentos = ", ".join(f"{k}={v!r}" for k, v in passo["argumentos"].items())
        with st.expander(f"🔧 {passo['ferramenta']}({argumentos})"):
            st.markdown("**Resultado da ferramenta:**")
            st.markdown(passo["resultado"])


with tabs[5]:
    st.markdown("## 🤖 Modo agente")
    st.caption("Escreva livremente. O modelo escolhe sozinho quais ferramentas usar. "
               "Ex.: *me dá exercícios da semana 3 e depois corrige a minha resposta*")

    for msg in st.session_state.agente_historico:
        with st.chat_message(msg["role"]):
            mostrar_passos(msg.get("passos", []))
            st.markdown(msg["content"])

    if prompt_agente := st.chat_input("Peça o que quiser ao agente...", key="chat_agente"):
        with st.chat_message("user"):
            st.markdown(prompt_agente)
        with st.chat_message("assistant"):
            with st.spinner("O agente está decidindo..."):
                resposta, passos = executar_agente(
                    carregar_agente(), prompt_agente, st.session_state.agente_historico
                )
            mostrar_passos(passos)
            st.markdown(resposta)
        st.session_state.agente_historico.append({"role": "user", "content": prompt_agente})
        st.session_state.agente_historico.append({"role": "assistant", "content": resposta, "passos": passos})


st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #666;'>Prof. Py v2.0 | {datetime.today().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)