import streamlit as st
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

def add_branch():
    st.subheader("Add New Branch")
    name = st.text_input("Branch Name")
    location = st.text_input("Location")
    branch_admins_2d = fetch_data("SELECT username FROM Users WHERE userType='branchadmin'")
    branch_admins = [item[0] for item in branch_admins_2d]

    branch_admin = st.selectbox("Select Branch Admin", branch_admins)

    if st.button("Add Branch"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM Users WHERE username = ?", (branch_admin,))
            user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO Branches (name, location,branchadmin_id) VALUES (?, ?,?)", (name, location,user_id))
            conn.commit()
            st.success("Branch Created Successfully!")
        except Exception as e:
            st.error(f"Error creating branch: {e}")
        finally:
            conn.close()
            st.session_state.show_add_form = False
            st.rerun()


def edit_branch(branch_id):
    st.subheader("Edit Branch")
    branch = fetch_data("SELECT * FROM Branches WHERE id = ?", (branch_id,))[0]
    name = st.text_input("Branch Name", value=branch[1])
    location = st.text_input("Location", value=branch[2])
    branch_admins_2d = fetch_data("SELECT username FROM Users WHERE userType='branchadmin'")
    branch_admins = [item[0] for item in branch_admins_2d]

    branch_admin = st.selectbox("Select Branch Admin", branch_admins,  index = branch_admins.index(fetch_data("SELECT username FROM Users WHERE id = ?",(branch[3],))[0][0]) if fetch_data("SELECT username FROM Users WHERE id = ?",(branch[3],)) else 0)

    if st.button("Update Branch"):
      conn = get_connection()
      cursor = conn.cursor()
      try:
          # Fetch the id of the user from username
          cursor.execute("SELECT id FROM Users WHERE username = ?", (branch_admin,))
          user_id = cursor.fetchone()[0]

          # Update the Branches table with the new branchadmin_id
          cursor.execute("UPDATE Branches SET name=?, location=?, branchadmin_id=? WHERE id=?", (name, location, user_id, branch_id))
          # Update the Users Table for the branch admin
          cursor.execute("UPDATE Users SET branch_id=? WHERE id=?",(branch_id, user_id))

          # Set branch_id as NULL for previous admin if it is changed
          if branch[3]:
               cursor.execute("UPDATE Users SET branch_id=? WHERE id=?",(None, branch[3]))


          conn.commit()
          st.success("Branch Updated Successfully!")
      except Exception as e:
          st.error(f"Error updating branch: {e}")
      finally:
         conn.close()
         st.session_state.show_edit_form = False
         st.rerun()

def delete_branch(branch_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Branches WHERE id=?", (branch_id,))
        conn.commit()
        st.success("Branch Deleted Successfully!")
    except Exception as e:
        st.error(f"Error deleting branch: {e}")
    finally:
        conn.close()
        st.rerun()

def fetch_branches():
    return fetch_data("""
        SELECT
            b.id AS branch_code,
            b.name AS branch_name,
            u.username AS branch_admin_name
        FROM
            Branches b
        LEFT JOIN
            Users u ON b.branchadmin_id = u.id;
    """)
def render_page():
    st.title("Manage Branches")

    branches = fetch_branches()
    if branches:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
        with col1:
            st.write("**Branch ID**")
        with col2:
            st.write("**Branch Name**")
        with col3:
            st.write("**Branch Admin**")
        with col4:
            st.write("**Edit**")
        with col5:
            st.write("**Delete**")
        for branch in branches:
            col1, col2, col3, col4,col5 = st.columns([2, 2,2, 1, 1])
            with col1:
                st.write(branch[0])  # Branch code
            with col2:
                st.write(branch[1])  # Branch Name
            
            with col3:
                st.write(branch[2] if branch[2] else "None")  # BranchAdmin Name
            with col4:
                 if st.button("✏️", key=f"edit_{branch[0]}"):
                    st.session_state.show_edit_form = True
                    st.session_state.branch_code = branch[0]
                    st.session_state.show_add_form = False
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"delete_{branch[0]}"):
                    delete_branch(branch[0])

    else:
        st.write("No branches available.")
    if st.button("Add New Branch", key = "add_button"):
            st.session_state.show_add_form = True
            st.session_state.show_edit_form = False
    if st.session_state.get("show_add_form", False):
            add_branch()
    

    if st.session_state.get("show_edit_form", False):
         edit_branch(st.session_state.branch_code)