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
                # LIMPEZA CRÍTICA: Remove caracteres de controle (como quebras de linha reais) 
                # que quebram o parser de JSON, mas mantém os espaços normais.
                clean_json = re.sub(r'[\x00-\x1F\x7F]', '', secret_data)
                
                # Se o regex removeu as quebras de linha necessárias da private_key, 
                # o json.loads ainda pode falhar. Vamos tentar carregar.
                try:
                    service_account_info = json.loads(clean_json)
                except:
                    # Se falhar, tenta carregar o original mas limpando apenas as quebras de linha
                    # que estão dentro de valores de string.
                    service_account_info = json.loads(secret_data, strict=False)
            else:
                service_account_info = dict(secret_data)

            # Garante que a private_key tenha os \n corretos para o Google
            if "private_key" in service_account_info:
                key = service_account_info["private_key"]
                if "\\n" in key:
                    service_account_info["private_key"] = key.replace("\\n", "\n")
                elif "\n" not in key:
                    # Caso a chave tenha vindo em uma linha só sem os \n
                    st.warning("Atenção: A chave privada parece estar mal formatada.")

            creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES
            )
            return creds

        except Exception as e:
            raise Exception(f"Erro no processamento do JSON: {str(e)}")

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
            st.error(f"Erro ao enviar e-mail via Gmail: {e}")
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
            st.error(f"Erro ao salvar na planilha: {e}")
            return False
