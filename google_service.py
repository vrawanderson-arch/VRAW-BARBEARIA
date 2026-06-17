import json
import base64
from email.message import EmailMessage

import streamlit as st

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets"
]

CALENDAR_ID = st.secrets.get("GOOGLE_CALENDAR_ID", "primary")


class GoogleService:

    def __init__(self):

        self.creds = self._authenticate()

        self.calendar_service = build(
            "calendar",
            "v3",
            credentials=self.creds
        )

        self.gmail_service = build(
            "gmail",
            "v1",
            credentials=self.creds
        )

        self.sheets_service = build(
            "sheets",
            "v4",
            credentials=self.creds
        )

    def _authenticate(self):

        try:

            secret = st.secrets["GOOGLE_SERVICE_ACCOUNT"]

            if isinstance(secret, str):
                service_account_info = json.loads(secret)
            else:
                service_account_info = dict(secret)

            creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES
            )

            return creds

        except Exception as e:
            raise Exception(
                f"Erro autenticação Google: {str(e)}"
            )

    def add_event(
        self,
        summary,
        start_time,
        end_time,
        description=""
    ):

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": "America/Sao_Paulo"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "America/Sao_Paulo"
            }
        }

        try:

            created_event = (
                self.calendar_service.events()
                .insert(
                    calendarId=CALENDAR_ID,
                    body=event
                )
                .execute()
            )

            return created_event.get("htmlLink")

        except HttpError as e:

            print(f"Erro Calendar: {e}")

            return None

    def send_email(
        self,
        to,
        subject,
        body
    ):

        try:

            message = EmailMessage()

            message.set_content(body)

            message["To"] = to
            message["From"] = "me"
            message["Subject"] = subject

            encoded_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()

            sent_message = (
                self.gmail_service.users()
                .messages()
                .send(
                    userId="me",
                    body={
                        "raw": encoded_message
                    }
                )
                .execute()
            )

            return sent_message

        except HttpError as e:

            print(f"Erro Gmail: {e}")

            return None

    def salvar_agendamento_planilha(
        self,
        spreadsheet_id,
        cliente,
        servico,
        data,
        email
    ):

        values = [
            [
                cliente,
                servico,
                data,
                email
            ]
        ]

        body = {
            "values": values
        }

        try:

            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="A:D",
                valueInputOption="RAW",
                body=body
            ).execute()

            return True

        except HttpError as e:

            print(f"Erro Sheets: {e}")

            return False
