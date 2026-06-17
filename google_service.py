import json
import base64
import streamlit as st
import re
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
            secret_data = st.secrets.get("GOOGLE_SERVICE_ACCOUNT")
            if not secret_data:
                raise Exception("Secret GOOGLE_SERVICE_ACCOUNT não encontrado.")

            if isinstance(secret_data, str):
                # Remove espaços e limpa o JSON
                clean_json = secret_data.strip()
                service_account_info = json.loads(clean_json)
            else:
                service_account_info = dict(secret_data)

            # RECONSTRUÇÃO AGRESSIVA DA PRIVATE KEY
            if "private_key" in service_account_info:
                key = service_account_info["private_key"]
                
                # 1. Remove cabeçalhos e rodapés temporariamente para limpar o miolo
                header = "-----BEGIN PRIVATE KEY-----"
                footer = "-----END PRIVATE KEY-----"
                
                # Limpa tudo que não for base64 ou os marcadores
                key_content = key.replace(header, "").replace(footer, "").replace("\\n", "").replace("\n", "").replace(" ", "").strip()
                
                # 2. Reconstrói a chave no formato padrão (64 caracteres por linha)
                formatted_key = header + "\n"
                for i in range(0, len(key_content), 64):
                    formatted_key += key_content[i:i+64] + "\n"
                formatted_key += footer + "\n"
                
                service_account_info["private_key"] = formatted_key

            creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES
            )
            return creds

        except Exception as e:
            raise Exception(f"Erro ao processar credenciais: {str(e)}")

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
            st.error(f"Erro Calendar: {e}")
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
            st.error(f"Erro Gmail: {e}")
            return None

    def salvar_agendamento_planilha(self, spreadsheet_id, cliente, servico, data, email):
        values = [[cliente, servico, data, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
        body = {"values": values}
        try:
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="A:E",
                valueInputOption="RAW",
                body=body
            ).execute()
            return True
        except Exception as e:
            st.error(f"Erro Planilha: {e}")
            return False
