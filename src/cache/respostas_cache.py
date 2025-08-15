import os
import json
from src.themes import THEMATIC_QUESTIONS
from dotenv import load_dotenv
load_dotenv()

# Caminho do arquivo de cache (focado no Chile)
CAMINHO_CACHE = "src/cache/respostas_chile.json"

# Cria o arquivo se não existir
def inicializar_cache():
    if not os.path.exists(CAMINHO_CACHE):
        with open(CAMINHO_CACHE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

# Carrega o cache do disco
def carregar_cache():
    inicializar_cache()
    with open(CAMINHO_CACHE, "r", encoding="utf-8") as f:
        return json.load(f)

# Salva o cache no disco
def salvar_cache(cache):
    with open(CAMINHO_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# Função principal que verifica o cache ou gera a resposta
def obter_ou_gerar_resposta(pergunta, query_fn):

    CACHE_ATIVADO = os.getenv("CACHE_ATIVADO")

    pergunta_limpa = pergunta.strip().lower()
    
    if CACHE_ATIVADO == "TRUE":

        cache = carregar_cache()

        if pergunta_limpa in cache:
            print(f"[CACHE] Resposta recuperada do cache para: {pergunta_limpa}")
            return cache[pergunta_limpa]
        
        else:
            # Não está no cache → consulta a LLM
            resposta = query_fn(pergunta)
            cache = carregar_cache()
            cache[pergunta_limpa] = str(resposta)
            salvar_cache(cache)
            print(f"[CACHE] Resposta gerada e salva para: {pergunta_limpa}")
        return str(resposta)
    
    else:
        # Não está no cache → consulta a LLM
        resposta = query_fn(pergunta)
        return str(resposta)

def preencher_cache_com_exemplos(query_fn):
    '''Preenche o cache com perguntas sugeridas e suas respostas correspondentes.'''
    
    CACHE_ATIVADO = os.getenv("CACHE_ATIVADO")
    
    if CACHE_ATIVADO == "TRUE":

        todas_perguntas = [pergunta for lista in THEMATIC_QUESTIONS.values() for pergunta in lista]

        for i, pergunta in enumerate(todas_perguntas):
            # print(f"[CACHE] Preenchendo cache com pergunta {i+1}/{len(todas_perguntas)}: {pergunta}")
            _ = obter_ou_gerar_resposta(pergunta, query_fn)
