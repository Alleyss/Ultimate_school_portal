import streamlit as st
import sqlite3
from database import get_connection


def authenticate_user(username, password, remember_me):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, password FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    if user and user[1] == password:
        if remember_me:
            st.session_state['remember_user'] = True
            st.session_state['username'] = username

        return { "id" : user[0], "username": username }
    return None


def logout_user():
    if "remember_user" in st.session_state:
         del st.session_state["remember_user"]
         del st.session_state["username"]
    st.session_state.user = None
    st.rerun()


# Function to check if the user was remembered
def check_remembered_user():
    if "remember_user" in st.session_state and st.session_state['remember_user'] == True:
        return st.session_state["username"]
    return None