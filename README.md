# ✂️ Guia Completo: Agente IA Salão de Beleza Pro

Este guia explica como subir seu projeto para o **GitHub**, fazer o deploy no **Streamlit Cloud** e configurar todas as chaves de API passo a passo.

---

## 🚀 Passo 1: Subir para o GitHub

1.  Crie uma conta no [GitHub](https://github.com/) se não tiver.
2.  Clique no botão **"+"** no canto superior direito e selecione **"New repository"**.
3.  Dê um nome ao repositório (ex: `meu-salao-ia`) e clique em **"Create repository"**.
4.  No seu computador, dentro da pasta do projeto, abra o terminal e execute:
    ```bash
    git init
    git add .
    git commit -m "Primeiro commit"
    git branch -M main
    git remote add origin https://github.com/SEU_USUARIO/meu-salao-ia.git
    git push -u origin main
    ```

---

## 🛠️ Passo 2: Deploy no Streamlit Cloud

1.  Acesse o [Streamlit Cloud](https://share.streamlit.io/).
2.  Clique em **"Create app"**.
3.  Selecione seu repositório `meu-salao-ia`, a branch `main` e o arquivo principal `app.py`.
4.  **IMPORTANTE:** Antes de clicar em "Deploy", clique em **"Advanced settings..."**.
5.  Na caixa **"Secrets"**, você vai colar as chaves que vamos gerar nos próximos passos.

---

## 🔑 Passo 3: Conseguindo as Chaves de API

### 1. Google Gemini (Chat IA)
1.  Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Clique em **"Create API key"**.
3.  Copie a chave e guarde.

### 2. Telegram Bot
1.  No seu Telegram, procure por `@BotFather`.
2.  Mande `/newbot` e siga as instruções (escolha nome e usuário).
3.  Ele vai te dar um **API TOKEN**. Copie e guarde.

### 3. Google Cloud (Calendar e Gmail)
1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um projeto.
3.  Em **"APIs e Serviços" > "Biblioteca"**, ative: `Google Calendar API` e `Gmail API`.
4.  Em **"Tela de Consentimento OAuth"**, escolha "Externo", coloque seu e-mail e em "Escopos" adicione `.../auth/calendar` e `.../auth/gmail.send`.
5.  Em **"Credenciais"**, clique em **"+ Criar Credenciais" > "ID do cliente OAuth"**.
6.  Escolha **"Aplicativo para computador"**.
7.  Baixe o arquivo JSON. Abra ele com o bloco de notas e **copie todo o conteúdo**.

---

## 🔐 Passo 4: Configurando os Secrets no Streamlit

No painel do Streamlit Cloud (Advanced Settings > Secrets), cole o seguinte modelo e preencha com suas chaves:

```toml
GEMINI_API_KEY = "SUA_CHAVE_GEMINI"
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_TELEGRAM"
SALAO_NOME = "Salão Bella"
SALAO_ENDERECO = "Rua das Flores, 123"
SALAO_TELEFONE = "(81) 99999-9999"
IA_NOME = "Sofia"

# Cole aqui TODO o conteúdo do arquivo JSON que você baixou do Google
GOOGLE_CREDENTIALS_JSON = '''
{
  "installed": {
    "client_id": "...",
    "project_id": "...",
    ...
  }
}
'''
```

---

## 🏃‍♂️ Passo 5: Funcionamento

1.  **Dashboard**: Assim que o app abrir, os gráficos já estarão lá.
2.  **Agendamentos**: Ao criar um novo agendamento, se você configurou o Google corretamente, ele pedirá para você clicar em um link para autorizar o acesso (apenas na primeira vez).
3.  **Telegram**: O bot do Telegram precisa de um servidor rodando. Se você estiver usando o Streamlit Cloud, o bot não rodará sozinho. Você deve rodar `python integrations/telegram_bot.py` em sua máquina local ou em um VPS para que ele responda aos clientes.

---

**Dúvidas?** Consulte a documentação oficial do Streamlit ou as APIs do Google.
