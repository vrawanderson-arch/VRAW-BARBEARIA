import streamlit as st
from google_service import GoogleService

st.title("Teste Google")

try:
    gs = GoogleService()

    resultado = (
        gs.calendar_service.calendarList()
        .list()
        .execute()
    )

    st.success("Autenticado")

    st.json(resultado)

except Exception as e:
    st.error(str(e))
