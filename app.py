import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

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

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def get_secret(key, default=None):
    if key in st.secrets:
        return st.secrets[key]

    return os.getenv(key, default)


# ==================================================
# CONFIGURAÇÕES GERAIS
# ==================================================

SALAO_INFO = {
    "nome": get_secret("SALAO_NOME", "Salão Bella"),
    "endereco": get_secret("SALAO_ENDERECO", "Rua das Flores, 123"),
    "telefone": get_secret("SALAO_TELEFONE", "(81) 99999-9999"),
    "ia_nome": get_secret("IA_NOME", "Sofia")
}

# ==================================================
# GEMINI
# ==================================================

GEMINI_KEY = get_secret("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# ==================================================
# GOOGLE SERVICES
# ==================================================

if "google_service" not in st.session_state:

    try:

        if get_secret("GOOGLE_SERVICE_ACCOUNT"):

            st.session_state.google_service = GoogleService()

        else:

            st.session_state.google_service = None

    except Exception as e:

        import traceback

        st.session_state.google_service = None

        st.error(f"ERRO GOOGLE: {e}")
        st.code(traceback.format_exc())

# ==================================================
# AGENDAMENTOS INICIAIS
# ==================================================

if "agendamentos" not in st.session_state:

    st.session_state.agendamentos = [
        {
            "id": 1,
            "cliente": "Ana Souza",
            "servico": "Manicure",
            "data": "2026-06-20 14:00",
            "status": "Confirmado",
            "telefone": "(81) 98765-4321",
            "email": "ana@email.com"
        },
        {
            "id": 2,
            "cliente": "Pedro Silva",
            "servico": "Corte masculino",
            "data": "2026-06-21 09:30",
            "status": "Confirmado",
            "telefone": "(81) 99876-5432",
            "email": "pedro@email.com"
        }
    ]

# ==================================================
# MENU
# ==================================================

st.sidebar.title(f"✂️ {SALAO_INFO['nome']}")

menu = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard Avançado",
        "📅 Agendamentos",
        "💬 Chat IA",
        "⚙️ Integrações"
    ]
)

# ==================================================
# DASHBOARD
# ==================================================

if menu == "📊 Dashboard Avançado":

    st.header("📊 Dashboard de Performance")

    df = pd.DataFrame(
        st.session_state.agendamentos
    )

    col1, col2, col3 = st.columns(3)

    fig_status, fig_receita, fig_evolucao = (
        create_advanced_dashboard(df)
    )

    if fig_status:

        with col1:
            st.plotly_chart(
                fig_status,
                width="stretch"
            )

        with col2:
            st.plotly_chart(
                fig_receita,
                width="stretch"
            )

        with col3:
            st.plotly_chart(
                fig_evolucao,
                width="stretch"
            )

    else:

        st.info(
            "Sem dados suficientes para gerar o dashboard."
        )

# ==================================================
# AGENDAMENTOS
# ==================================================

elif menu == "📅 Agendamentos":

    st.header("📅 Gerenciar Agendamentos")

    with st.expander("➕ Novo Agendamento"):

        with st.form("novo_agendamento"):

            nome = st.text_input(
                "Nome do Cliente"
            )

            email = st.text_input(
                "E-mail"
            )

            servico = st.selectbox(
                "Serviço",
                [
                    "Corte feminino",
                    "Corte masculino",
                    "Manicure",
                    "Pedicure",
                    "Coloração"
                ]
            )

            data = st.date_input(
                "Data"
            )

            hora = st.time_input(
                "Hora"
            )

            submit = st.form_submit_button(
                "Agendar"
            )

            if submit:

                if not nome:

                    st.error(
                        "Informe o nome do cliente."
                    )

                else:

                    data_hora = (
                        f"{data} {hora}"
                    )

                    novo = {
                        "id": len(
                            st.session_state.agendamentos
                        ) + 1,
                        "cliente": nome,
                        "servico": servico,
                        "data": data_hora,
                        "status": "Confirmado",
                        "email": email
                    }

                    st.session_state.agendamentos.append(
                        novo
                    )

                    # ==================================
                    # GOOGLE CALENDAR
                    # ==================================

                    if st.session_state.google_service:

                        try:

                            start = datetime.combine(
                                data,
                                hora
                            ).strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            )

                            end = (
                                datetime.combine(
                                    data,
                                    hora
                                )
                                + timedelta(hours=1)
                            ).strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            )

                            link = (
                                st.session_state.google_service
                                .add_event(
                                    f"{servico} - {nome}",
                                    start,
                                    end
                                )
                            )

                            if link:

                                st.success(
                                    "✅ Evento criado no Google Calendar"
                                )

                                st.markdown(
                                    f"[Abrir Evento]({link})"
                                )

                            else:

                                st.warning(
                                    "⚠️ Evento não criado."
                                )

                        except Exception as e:

                            st.error(
                                f"Erro Calendar: {e}"
                            )

                    # ==================================
                    # GMAIL
                    # ==================================

                    if (
                        st.session_state.google_service
                        and email
                    ):

                        try:

                            resultado = (
                                st.session_state.google_service
                                .send_email(
                                    email,
                                    f"Confirmação de Agendamento - {SALAO_INFO['nome']}",
                                    f"""
Olá {nome}!

Seu agendamento foi confirmado.

Serviço: {servico}
Data: {data_hora}

Obrigado pela preferência.
"""
                                )
                            )

                            if resultado:

                                st.success(
                                    "✅ E-mail enviado"
                                )

                            else:

                                st.warning(
                                    "⚠️ E-mail não enviado."
                                )

                        except Exception as e:

                            st.error(
                                f"Erro Gmail: {e}"
                            )

                    st.rerun()

    st.subheader(
        "Agendamentos"
    )

    st.table(
        pd.DataFrame(
            st.session_state.agendamentos
        )
    )

# ==================================================
# CHAT IA
# ==================================================

elif menu == "💬 Chat IA":

    st.header(
        f"💬 Conversar com {SALAO_INFO['ia_nome']}"
    )

    user_input = st.chat_input(
        "Como posso ajudar?"
    )

    if user_input:

        st.write(
            f"👤 Você: {user_input}"
        )

        if GEMINI_KEY:

            try:

                model = genai.GenerativeModel(
                    "gemini-1.5-flash"
                )

                response = (
                    model.generate_content(
                        user_input
                    )
                )

                st.write(
                    f"💬 {SALAO_INFO['ia_nome']}: {response.text}"
                )

            except Exception as e:

                st.error(
                    f"Erro Gemini: {e}"
                )

        else:

            st.error(
                "Gemini API Key não configurada."
            )

# ==================================================
# INTEGRAÇÕES
# ==================================================

elif menu == "⚙️ Integrações":

    st.header(
        "⚙️ Status das Integrações"
    )

    col1, col2 = st.columns(2)

    # Telegram

    with col1:

        st.subheader(
            "🤖 Telegram"
        )

        if get_secret(
            "TELEGRAM_BOT_TOKEN"
        ):

            st.success(
                "✅ Configurado"
            )

        else:

            st.error(
                "❌ Não configurado"
            )

    # Google

    with col2:

        st.subheader(
            "☁️ Google"
        )

        if get_secret(
            "GOOGLE_SERVICE_ACCOUNT"
        ):

            st.success(
                "✅ Secret encontrado"
            )

            if st.session_state.google_service:

                st.success(
                    "✅ Autenticado"
                )

            else:

                st.error(
                    "❌ Falha autenticação"
                )

        else:

            st.error(
                "❌ Secret não encontrado"
            )

    st.divider()

    st.subheader(
        "🧪 Teste da Integração Google"
    )

    if st.button(
        "TESTAR GOOGLE"
    ):

        try:

            resultado = (
                st.session_state.google_service
                .calendar_service
                .calendars()
                .get(
                    calendarId=st.secrets.get("GOOGLE_CALENDAR_ID","primary")
                )
                .execute()
            )

            st.success(
                "Google conectado!"
            )

            st.json(
                resultado
            )

        except Exception as e:

            st.error(
                f"Erro: {e}"
            )
