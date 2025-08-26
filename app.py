import streamlit as st
from src.paginas.home import home
from src.paginas.analise import analise
from src.paginas.contato import contato

# Inicializar o valor de página no session_state, se não estiver definido
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

# Menu de navegação na barra lateral
pagina_selecionada = st.sidebar.selectbox("Selecione uma página", 
                                          ["Home", "Análise", "Contato"],
                                          index=["Home", "Análise", "Contato"].index(st.session_state.pagina))

# Atualiza a página de acordo com a seleção do usuário
st.session_state.pagina = pagina_selecionada

# Carrega a página selecionada
if st.session_state.pagina == "Home":
    home()

elif st.session_state.pagina == "Análise":
    analise()
    
elif st.session_state.pagina == "Contato":
    contato()
