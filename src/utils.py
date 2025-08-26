import os
import streamlit as st
from fpdf import FPDF
import re

def trata_temas(resposta):
    # captura palavras entre aspas simples ou duplas
    temas = re.findall(r"'(.*?)'|\"(.*?)\"", resposta)
    
    # re.findall retorna lista de tuplas, pegar valores não vazios
    temas = [t1 or t2 for t1, t2 in temas]
    
    # junta numa string separada por vírgulas
    resultado = ", ".join(temas)
    return resultado

def mostra_origem_da_resposta(resposta, tipo):
    if tipo == 'curto':
        tamanho_resposta = 250
    elif tipo == 'longo':
        tamanho_resposta = 500
     
    if hasattr(resposta, 'source_nodes') and resposta.source_nodes:
        st.markdown("### Origem da Resposta")
        for node in resposta.source_nodes:
            st.markdown(f"- **Fonte:** {node.node_id} - **Texto:** {node.text[:tamanho_resposta]}...")
    else:
        st.markdown("### Origem da Resposta")
        st.markdown("Nenhuma fonte disponível.")

def exportar_historico_para_pdf(historico):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    fonte_regular = os.path.join("src", "fonts", "DejaVuSans.ttf")
    fonte_bold = os.path.join("src", "fonts", "DejaVuSans-Bold.ttf")

    pdf.add_font("DejaVu", "", fonte_regular, uni=True)
    pdf.add_font("DejaVu", "B", fonte_bold, uni=True)

    pdf.add_page()
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Histórico da Conversa", ln=True)
    pdf.ln(5)

    for pergunta, resposta in historico:
        pdf.set_font("DejaVu", "B", 12)
        pdf.multi_cell(0, 10, f"Você: {pergunta}")
        pdf.ln(1)

        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 10, f"LLM: {resposta}")
        pdf.ln(5)

    pdf.set_font("DejaVu", "", 10)
    pdf.ln(10)

    rodape = (
        "Este resumo foi gerado automaticamente por um assistente de IA criado por Rafael Gardel.\n"
        "Quer uma solução parecida? Me envie um email e poderemos conversar: rafaelgardel@gmail.com"
    )
    
    pdf.multi_cell(0, 10, rodape)

    caminho = "historico_conversa.pdf"
    # breakpoint()
    pdf.output(caminho)
    return caminho
