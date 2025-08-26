import streamlit as st

def contato():
    st.title("📧 Contato")

    st.write("Entre em contato comigo através das opções abaixo:")

    st.markdown(
        """
        - 📩 **E-mail**: [rafaelgardel@gmail.com](mailto:rafaelgardel@gmail.com)  
        - 💼 **LinkedIn**: [linkedin.com/in/rafael-gardel-b1976999](https://www.linkedin.com/in/rafael-gardel-b1976999/)  
        - 🐙 **Portfólio**: [rafaelgard.github.io](https://rafaelgard.github.io/)  
        """
    )

    # st.divider()

    # st.subheader("📨 Envie uma mensagem rápida")
    # with st.form("form_contato"):
    #     nome = st.text_input("Seu nome")
    #     email = st.text_input("Seu e-mail")
    #     mensagem = st.text_area("Mensagem")
    #     enviar = st.form_submit_button("Enviar")

    #     if enviar:
    #         if nome and email and mensagem:
    #             st.success(f"Obrigado {nome}, sua mensagem foi enviada com sucesso!")
    #             # Aqui você pode integrar com um backend (ex: e-mail, banco de dados, Google Sheets, etc.)
    #         else:
    #             st.error("Por favor, preencha todos os campos antes de enviar.")
