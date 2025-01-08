import streamlit as st
import sqlite3
from visualizations import display_overview,display_completion_pie_chart,display_chapter_histogram,display_student_histogram,display_student_performance_graph,display_chapter_wise_table

def render_dashboard():
    st.title("Teacher Dashboard")
    st.write("Welcome Teacher!")
    if st.session_state.userDetails is not None:
        teacher_username = st.session_state.userDetails["username"]

    # Connect to SQLite database
        conn = sqlite3.connect('school.db')  # Replace with your database file
        cursor = conn.cursor()

        display_overview(cursor, teacher_username)
        display_completion_pie_chart(cursor, teacher_username)
        display_chapter_histogram(cursor, teacher_username)
        display_student_histogram(cursor, teacher_username)
        display_student_performance_graph(cursor, teacher_username)
        display_chapter_wise_table(cursor, teacher_username)


        conn.close()
    else:
        st.write("Not logged In")
    # Add Teacher dashboard functionalities and visualizations here