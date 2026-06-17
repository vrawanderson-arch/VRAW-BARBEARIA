# ✂️ Agente IA Salão de Beleza Pro (Versão Corrigida)

Este guia explica como configurar seu projeto do zero, desde o GitHub até o funcionamento das APIs de IA, Telegram e Google.

---

## 🚀 Passo 1: Subir para o GitHub

1.  Crie um novo repositório no [GitHub](https://github.com/) (ex: `agente-salao`).
2.  Na pasta do projeto, execute:
    ```bash
    git init
    git add .
    git commit -m "Projeto Corrigido"
    git branch -M main
    git remote add origin https://github.com/SEU_USUARIO/agente-salao.git
    git push -u origin main
    ```

---

## 🛠️ Passo 2: Deploy no Streamlit Cloud

1.  Acesse o [Streamlit Cloud](https://share.streamlit.io/).
2.  Conecte seu repositório e selecione o arquivo `app.py`.
3.  **IMPORTANTE:** Antes de clicar em "Deploy", vá em **"Advanced settings..." > "Secrets"**.

---

## 🔑 Passo 3: Configurando os Secrets (O Coração do App)

No campo **Secrets** do Streamlit Cloud, cole o código abaixo e preencha com suas chaves:

```toml
GEMINI_API_KEY = "SUA_CHAVE_GEMINI"
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_TELEGRAM"
SALAO_NOME = "Seu Salão"
SALAO_ENDERECO = "Seu Endereço"
SALAO_TELEFONE = "(XX) XXXXX-XXXX"
IA_NOME = "Sofia"

# Cole aqui TODO o conteúdo do arquivo JSON da sua Service Account do Google
GOOGLE_SERVICE_ACCOUNT = '''
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "...",
  ...
}
'''
```

---

## 🔑 Passo 4: Como conseguir cada chave

### 1. Google Gemini (IA)
1.  Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Clique em **"Create API key"**.

### 2. Telegram Bot
1.  Fale com o `@BotFather` no Telegram.
2.  Use `/newbot` e pegue o **API Token**.

### 3. Google Calendar e Gmail (Service Account)
1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um projeto e ative as APIs: `Google Calendar API` e `Gmail API`.
3.  Vá em **"IAM e Administrador" > "Contas de Serviço"**.
4.  Crie uma conta, vá na aba **"Chaves" > "Adicionar Chave" > "Criar nova chave" (JSON)**.
5.  **IMPORTANTE:** Abra esse JSON e cole o conteúdo no secret `GOOGLE_SERVICE_ACCOUNT` (conforme Passo 3).
6.  Para o Gmail funcionar, você deve autorizar o e-mail da service account a enviar e-mails ou usar delegação. *Dica: Para testes simples, o Calendar é mais imediato.*

---

## 🏃‍♂️ Passo 5: Funcionamento

1.  **Dashboard**: Gráficos automáticos baseados nos seus agendamentos.
2.  **Agendamentos**: Salva localmente na sessão e tenta enviar para o Google Calendar/Gmail se configurados.
3.  **Telegram**: Para rodar o bot, execute `python telegram_bot.py` em um terminal (local ou servidor).

---

**Desenvolvido por Manus AI**
