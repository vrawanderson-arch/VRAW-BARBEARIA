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
            # Pega o segredo bruto
            raw_secret = st.secrets.get("GOOGLE_SERVICE_ACCOUNT")
            if not raw_secret:
                raise Exception("Secret GOOGLE_SERVICE_ACCOUNT não encontrado.")

            # Se for um objeto do Streamlit (dict), converte para string JSON
            if not isinstance(raw_secret, str):
                raw_secret = json.dumps(dict(raw_secret))

            # ESTRATÉGIA DE EXTRAÇÃO MANUAL (SOLUÇÃO NUCLEAR)
            # Em vez de json.loads, vamos usar Regex para pegar os campos essenciais
            # Isso ignora qualquer caractere de controle ou quebra de linha inválida.
            
            def extract_field(field_name, text):
                pattern = f'"{field_name}"\s*:\s*"([^"]+)"'
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    return match.group(1)
                return None

            client_email = extract_field("client_email", raw_secret)
            project_id = extract_field("project_id", raw_secret)
            private_key_id = extract_field("private_key_id", raw_secret)
            
            # Para a Private Key, pegamos tudo entre as aspas, incluindo quebras de linha
            pk_pattern = r'"private_key"\s*:\s*"([^"]+)"'
            pk_match = re.search(pk_pattern, raw_secret, re.DOTALL)
            if not pk_match:
                raise Exception("Não foi possível encontrar a 'private_key' no segredo.")
            
            raw_pk = pk_match.group(1)
            
            # Limpeza e Formatação da Private Key
            header = "-----BEGIN PRIVATE KEY-----"
            footer = "-----END PRIVATE KEY-----"
            clean_pk = raw_pk.replace(header, "").replace(footer, "").replace("\\n", "").replace("\n", "").replace(" ", "").strip()
            
            formatted_pk = header + "\n"
            for i in range(0, len(clean_pk), 64):
                formatted_pk += clean_pk[i:i+64] + "\n"
            formatted_pk += footer + "\n"

            # Monta o dicionário que o Google espera
            info = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": private_key_id,
                "private_key": formatted_pk,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }

            if not client_email or not project_id:
                # Se a extração manual falhar, tenta o método tradicional como última esperança
                return service_account.Credentials.from_service_account_info(
                    json.loads(raw_secret, strict=False),
                    scopes=SCOPES
                )

            creds = service_account.Credentials.from_service_account_info(
                info,
                scopes=SCOPES
            )
            return creds

        except Exception as e:
            raise Exception(f"Falha na extração de credenciais: {str(e)}")

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
