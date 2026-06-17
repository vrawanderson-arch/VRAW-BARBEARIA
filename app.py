import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

from dashboard_charts import create_advanced_dashboard
from google_service import GoogleService

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Agente IA Salão de Beleza Pro",
    page_icon="✂️",
    layout="wide"
)

load_dotenv()

def get_secret(key, default=None):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

SALAO_INFO = {
    "nome": get_secret("SALAO_NOME", "Salão Bella"),
    "endereco": get_secret("SALAO_ENDERECO", "Rua das Flores, 123"),
    "telefone": get_secret("SALAO_TELEFONE", "(81) 99999-9999"),
    "ia_nome": get_secret("IA_NOME", "Sofia")
}

# GEMINI
GEMINI_KEY = get_secret("GEMINI_API_KEY")
client = None
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)

# GOOGLE SERVICES
if "google_service" not in st.session_state:
    try:
        if get_secret("GOOGLE_SERVICE_ACCOUNT"):
            st.session_state.google_service = GoogleService()
        else:
            st.session_state.google_service = None
    except Exception as e:
        st.session_state.google_service = None
        st.error(f"ERRO GOOGLE: {e}")

# AGENDAMENTOS (PERSISTÊNCIA NA SESSÃO)
if "agendamentos" not in st.session_state:
    st.session_state.agendamentos = [
        {"id": 1, "cliente": "Ana Souza", "servico": "Manicure", "data": "2026-06-20 14:00", "status": "Confirmado", "telefone": "(81) 98765-4321", "email": "ana@email.com"},
        {"id": 2, "cliente": "Pedro Silva", "servico": "Corte masculino", "data": "2026-06-21 09:30", "status": "Confirmado", "telefone": "(81) 99876-5432", "email": "pedro@email.com"}
    ]

# MENU
st.sidebar.title(f"✂️ {SALAO_INFO['nome']}")
menu = st.sidebar.radio("Navegação", ["📊 Dashboard Avançado", "📅 Agendamentos", "💬 Chat IA", "⚙️ Integrações"])

# DASHBOARD
if menu == "📊 Dashboard Avançado":
    st.header("📊 Dashboard de Performance")
    df = pd.DataFrame(st.session_state.agendamentos)
    col1, col2, col3 = st.columns(3)
    fig_status, fig_receita, fig_evolucao = create_advanced_dashboard(df)
    if fig_status:
        with col1: st.plotly_chart(fig_status, width="stretch")
        with col2: st.plotly_chart(fig_receita, width="stretch")
        with col3: st.plotly_chart(fig_evolucao, width="stretch")
    else:
        st.info("Sem dados suficientes.")

# AGENDAMENTOS
elif menu == "📅 Agendamentos":
    st.header("📅 Gerenciar Agendamentos")
    
    with st.expander("➕ Novo Agendamento", expanded=True):
        with st.form("novo_agendamento"):
            nome = st.text_input("Nome do Cliente")
            email = st.text_input("E-mail")
            servico = st.selectbox("Serviço", ["Corte feminino", "Corte masculino", "Manicure", "Pedicure", "Coloração"])
            data = st.date_input("Data")
            hora = st.time_input("Hora")
            submit = st.form_submit_button("AGENDAR AGORA")

            if submit:
                if not nome:
                    st.error("Por favor, informe o nome do cliente.")
                else:
                    with st.spinner("Processando agendamento..."):
                        data_hora = f"{data} {hora}"
                        novo = {
                            "id": len(st.session_state.agendamentos) + 1,
                            "cliente": nome,
                            "servico": servico,
                            "data": data_hora,
                            "status": "Confirmado",
                            "email": email
                        }
                        st.session_state.agendamentos.append(novo)

                        # GOOGLE CALENDAR
                        if st.session_state.google_service:
                            try:
                                start = datetime.combine(data, hora).strftime("%Y-%m-%dT%H:%M:%S")
                                end = (datetime.combine(data, hora) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
                                link = st.session_state.google_service.add_event(f"{servico} - {nome}", start, end)
                                if link:
                                    st.success(f"✅ Agendado no Google! [Ver no Calendário]({link})")
                                else:
                                    st.warning("⚠️ Autenticado, mas o Google recusou a criação do evento. Verifique se você compartilhou o calendário com o e-mail da Service Account.")
                            except Exception as e:
                                st.error(f"Erro no Google Calendar: {e}")

                        # GOOGLE SHEETS (OPCIONAL)
                        sheet_id = get_secret("GOOGLE_SHEET_ID")
                        if st.session_state.google_service and sheet_id:
                            try:
                                success = st.session_state.google_service.salvar_agendamento_planilha(sheet_id, nome, servico, data_hora, email)
                                if success: st.success("✅ Salvo na Planilha Google!")
                            except Exception as e: st.error(f"Erro na Planilha: {e}")

                        st.success("✅ Agendamento salvo localmente!")
                        st.rerun()

    st.subheader("Lista de Agendamentos")
    st.dataframe(pd.DataFrame(st.session_state.agendamentos), use_container_width=True)

# CHAT IA
elif menu == "💬 Chat IA":
    st.header(f"💬 Conversar com {SALAO_INFO['ia_nome']}")
    user_input = st.chat_input("Como posso ajudar?")
    if user_input:
        st.write(f"👤 Você: {user_input}")
        if client:
            try:
                response = client.models.generate_content(model="gemini-2.0-flash", contents=user_input)
                st.write(f"💬 {SALAO_INFO['ia_nome']}: {response.text}")
            except Exception as e: st.error(f"Erro Gemini: {e}")
        else: st.error("Gemini API Key não configurada.")

# INTEGRAÇÕES
elif menu == "⚙️ Integrações":
    st.header("⚙️ Status das Integrações")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 Telegram")
        if get_secret("TELEGRAM_BOT_TOKEN"): st.success("✅ Configurado")
        else: st.error("❌ Não configurado")
    with col2:
        st.subheader("☁️ Google")
        if get_secret("GOOGLE_SERVICE_ACCOUNT"):
            st.success("✅ Secret encontrado")
            if st.session_state.google_service:
                st.success("✅ Autenticado com Sucesso")
                # Mostra o e-mail da service account para facilitar o compartilhamento
                try:
                    secret_data = json.loads(get_secret("GOOGLE_SERVICE_ACCOUNT"))
                    st.info(f"E-mail para compartilhar no Google Calendar:\n`{secret_data.get('client_email')}`")
                except: pass
            else: st.error("❌ Falha na autenticação")
        else: st.error("❌ Secret não encontrado")
