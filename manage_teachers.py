import streamlit as st
from dashboards.superadmin_dashboard import create_user,update_user,delete_user,fetch_data
import pandas as pd

def render_page():
    # Teachers Operations
    st.header("Teacher Management")
    menu = ["Create Teachers", "See All Teachers", "Update Teachers", "Delete Teachers"]
    selected_operation = st.radio("Teachers Operations", menu)
    grp=['teacher']
    user_ids=fetch_data("SELECT id FROM users WHERE userType='teacher'")
    if selected_operation == "Create Teachers":
        create_user(grp)
    elif selected_operation == "See All Teachers":
       all_users = fetch_data("SELECT * FROM Users WHERE usertype='teacher'")
       st.subheader("All Teachers")
       if all_users:
          df_users = pd.DataFrame(all_users, columns=["id","username", "email", "password", "userType", "branch_id", "additional_details"])
          st.dataframe(df_users)
       else:
           st.write("No Teachers Found!")
    elif selected_operation == "Update Teachers":
       update_user(grp,user_ids)
    elif selected_operation == "Delete Teachers":
        delete_user()