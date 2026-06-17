import json
import base64
import streamlit as st
from email.message import EmailMessage
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets"
]

class GoogleService:
    def __init__(self):
        self.creds = self._authenticate()
        self.calendar_service = build("calendar", "v3", credentials=self.creds)
        self.gmail_service = build("gmail", "v1", credentials=self.creds)
        self.sheets_service = build("sheets", "v4", credentials=self.creds)

    def _authenticate(self):
        try:
            # Pega o segredo do Streamlit
            secret_data = st.secrets.get("GOOGLE_SERVICE_ACCOUNT")
            
            if not secret_data:
                raise Exception("Secret GOOGLE_SERVICE_ACCOUNT não encontrado.")

            # Se for string, tenta converter para dicionário
            if isinstance(secret_data, str):
                # Remove possíveis espaços em branco ou quebras de linha extras
                secret_data = secret_data.strip()
                service_account_info = json.loads(secret_data)
            else:
                # Se o Streamlit já converteu para dict (formato TOML)
                service_account_info = dict(secret_data)

            # CORREÇÃO CRÍTICA: Trata quebras de linha na private_key que o TOML costuma quebrar
            if "private_key" in service_account_info:
                service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

            creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES
            )
            return creds

        except Exception as e:
            st.error(f"Erro detalhado na autenticação Google: {e}")
            raise Exception(f"Falha ao processar credenciais Google: {str(e)}")

    def add_event(self, summary, start_time, end_time, description=""):
        calendar_id = st.secrets.get("GOOGLE_CALENDAR_ID", "primary")
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "America/Sao_Paulo"},
            "end": {"dateTime": end_time, "timeZone": "America/Sao_Paulo"}
        }
        try:
            created_event = self.calendar_service.events().insert(calendarId=calendar_id, body=event).execute()
            return created_event.get("htmlLink")
        except HttpError as e:
            st.error(f"Erro ao criar evento no Calendar: {e}")
            return None

    def send_email(self, to, subject, body):
        try:
            message = EmailMessage()
            message.set_content(body)
            message["To"] = to
            message["From"] = "me"
            message["Subject"] = subject
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            sent_message = self.gmail_service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
            return sent_message
        except HttpError as e:
            st.error(f"Erro ao enviar e-mail via Gmail: {e}")
            return None
