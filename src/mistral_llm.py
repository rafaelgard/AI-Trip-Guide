import os
import torch
import json
import streamlit as st
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import StorageContext, load_index_from_storage
from transformers import BitsAndBytesConfig
from transformers import pipeline

class llm_traveller():
    def __init__(self, habilitar_correcao_gramatical, habilitar_geracao_de_metadados):
        self.habilitar_correcao_gramatical = habilitar_correcao_gramatical
        self.habilitar_geracao_de_metadados = habilitar_geracao_de_metadados
        self.load_configs()

    def load_configs(self):
        self.llm_metadados = self.carregar_llm_para_metadados()
        self.llm_resumo = self.carregar_llm_resumo()
 
        embeddings = HuggingFaceEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            embed_batch_size=32,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

        Settings.embed_model = embeddings
        

    def dividir_texto_em_blocos(self, texto, max_chars):
        """Divide o texto em blocos menores, respeitando o limite de caracteres."""
        blocos = []
        while len(texto) > max_chars:
            corte = texto[:max_chars].rfind(".")
            if corte == -1 or corte < 100:  # Se não houver ponto final útil
                corte = max_chars

            bloco = texto[:corte].strip()
            if not bloco:
                break  # Proteção contra loop infinito

            blocos.append(bloco)
            texto = texto[corte:].strip()

            if not texto or len(texto) == 0:
                break  # Proteção extra

        if texto:
            blocos.append(texto.strip())

        return blocos
    
    def checa_se_o_indice_existe(self):
        ''' Verifica se o índice já existe no diretório especificado '''
        caminho = 'D:/Projetos/Resumo Inteligente de Vídeos de Viagem com LLMs Open-Source/src/vectordatabase/docstore.json'
        return os.path.exists(caminho)

    def ler_metadados_json(self, caminho):

        try:
            with open(caminho, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # print("JSON carregado com sucesso:")
            # print(data)

            # Como é um único dicionário, acessamos o campo 'duration' diretamente
            duracao_segundos = data.get('duration', 0)
            duracao_minutos = duracao_segundos / 60

            return duracao_minutos

            # print(f"Duração do vídeo: {duracao_minutos:.2f} minutos")

        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho}' não encontrado.")
            return 0
        
        except json.JSONDecodeError:
            print("Erro: Não foi possível decodificar o JSON. Verifique o formato do arquivo.")
            return 0 


    def ler_arquivos_txt(self,pasta_raiz):
        '''Lê todos os arquivos .txt dentro das subpastas de uma pasta e retorna uma lista de textos'''

        data = {'textos': [],'nomes_arquivos': [], 'duracao_minutos': []}


        for nome_subpasta in os.listdir(pasta_raiz):
            caminho_subpasta = os.path.join(pasta_raiz, nome_subpasta)

            # Verifica se é uma pasta
            if os.path.isdir(caminho_subpasta):
                for nome_arquivo in os.listdir(caminho_subpasta):
                    if nome_arquivo.endswith(".txt"):
                        caminho_arquivo = os.path.join(caminho_subpasta, nome_arquivo)
                        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                            data['textos'].append(arquivo.read())
                            data['nomes_arquivos'].append(nome_arquivo)

                    if nome_arquivo.endswith(".json"):
                        caminho_arquivo = os.path.join(caminho_subpasta, nome_arquivo)
                        duracao_minutos = self.ler_metadados_json(caminho_arquivo)
                        data['duracao_minutos'].append(duracao_minutos)
              
        return data
    
    def gerar_resumo(self, prompt: str) -> str:
        """Gera um resumo baseado em um tema específico usando o modelo LLM."""
        # Carrega a LLM apenas para resumos
        response = self.llm_resumo.complete(prompt)
        return response.text.strip()
    
    # Função de resumo independente, sem afetar o carregamento do índice
    def carregar_llm_resumo(self):
        """Carrega o modelo LLM Mistral para geração de resumos."""
        modelo = "mistralai/Mistral-7B-Instruct-v0.2"
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        system_prompt = """
        Você é um assistente especializado em planejamento de viagens, com foco em viagens ao Chile. 
        Sua tarefa é analisar o conteúdo de vídeos transcritos por viajantes reais e fornecer respostas úteis, práticas e bem estruturadas.
        Antes de responder, pense passo a passo. Extraia informações relevantes dos vídeos, organize o raciocínio e só então gere a resposta.
        Considere que os dados vêm de diferentes criadores de conteúdo e que o usuário busca um resumo confiável com base em múltiplas experiências.
        Evite responder com base em conhecimento genérico. Sempre baseie suas respostas nos vídeos analisados.
        Se não houver informações suficientes nos vídeos, diga claramente: "Os vídeos analisados não trazem informações suficientes sobre isso.". Responda sempre em **português**
        """
        
        return HuggingFaceLLM(
            model_name=modelo,
            tokenizer_name=modelo,
            query_wrapper_prompt="Responda em português: {query_str}",
            context_window=3900,
            max_new_tokens=512,
            system_prompt=system_prompt,
            device_map="cuda" if torch.cuda.is_available() else "cpu",
            tokenizer_kwargs={"use_fast": True},
            model_kwargs={
                "torch_dtype": torch.float16,
                "quantization_config": quant_config,
                "repetition_penalty": 1.1
            }
        )

    def carregar_llm_para_metadados(self):
        """Carrega o modelo para gerar metadados (tema principal) usando zero-shot classification."""
        return pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

    def carregar_llm_para_llamaindex(self):
        """Carrega o modelo LLM Mistral para uso com LlamaIndex."""

        modelo = "mistralai/Mistral-7B-Instruct-v0.2"
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            )
        
        system_prompt = """
        Você é um assistente especializado em planejamento de viagens, com foco em viagens ao Chile. 
        Sua tarefa é analisar o conteúdo de vídeos transcritos por viajantes reais e fornecer respostas úteis, práticas e bem estruturadas.
        Antes de responder, pense passo a passo. Extraia informações relevantes dos vídeos, organize o raciocínio e só então gere a resposta.
        Considere que os dados vêm de diferentes criadores de conteúdo e que o usuário busca um resumo confiável com base em múltiplas experiências.
        Evite responder com base em conhecimento genérico. Sempre baseie suas respostas nos vídeos analisados.
        Se não houver informações suficientes nos vídeos, diga claramente: \"Os vídeos analisados não trazem informações suficientes sobre isso.\". Responda sempre em **português**
        """
        return HuggingFaceLLM(
            model_name=modelo,
            tokenizer_name=modelo,
            query_wrapper_prompt="Responda em português: {query_str}",
            context_window=3900,
            max_new_tokens=512,
            system_prompt=system_prompt,
            device_map="cuda" if torch.cuda.is_available() else "cpu",
            tokenizer_kwargs={"use_fast": True},
            model_kwargs={
                "torch_dtype": torch.float16,
                "quantization_config": quant_config,
                "repetition_penalty": 1.1
            }
        )

    def corrigir_transcricao(self, texto):
        """Corrige a transcrição automática de um vídeo, melhorando frases cortadas e erros de reconhecimento de fala."""
            
        print(f"Corrigindo texto...")

        prompt = f"""
        Corrija a transcrição automática de um vídeo sobre turismo no Chile. Melhore frases cortadas, nomes de lugares e erros de reconhecimento de fala. Use português natural e claro.

        Texto original:
        {texto}
        """
        try:
            resposta = self.llm_respostas.complete(prompt).text.strip()
        except Exception as e:
            print(f"Erro ao corrigir bloco {texto}: {e}")
            return texto

        return resposta

    def gerar_metadados(self, texto):
        """Gera metadados (tema principal) a partir do texto usando o modelo de metadados."""

        labels = [
            "gastronomia", "transporte", "hospedagem",
            "passeios", "clima", "dinheiro", "segurança", "outros"
        ]

        resultado = self.llm_metadados(texto, candidate_labels=labels)
        tema = resultado["labels"][0]  # o mais provável

        return {"tema": tema.lower()}

    def pre_processa_textos(self, data):
        """Pré-processa os textos, corrigindo e gerando metadados."""

        textos = data['textos']
        nomes_arquivos = data['nomes_arquivos'] 
        duracao_minutos = data['duracao_minutos'] 

        documents = []
        for i, texto in enumerate(textos):

            blocos = self.dividir_texto_em_blocos(texto, max_chars=1024)

            for j, bloco_de_texto in enumerate(blocos):
 
                if len(bloco_de_texto.strip()) < 20:                   
                    continue  # ignora blocos irrelevantes

                if self.habilitar_correcao_gramatical:
                    print(f"Corrigindo bloco de texto {i + 1}, parte {j + 1}...")            
                    bloco_de_texto_corrigido = self.corrigir_transcricao(bloco_de_texto)
                    print(f"len bloco_de_texto {len(bloco_de_texto)}")
                else:
                    bloco_de_texto_corrigido = bloco_de_texto
                
                if self.habilitar_geracao_de_metadados:
                    metadados = self.gerar_metadados(bloco_de_texto_corrigido)
                    print(f"metadados do texto {i+1} bloco {j + 1}: {metadados}")

                else:
                    metadados = {"tema": "desconhecido"}
    
                tema = metadados.get("tema", "desconhecido")
                print(f"tema {tema}...")

                # Calcula a duração em minutos do bloco de texto proporcionalmente a quantidade de caracteres 
                # do bloco em relação ao texto original
                duracao_minutos_bloco_texto = duracao_minutos[i] * (len(bloco_de_texto.strip())/len(texto))

                doc = Document(
                    text=bloco_de_texto_corrigido,
                    metadata={
                        "tema": tema,
                        "fonte": nomes_arquivos[i],
                        "duracao_minutos": duracao_minutos_bloco_texto
                    }
                )

                documents.append(doc)
        
        return documents

    def criar_indice(self, data):
        """Cria um índice a partir dos textos corrigidos e salva no diretório especificado."""
        
        if self.habilitar_correcao_gramatical:
            self.llm_respostas = self.carregar_llm_para_llamaindex() 

        documents = self.pre_processa_textos(data)
        index = VectorStoreIndex.from_documents(documents)
        persist_dir = "src/vectordatabase"
        index.storage_context.persist(persist_dir=persist_dir)
        print("Índice criado e salvo com sucesso!")

    def identificar_tema_da_pergunta(self, pergunta: str) -> str:
        """Identifica o tema da pergunta usando o modelo de metadados."""
        
        labels = [
            "gastronomia", "transporte", "hospedagem",
            "passeios", "clima", "dinheiro", "segurança", "outros"
        ]

        try:
            resultado = self.llm_metadados(pergunta, candidate_labels=labels)
            tema = resultado["labels"][0]  # o mais provável
            return tema.lower()
        except Exception as e:
            print(f"Erro ao identificar tema da pergunta: {e}")
            return "outros"

    def criar_query_fn_a_partir_do_indice(self, _index):
        """Cria uma função de consulta a partir de um índice carregado."""
        
        def query_fn(prompt):
            tema = self.identificar_tema_da_pergunta(prompt)
            print(f"Tema identificado da pergunta: {tema}")

            retriever = _index.as_retriever(filters={"tema": tema})
            query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                response_mode="compact",
                text_qa_template=None,
                refine_template=None,
                node_postprocessors=[],
            )

            prompt_final = f"""
            Responda sempre em português.
            Analise cuidadosamente os relatos dos vídeos sobre o tema "{tema}" antes de responder.
            Pergunta: {prompt}
            """
            return query_engine.query(prompt_final)

        return query_fn

    def carregar_ou_criar_indice(self):
        """Carrega o índice existente ou cria um novo se não existir."""
        
        if self.checa_se_o_indice_existe():

            self.llm_respostas = self.carregar_llm_para_llamaindex() 

            persist_dir = "src/vectordatabase"

            # Cria o storage context apontando para o diretório persistido
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)

            # Carrega o índice salvo
            index = load_index_from_storage(storage_context)

            # Configura o mecanismo de consulta
            retriever = index.as_retriever()
            query_engine = RetrieverQueryEngine.from_args(
                llm=self.llm_respostas,
                retriever=retriever,
                response_mode="compact",
                text_qa_template=None,
                refine_template=None,
                node_postprocessors=[],
            )

            def custom_query(prompt):
                prompt_cot = f"""
                Pense passo a passo. Analise cuidadosamente os relatos dos vídeos antes de responder.
                Pergunta: {prompt}
                """
                return query_engine.query(f"Responda sempre em **português**: {prompt_cot}")
            
            return custom_query, index

        else:
            # textos, nomes_arquivos = self.ler_arquivos_txt("src/transcriptions")
            data = self.ler_arquivos_txt("src/transcriptions")

            if data['textos']:
                with st.spinner("Construindo índice a partir dos vídeos..."):
                    self.criar_indice(data)
                    custom_query, index = self.carregar_ou_criar_indice()
           
                st.success("Índice criado com sucesso!")
                return custom_query, index
            else:
                st.warning("Não há arquivos de legenda na pasta 'input'.")
            