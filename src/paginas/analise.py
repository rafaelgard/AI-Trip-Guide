import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
from llama_index.core import Settings
from src.mistral_llm import llm_traveller
from dotenv import load_dotenv
import os
load_dotenv()
modo = os.getenv("MODO")

if modo != 'cloud':
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

@st.cache_data(show_spinner="🔄 Carregando dados do índice...")
def carregar_blocos():
    # Define explicitamente o modelo local de embeddings
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    classe = llm_traveller(habilitar_correcao_gramatical=False, habilitar_geracao_de_metadados=True)
    _, index = classe.carregar_ou_criar_indice()
    
    # Retorna os documentos armazenados
    docs = list(index.docstore.docs.values())
    return docs


def analise():

    if modo != 'cloud':
        st.title("📊 Análise dos Blocos Transcritos")
        st.write("Esta análise foi gerada com base nos vídeos processados e classificados por tema.")

        documentos = carregar_blocos()
        total_blocos = len(documentos)

        if modo == 'cloud':
            # Contagem de temas
            temas = [doc.metadata.get("temas", "outros") for doc in documentos]

            lista_de_temas= []
            temas_unicos = []

            for x in temas:
                for y in x.split(','):
                    if y not in temas_unicos and y!='':
                        temas_unicos.append(y)
                    
                    elif  y!='':
                        lista_de_temas.append(y)


            contagem_temas = Counter(lista_de_temas)
            temas = temas_unicos

        else:
            # Contagem de temas
            temas = [doc.metadata.get("tema", "outros") for doc in documentos]
            contagem_temas = Counter(temas)


        # Duração total
        duracao_total_minutos = sum([doc.metadata.get("duracao_minutos", 0) for doc in documentos])
        duracao_total_horas = duracao_total_minutos / 60

        # Arredondamento
        duracao_total_minutos = round(duracao_total_minutos, 2)
        duracao_total_horas = round(duracao_total_horas, 2)

        # Número de vídeos únicos (pelo ID do vídeo)
        ids_unicos = set(doc.metadata.get("fonte", "desconhecido") for doc in documentos)
        total_videos = len(ids_unicos)

        col1, col2, col3, col4  = st.columns(4)
        col1.metric("🎞️ Vídeos Processados", total_videos)
        col2.metric("📄 Blocos Analisados", total_blocos)
        col3.metric("📄 Horas de Vídeos", duracao_total_horas)
        col4.metric("📄 Minutos de Vídeos", duracao_total_minutos)

        # Gráfico de barras
        st.subheader("Distribuição dos Temas")
        fig, ax = plt.subplots()
        ax.bar(contagem_temas.keys(), contagem_temas.values(), color="skyblue")
        ax.set_ylabel("Quantidade de Blocos")
        ax.set_xlabel("Temas")
        ax.set_title("Número de Blocos por Tema")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Exibe a lista completa de temas se quiser debug
        with st.expander("🔍 Ver temas detectados por bloco"):
            for i, doc in enumerate(documentos):
                st.markdown(f"**Bloco {i+1}** - Tema: `{doc.metadata.get('tema', 'outros')}`")
                st.caption(doc.text[:200] + "...")  # Mostra trecho inicial
    else:
        st.title("Página em construção...")