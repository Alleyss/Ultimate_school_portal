import streamlit as st
import plotly.express as px
import pandas as pd
from database import get_connection
from visualizations import display_branch_cards,display_branch_stats,student_distribution_by_branch,subject_wise_teacher_distribution,evaluation_visualizations_per_student,subject_wise_structure_analysis,performance_analysis_by_subject,class_wise_statistics

def fetch_data(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def create_user(grp):
    st.subheader("Create New User")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    userType = st.selectbox("User Type", grp)
    branches=fetch_data('SELECT id,name FROM Branches')
    if branches:
        # Extract branch names for display in the selectbox
        branch_names = [branch[1] for branch in branches]
        # Display branch names in the selectbox
        selected_branch_name = st.selectbox("Branch", branch_names)
        # Find the corresponding branch ID based on the selected name
        branch_id = next(branch[0] for branch in branches if branch[1] == selected_branch_name)
    else:
        st.error("No branches available. Please add branches first.")
        branch_id = None
    additional_details = st.text_area("Additional Details", value="")
    
    if st.button("Create User"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if branch_id:
                cursor.execute("INSERT INTO Users (username, email, password, userType, branch_id, additional_details) VALUES (?, ?, ?, ?, ?, ?)",
                                (username, email, password, userType, int(branch_id), additional_details))
            else:
                 cursor.execute("INSERT INTO Users (username, email, password, userType, additional_details) VALUES (?, ?, ?, ?, ?)",
                                (username, email, password, userType, additional_details))
            conn.commit()
            st.success("User Created Successfully")

        except Exception as e:
             st.error(f"Error creating user: {e}")
        finally:
            conn.close()


def update_user(grp,user_ids):
    st.subheader("Update User")
    user_id_update = st.selectbox("User ID",[i[0] for i in user_ids])
    new_email = st.text_input("New Email", value="")
    new_password = st.text_input("New Password (Leave blank to keep same)", type="password", value="")
    new_user_type = st.selectbox("New User Type", grp, index=0)
    new_branch_id = st.text_input("New Branch ID (Leave blank to keep same)", value="")
    new_additional_details = st.text_area("New Additional Details (Leave blank to keep same)", value="")


    if st.button("Update User"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if new_password:
                cursor.execute("UPDATE Users SET email=?, password=?, userType=?, branch_id=?, additional_details=? WHERE id=?",
                                (new_email, new_password, new_user_type,  int(new_branch_id) if new_branch_id else None , new_additional_details, int(user_id_update)))
            else:
                cursor.execute("UPDATE Users SET email=?, userType=?, branch_id=?, additional_details=? WHERE id=?",
                                (new_email, new_user_type, int(new_branch_id) if new_branch_id else None , new_additional_details, int(user_id_update)))
            conn.commit()
            st.success("User Updated Successfully!")

        except Exception as e:
            st.error(f"Error updating user {e}")
        finally:
            conn.close()

def delete_user():
    st.subheader("Delete User")
    user_id_delete = st.text_input("User ID to Delete")
    if st.button("Delete User"):
       conn = get_connection()
       cursor = conn.cursor()
       try:
            cursor.execute("DELETE FROM Users WHERE id=?", (int(user_id_delete),))
            conn.commit()
            st.success("User Deleted Successfully!")
       except Exception as e:
           st.error(f"Error deleting user {e}")
       finally:
           conn.close()


def render_dashboard():
    st.title("Super Admin Dashboard")
    grp=['superadmin','branchadmin','teacher']
    user_ids=fetch_data("SELECT id FROM users")
    # Fetch Data
    num_students = fetch_data("SELECT COUNT(*) FROM Students")[0][0]
    num_teachers = fetch_data("SELECT COUNT(*) FROM Users WHERE userType = 'teacher'")[0][0]
    num_branches = fetch_data("SELECT COUNT(*) FROM Branches")[0][0]
    num_branch_admins = fetch_data("SELECT COUNT(*) FROM Users WHERE userType = 'branchadmin'")[0][0]
    num_super_admins = fetch_data("SELECT COUNT(*) FROM Users WHERE userType = 'superadmin'")[0][0]

    # Display Numbers
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Number of Students", num_students)
    col2.metric("Number of Teachers", num_teachers)
    col3.metric("Number of Branches", num_branches)
    col4.metric("Number of Branch Admins", num_branch_admins)
    col5.metric("Number of Super Admins", num_super_admins)
    


    # Students per Branch Pie Chart
    students_per_branch_data = fetch_data("""
        SELECT b.name, COUNT(s.id)
        FROM Students s
        JOIN Sections sec ON s.section_id = sec.id
        JOIN Classes c ON sec.class_id = c.id
        JOIN Branches b ON c.branch_id = b.id
        GROUP BY b.name
    """)

    if students_per_branch_data:
      df_students_per_branch = pd.DataFrame(students_per_branch_data, columns=["Branch", "Number of Students"])
      fig_students_per_branch = px.pie(df_students_per_branch, names="Branch", values="Number of Students", title="Students Per Branch")
      st.plotly_chart(fig_students_per_branch)
    else:
        st.write("No student data found for pie chart")


    # Teachers per Branch Pie Chart
    teachers_per_branch_data = fetch_data("""
        SELECT b.name, COUNT(u.id)
        FROM Users u
        JOIN Branches b ON u.branch_id = b.id
        WHERE u.userType = 'teacher'
        GROUP BY b.name
    """)
    if teachers_per_branch_data:
       df_teachers_per_branch = pd.DataFrame(teachers_per_branch_data, columns=["Branch", "Number of Teachers"])
       fig_teachers_per_branch = px.pie(df_teachers_per_branch, names="Branch", values="Number of Teachers", title="Teachers Per Branch")
       st.plotly_chart(fig_teachers_per_branch)
    else:
         st.write("No teacher data found for pie chart")

    if 'userDetails' in st.session_state and 'branch_id' in st.session_state.userDetails:
         branch_id = st.session_state.userDetails['branch_id']
         #1. Display Table
         st.subheader("Branch Statistics")
         display_branch_stats()
        #2. Display Student Distribution Based on Branch
         st.subheader("Student Distribution by Branch")
         student_distribution_by_branch()
        #4. Cards with specific data of the selected branch
         st.subheader("Branch Specific Data")
         for branch in st.session_state.selected_branch_ids:
            st.write("Branch ID: ",branch)
            display_branch_cards(branch)

         # 5. Subject wise teacher distribution
         st.subheader("Subject Wise Teacher Distribution")
         subject_wise_teacher_distribution()
        #6. Class wise statistics
         st.subheader("Class Wise Statistics")
         class_wise_statistics()

         #Subject id selection for other visualizations
         subjects = fetch_data("SELECT id, name FROM Subjects")
         if subjects:
           #3. Performance Analysis based on selected subject
           for sub in st.session_state.selected_subject_ids:
            st.subheader("Performance Analysis Based on Selected Subject")
            performance_analysis_by_subject(sub)

            #7. Subject wise structure Analysis
            st.subheader("Subject Wise Structure Analysis")
            subject_wise_structure_analysis(sub)


         else:
            st.write("No Subject available to visualize")

         #8. Evaluation Visualizations
         st.subheader("Evaluation Visualizations per Student")
         students = fetch_data("SELECT id,name from Students")
         classes = fetch_data("SELECT id, name FROM Classes")
         sections = fetch_data("SELECT id, name from Sections")
         if students and classes and sections:
          student_names = {student[0]:student[1] for student in students}
          class_names = {class_item[0]:class_item[1] for class_item in classes}
          section_names = {section[0]:section[1] for section in sections}
          selected_student_id = st.selectbox("Select Student", list(student_names.keys()),format_func = lambda x: student_names[x])
          selected_class_id = st.selectbox("Select Class",list(class_names.keys()), format_func = lambda x: class_names[x])
          selected_section_id = st.selectbox("Select Section", list(section_names.keys()),format_func = lambda x: section_names[x])
          for sub in st.session_state.selected_subject_ids:
            evaluation_visualizations_per_student(selected_student_id, sub, selected_class_id, selected_section_id)

         else:
             st.write("No Students, Sections or Classes to show visualizations")



    else:
        st.write("User details or branch ID not available in session state. Please login.")

    
    
    
    
    
    
    
    # User Operations
    st.header("User Management")
    menu = ["Create User", "See All Users", "Update User", "Delete User"]
    selected_operation = st.radio("User Operations", menu)


    if selected_operation == "Create User":
        create_user(grp)
    elif selected_operation == "See All Users":
       all_users = fetch_data("SELECT * FROM Users")
       st.subheader("All Users")
       if all_users:
          df_users = pd.DataFrame(all_users, columns=["id","username", "email", "password", "userType", "branch_id", "additional_details"])
          st.dataframe(df_users)
       else:
           st.write("No User Found!")
    elif selected_operation == "Update User":
       update_user(grp)
    elif selected_operation == "Delete User":
        delete_user()