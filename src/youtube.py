from googleapiclient.discovery import build
import os
import subprocess
import json
import time
from dotenv import load_dotenv
import streamlit as st

    
load_dotenv()

modo = os.getenv("MODO")

if modo == 'local':
    import whisper
    from slugify import slugify
    import yt_dlp

def buscar_videos_youtube(query, max_results=30):
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY não encontrada. Verifique o .env.")

    youtube = build('youtube', 'v3', developerKey=GOOGLE_API_KEY)

    resultados = youtube.search().list(
        q=query,
        part='id,snippet',
        type='video',
        maxResults=max_results,
        relevanceLanguage='pt',
        regionCode='BR'
    ).execute()

    videos = []
    for item in resultados['items']:
        video_id = item['id']['videoId']
        titulo = item['snippet']['title']
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append((titulo, url))
  
    return videos

def extrair_info_video(url):
    ydl_opts = {'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "upload_date": info.get("upload_date"),
            "uploader": info.get("uploader"),
            "channel_id": info.get("channel_id"),
            "duration": info.get("duration"),
            "webpage_url": info.get("webpage_url"),
        }

def baixar_audio_com_yt_dlp(url, output_path):
    '''Baixa o áudio diretamente em formato WAV se ainda não existir.'''
    if os.path.exists(output_path):
        print(f"⏩ Áudio já existe: {output_path}, pulando download.")
        return
    command = [
        'yt-dlp',
        '-f', 'bestaudio',
        '--extract-audio',
        '--audio-format', 'wav',
        '--output', output_path,
        url
    ]
    subprocess.run(command, check=True)

def transcrever_audio(audio_path, output_path):
    model = whisper.load_model("medium", device="cuda")
    print("🗣️ Transcrevendo com Whisper...")
    result = model.transcribe(audio_path, language='pt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result['text'])
    return result['text']

def main(url):
    # Extrai metadados e define paths
    print("🔍 Extraindo metadados do vídeo...")
    info = extrair_info_video(url)
    basename = slugify(info['id'])
    output_folder = os.path.join("src/transcriptions", basename)
    os.makedirs(output_folder, exist_ok=True)

    output_audio_filename = f"{basename}.wav"
    transcription_filename = f"{basename}_transcricao.txt"
    metadata_filename = f"{basename}_metadata.json"

    output_audio_path = os.path.join(output_folder, output_audio_filename)
    transcription_path = os.path.join(output_folder, transcription_filename)
    metadata_path = os.path.join(output_folder, metadata_filename)

    if os.path.exists(transcription_path):
        print(f"⏩ Já processado: {basename}, pulando...")
        return

    # Salva metadados
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"✅ Metadados salvos em {metadata_path}")

    # Baixa áudio (caso ainda não exista)
    print("⬇️ Baixando áudio com yt-dlp...")
    baixar_audio_com_yt_dlp(url, output_audio_path)

    # Transcreve
    transcrever_audio(output_audio_path, transcription_path)
    print(f"✅ Transcrição salva em {transcription_path}")

    # Remove WAV
    if os.path.exists(output_audio_path):
        os.remove(output_audio_path)
        print(f"🧹 Arquivo WAV removido: {output_audio_path}")

    print("✅ Processo finalizado para este vídeo!")

def baixar_videos_youtube_por_termo(termo_busca, num_videos):
    videos = buscar_videos_youtube(termo_busca, max_results=num_videos)

    for i, (titulo, url) in enumerate(videos):
        print(f"\n🔗 Processando vídeo {i + 1}/{len(videos)}")
        print(f"🎥 Título: {titulo}")
        print(f"🔗 URL: {url}")
        print("=========================================")

        inicio = time.time()
        try:
            main(url)
        except Exception as e:
            print(f"❌ Erro ao processar o vídeo {url}: {e}")
        fim = time.time()
        print(f"⏱️ Tempo gasto: {fim - inicio:.2f} segundos")

def contar_transcricoes_existentes(pasta="src/transcriptions"):
    total = 0
    for subpasta in os.listdir(pasta):
        caminho = os.path.join(pasta, subpasta)
        if os.path.isdir(caminho):
            arquivos_txt = [f for f in os.listdir(caminho) if f.endswith("_transcricao.txt")]
            if arquivos_txt:
                total += 1
    return total

def verifica_base_transcricoes():
    modo = os.getenv("MODO")
    
    if modo !='cloud':
        total_transcricoes_existentes = contar_transcricoes_existentes()
        num_videos = int(os.getenv("NUM_VIDEOS", 30))

        if total_transcricoes_existentes < num_videos:
            st.info(f"🔄 Transcrições insuficientes. Iniciando coleta de vídeos...")
            baixar_videos_youtube_por_termo("dicas Chile turismo", num_videos)
            st.info("✅ Transcrições mínimas baixadas e processadas.")
