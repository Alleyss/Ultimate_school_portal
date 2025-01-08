import streamlit as st
from auth import authenticate_user, logout_user
from database import  create_tables,get_user_details
from dashboards import superadmin_dashboard, branchadmin_dashboard, teacher_dashboard
import manage_students,manage_branches,manage_subjects,manage_grades
from visualizations import fetch_data
from streamlit_tags import st_tags

st.set_page_config(layout="wide")

def main():
  st.title("School Management System")
  create_tables() # Create tables when the app is launched.

  if "user" not in st.session_state:
      st.session_state.user = None

  if st.session_state.user:
      if st.session_state.userDetails['userType'] == "superadmin":
        with st.sidebar:
          menu_options = ["Super Admin Dashboard","Branch Admin Dashboard", "Manage Branches", "Teacher Dashboard","Manage Subjects", "Logout"]
          menu_selection = st.radio("Menu", menu_options)
          
        if menu_selection == "Super Admin Dashboard":
            with st.sidebar:
               display_filters()
            superadmin_dashboard.render_dashboard()
        elif menu_selection == "Branch Admin Dashboard":
            with st.sidebar:
               display_filters()
            branchadmin_dashboard.render_dashboard()
        elif menu_selection == "Manage Branches":
          manage_branches.render_page()
        elif menu_selection == "Teacher Dashboard":
          teacher_dashboard.render_dashboard()
        elif menu_selection == "Manage Subjects":
          manage_subjects.render_page()
        elif menu_selection == "Logout":
            logout_user()
      elif st.session_state.userDetails['userType'] == "branchadmin":
        with st.sidebar:
          menu_options = ["Branch Admin Dashboard" ,"Manage Subjects", "Logout"]
          menu_selection = st.radio("Menu", menu_options)

        if menu_selection == "Branch Admin Dashboard":
          with st.sidebar:
             display_filters2()
          branchadmin_dashboard.render_dashboard()
        elif menu_selection == "Manage Subjects":
          manage_subjects.render_page()
        elif menu_selection == "Logout":
            logout_user()
      elif st.session_state.userDetails['userType'] == "teacher":
        with st.sidebar:
            st.write("Welcome Teacher:",st.session_state.userDetails['username'])
            st.write(st.session_state.userDetails['additional_details'])            
            menu_options = ["Teacher Dashboard", "Manage Students","Manage Grades","Logout"]
            menu_selection = st.radio("Menu", menu_options)
        if menu_selection == "Teacher Dashboard":
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
              user_details=get_user_details(username)
              st.session_state.user = user
              st.session_state.userDetails = user_details # Store user details
              #st.session_state.addDetails = add_details # Store additional details in session
              st.success(f"Logged in as {st.session_state.userDetails['userType']}")
              st.rerun()
          else:
              st.error("Login Failed")

def display_filters():
    # Fetch Branches Data
    branches = fetch_data("SELECT id, name FROM Branches")
    if branches:
        branch_names = {branch[0]: branch[1] for branch in branches}
        selected_branch_ids = st.multiselect(
            "Select Branch",
            list(branch_names.keys()),
            format_func=lambda x: branch_names[x],
            key="branch_select"
        )
        st.session_state.selected_branch_ids = selected_branch_ids
    else:
         st.write("No branches available")
    # Fetch Subjects Data
    subjects = fetch_data("SELECT id, name FROM Subjects")
    if subjects:
       subject_names = {subject[0]: subject[1] for subject in subjects}
       selected_subject_ids = st.multiselect(
            "Select Subjects",
            list(subject_names.keys()),
             format_func=lambda x: subject_names[x],
             key="subject_select",
        )
       st.session_state.selected_subject_ids = selected_subject_ids
    else:
      st.write("No Subjects available")
    # Fetch Grades (from Classes table)

def display_filters2():
    # Fetch Subjects Data
    subjects = fetch_data("SELECT id, name FROM Subjects")
    if subjects:
       subject_names = {subject[0]: subject[1] for subject in subjects}
       selected_subject_ids = st.multiselect(
            "Select Subjects",
            list(subject_names.keys()),
             format_func=lambda x: subject_names[x],
             key="subject_select",
        )
       st.session_state.selected_subject_ids = selected_subject_ids
    else:
      st.write("No Subjects available")
    # Fetch Grades (from Classes table)
   

if __name__ == "__main__":
    main()