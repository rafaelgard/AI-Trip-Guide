#!/bin/bash
# Atualizar pacotes
sudo dnf update -y

# Limpar cache para liberar espaço antes de instalar dependências
sudo dnf clean all
sudo rm -rf /var/cache/dnf
sudo rm -rf /var/cache/yum
sudo rm -rf /tmp/*

# Instalar dependências básicas
sudo dnf install git -y
sudo dnf install python3.12 python3.12-pip -y

# Definir Python 3.12 como padrão
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 10
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 20
sudo alternatives --set python3 /usr/bin/python3.12

# Clonar o repositório
if [ ! -d "AI-Trip-Guide" ]; then
  git clone https://github.com/rafaelgard/AI-Trip-Guide.git
fi
cd AI-Trip-Guide

# Criar ambiente virtual
python3 -m venv env
source env/bin/activate

# Criar diretório temporário dedicado para o pip
mkdir -p /home/ec2-user/pip-tmp
export TMPDIR=/home/ec2-user/pip-tmp

# Instalar dependências
pip install --upgrade pip

# Limpar caches para economizar espaço
pip cache purge

if [ -f requirements-cloud.txt ]; then
  pip install -r requirements-cloud.txt --no-cache-dir
fi

# Remover temporários após a instalação
rm -rf /home/ec2-user/pip-tmp

# Rodar o Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
