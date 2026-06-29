#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Instalando DEV IA..."
echo ""

# Atualizar pacotes
echo "📦 Atualizando pacotes..."
pkg update -y && pkg upgrade -y

# Instalar dependências do sistema
echo "🔧 Instalando dependências..."
pkg install python git -y

# Permitir acesso ao armazenamento
echo "📁 Configurando armazenamento..."
termux-setup-storage

# Instalar bibliotecas Python
echo "🐍 Instalando bibliotecas Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar alias
echo "⚡ Criando atalho 'ia'..."
echo "alias ia='python $(pwd)/login-ia.py'" >> ~/.bashrc

# Executar setup
echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🎯 Executando configuração inicial..."
sleep 2
python setup.py

echo ""
echo "🎉 Tudo pronto! Digite 'ia' para começar."
