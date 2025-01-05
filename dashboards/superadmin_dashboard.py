import streamlit as st
import plotly.express as px
import pandas as pd
from database import get_connection


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

def create_user():
    st.subheader("Create New User")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    userType = st.selectbox("User Type", ["superadmin", "branchadmin", "teacher"])
    branch_id = st.text_input("Branch ID (Leave Blank for Super Admin)", value="")
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


def update_user():
    st.subheader("Update User")
    user_id_update = st.text_input("User ID to Update")
    new_email = st.text_input("New Email", value="")
    new_password = st.text_input("New Password (Leave blank to keep same)", type="password", value="")
    new_user_type = st.selectbox("New User Type", ["superadmin", "branchadmin", "teacher"], index=0)
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


    # User Operations
    st.header("User Management")
    menu = ["Create User", "See All Users", "Update User", "Delete User"]
    selected_operation = st.radio("User Operations", menu)


    if selected_operation == "Create User":
        create_user()
    elif selected_operation == "See All Users":
       all_users = fetch_data("SELECT * FROM Users")
       st.subheader("All Users")
       if all_users:
          df_users = pd.DataFrame(all_users, columns=["id","username", "email", "password", "userType", "branch_id", "additional_details"])
          st.dataframe(df_users)
       else:
           st.write("No User Found!")
    elif selected_operation == "Update User":
       update_user()
    elif selected_operation == "Delete User":
        delete_user()