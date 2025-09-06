import os
import streamlit as st
from src.utils import exportar_historico_para_pdf
from src.llm import llm_traveller
from src.themes import THEMATIC_QUESTIONS
from src.cache.respostas_cache import obter_ou_gerar_resposta, preencher_cache_com_exemplos
from src.youtube import verifica_base_transcricoes
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="AI Trip Guide", layout="centered")

def home():

    st.title("📍 AI Trip Guide")
    st.markdown("Explore o conteúdo de dezenas de vídeos sobre o **Chile** e faça perguntas com base nas experiências de vários viajantes.")

    # Inicializa estados
    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    if "pergunta_preenchida" not in st.session_state:
        st.session_state["pergunta_preenchida"] = ""

    if "tema_selecionado" not in st.session_state:
        st.session_state["tema_selecionado"] = ""

    # Carrega índice e função de consulta
    if "classe" not in st.session_state:
        st.session_state["classe"] = llm_traveller(habilitar_correcao_gramatical=False, habilitar_geracao_de_metadados=True)

    if "index" not in st.session_state:
        st.session_state["query_fn"], st.session_state["index"] = st.session_state["classe"].carregar_ou_criar_indice()

    if "index" in st.session_state:
        if "query_fn" not in st.session_state:
            st.session_state["query_fn"] = st.session_state["classe"].criar_query_fn_a_partir_do_indice(st.session_state["index"])

        # Seção de temas
        st.subheader("💡 Escolha um tema para perguntas sugeridas")
        temas = list(THEMATIC_QUESTIONS.keys())
        cols = st.columns(len(temas))

        for i, tema in enumerate(temas):
            if cols[i].button(tema):
                st.session_state["tema_selecionado"] = tema

        # Perguntas sugeridas por tema
        if st.session_state["tema_selecionado"]:
            st.markdown("#### Perguntas sugeridas para o tema selecionado:")
            for pergunta in THEMATIC_QUESTIONS[st.session_state["tema_selecionado"]]:
                if st.button(pergunta, use_container_width=True):
                    st.session_state["pergunta_preenchida"] = pergunta
        else:
            st.markdown("#### Exemplos gerais de perguntas:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📌 O que os viajantes recomendam em Santiago?"):
                    st.session_state["pergunta_preenchida"] = "O que os viajantes recomendam em Santiago?"
                if st.button("🚍 Há dicas sobre transporte entre cidades?"):
                    st.session_state["pergunta_preenchida"] = "Há dicas sobre transporte entre cidades?"
            with col2:
                if st.button("🏔️ Quais lugares aparecem com mais frequência?"):
                    st.session_state["pergunta_preenchida"] = "Quais lugares aparecem com mais frequência?"
                if st.button("🎎 Quais são os costumes locais mencionados?"):
                    st.session_state["pergunta_preenchida"] = "Quais são os costumes locais mencionados?"

        # Campo de pergunta
        st.subheader("🔎 Faça sua pergunta")
        pergunta_usuario = st.text_input(
            "Digite ou escolha uma pergunta:",
            value=st.session_state["pergunta_preenchida"],
            key="input_pergunta"
        )
        
        # # Verifica se a base de transcrições está pronta
        with st.spinner("Verificando o tamanho da base de transcrições existente...", show_time=True):
            verifica_base_transcricoes()

        # # Preencher cache com perguntas sugeridas
        with st.spinner("Verificando o cache...", show_time=True):
            preencher_cache_com_exemplos(st.session_state["query_fn"])
        
        # Enviar pergunta
        if st.button("Enviar"):
            if pergunta_usuario.strip() != "":
                with st.spinner("Consultando os vídeos...", show_time=True):
                    # resposta = st.session_state["query_fn"](pergunta_usuario)
                    resposta = obter_ou_gerar_resposta(pergunta_usuario, st.session_state["query_fn"])

                st.session_state["historico"].append(("Você", pergunta_usuario))
                st.session_state["historico"].append(("LLM", str(resposta)))
                st.session_state["pergunta_preenchida"] = ""
            else:
                st.warning("Digite uma pergunta antes de enviar.")

        # Exibir histórico
        if st.session_state["historico"]:
            st.subheader("💬 Histórico da Conversa")
            for remetente, mensagem in reversed(st.session_state["historico"]):
                if remetente == "Você":
                    st.markdown(f"**🧍 {remetente}:** {mensagem}")
                else:
                    st.markdown(f"**🤖 {remetente}:** {mensagem}")

            if os.getenv("MODO") == "local":
                # Exportação PDF
                if st.button("📄 Exportar conversa como PDF"):
                    caminho_pdf = exportar_historico_para_pdf(st.session_state["historico"])
                    st.success("PDF exportado com sucesso!")
                    with open(caminho_pdf, "rb") as f:
                        st.download_button(
                            label="📥 Baixar PDF",
                            data=f,
                            file_name="resumo_viagem_completo.pdf",
                            mime="application/pdf"
                        )
