import streamlit as st
from streamlit_gsheets import GSheetsConnection


class SheetConnector:
    def __init__(self, sheet_name):
        self.conn = st.connection('gsheets', type=GSheetsConnection)
        self.sheet_name = sheet_name

    def get_sheet(self):
        return self.conn.read(
            worksheet=self.sheet_name,
            ttl='3s'
        )

    def clear_sheet(self):
        self.conn.clear(
            worksheet=self.sheet_name
        )

    def update_sheet(self, df):
        self.conn.update(
            worksheet=self.sheet_name,
            data=df
        )