import streamlit as st
from auth import authenticate_user, logout_user
from database import get_user_type, create_tables
from dashboards import superadmin_dashboard, branchadmin_dashboard, teacher_dashboard
import manage_students,manage_branches,manage_subjects,manage_grades

st.set_page_config(layout="wide")

def main():
  st.title("School Management System")
  create_tables() # Create tables when the app is launched.

  if "user" not in st.session_state:
      st.session_state.user = None

  if st.session_state.user:
      if st.session_state.user['userType'] == "superadmin":
        with st.sidebar:
          menu_options = ["Super Admin Dashboard","Branch Admin Dashboard", "Manage Branches", "Teacher Dashboard","Manage Subjects","Manage Students", "Logout"]
          menu_selection = st.radio("Menu", menu_options)

        if menu_selection == "Super Admin Dashboard":
            superadmin_dashboard.render_dashboard()
        elif menu_selection == "Branch Admin Dashboard":
            branchadmin_dashboard.render_dashboard()
        elif menu_selection == "Manage Branches":
          manage_branches.render_page()
        elif menu_selection == "Teacher Dashboard":
          teacher_dashboard.render_dashboard()
        elif menu_selection == "Manage Subjects":
          manage_subjects.render_page()
        elif menu_selection == "Manage Students":
          manage_students.render_page()
        elif menu_selection == "Logout":
            logout_user()
      elif st.session_state.user['userType'] == "branchadmin":
        with st.sidebar:
          menu_options = ["Branch Admin Dashboard", "Manage Branches" ,"Teacher Dashboard","Manage Subjects","Manage Students", "Logout"]
          menu_selection = st.radio("Menu", menu_options)

        if menu_selection == "Branch Admin Dashboard":
          branchadmin_dashboard.render_dashboard()
        elif menu_selection == "Manage Branches":
          manage_branches.render_page()
        elif menu_selection == "Teacher Dashboard":
          teacher_dashboard.render_dashboard()
        elif menu_selection == "Manage Subjects":
          manage_subjects.render_page()
        elif menu_selection == "Manage Students":
          manage_students.render_page()
        elif menu_selection == "Logout":
            logout_user()
      elif st.session_state.user['userType'] == "teacher":
        with st.sidebar:
            st.write(st.session_state.user['additonal_details'])
            menu_options = ["Teacher Dashboard", "Manage Students","Manage Grades","Logout"]
            menu_selection = st.radio("Menu", menu_options)
        if menu_selection == "Dashboard":
          teacher_dashboard.render_dashboard()
        elif menu_selection == "Manage Students":
          manage_students.render_page()
        elif menu_selection == "Manage Grades":
          manage_grades.render_page()
        elif menu_selection == "Logout":
            logout_user()


  else:
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      remember_me = st.checkbox("Remember me")
      if st.button("Login"):
          user = authenticate_user(username, password, remember_me)
          if user:
              user_type = get_user_type(username)
              st.session_state.user = user
              st.session_state.user['userType'] = user_type # Store user type in session
              st.success(f"Logged in as {user_type}")
              st.rerun()
          else:
              st.error("Login Failed")

if __name__ == "__main__":
    main()