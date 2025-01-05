import streamlit as st
from database import get_connection
from datetime import date

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


def add_student():
    st.subheader("Add New Student")
    name = st.text_input("Student Name")
    dob = st.date_input("Date of Birth", value = date.today())
    guardian_contact = st.text_input("Guardian Contact")
    enrollment_date = st.date_input("Enrollment Date", value=date.today())

    branches = fetch_data("SELECT id,name FROM Branches")
    branch_names = {branch[0]:branch[1] for branch in branches}
    selected_branch_id = st.selectbox("Select Branch", list(branch_names.keys()), format_func=lambda x: branch_names[x])
    classes = fetch_data("SELECT id,name FROM Classes WHERE branch_id = ?", (selected_branch_id,))
    class_names = {class_item[0]:class_item[1] for class_item in classes}

    selected_class_id = st.selectbox("Select Class",list(class_names.keys()) if classes else [], format_func=lambda x: class_names[x] if classes else "")
    sections = fetch_data("SELECT id, name FROM Sections WHERE class_id=?", (selected_class_id,)) if classes else None
    section_names = {section[0]:section[1] for section in sections} if sections else {}
    selected_section_id = st.selectbox("Select Section", list(section_names.keys()) if sections else [], format_func= lambda x: section_names[x] if sections else "") if sections else None


    if st.button("Add Student"):
        conn = get_connection()
        cursor = conn.cursor()
        try:

          cursor.execute("INSERT INTO Students (name, dob, guardian_contact, enrollment_date, section_id) VALUES (?, ?, ?, ?, ?)",
                       (name, dob, guardian_contact, enrollment_date, selected_section_id)
                       )
          conn.commit()
          st.success("Student Added Successfully!")
        except Exception as e:
          st.error(f"Error adding student: {e}")
        finally:
           conn.close()
           st.session_state.show_add_form = False
           st.rerun()



def edit_student(student_id):
  st.subheader("Edit Student")
  student = fetch_data("SELECT * FROM Students WHERE id = ?", (student_id,))[0]

  name = st.text_input("Student Name", value=student[1])
  dob = st.date_input("Date of Birth", value=student[2])
  guardian_contact = st.text_input("Guardian Contact", value=student[3])
  enrollment_date = st.date_input("Enrollment Date", value=student[4])


  branches = fetch_data("SELECT id,name FROM Branches")
  branch_names = {branch[0]:branch[1] for branch in branches}
  classes = fetch_data("""SELECT
                                c.id,
                                c.name
                            FROM Classes c
                                JOIN Sections s ON c.id = s.class_id
                                JOIN Students st ON s.id = st.section_id
                            WHERE st.id = ?;""",(student_id,))
  
  if classes:
    selected_branch_id = fetch_data("""
    SELECT b.id FROM Branches b 
    JOIN Classes c ON b.id = c.branch_id
    JOIN Sections s ON c.id = s.class_id
    JOIN Students st ON s.id = st.section_id
    WHERE st.id = ?""",(student_id,))[0][0]

    selected_branch_id = st.selectbox("Select Branch", list(branch_names.keys()), format_func=lambda x: branch_names[x], index = list(branch_names.keys()).index(selected_branch_id))
    class_names = {class_item[0]:class_item[1] for class_item in classes}
    selected_class_id = st.selectbox("Select Class",list(class_names.keys()) , format_func=lambda x: class_names[x] ,index = list(class_names.keys()).index(classes[0][0]))
    sections = fetch_data("SELECT id, name FROM Sections WHERE class_id=?", (selected_class_id,)) 
    section_names = {section[0]:section[1] for section in sections} if sections else {}
    selected_section_id = st.selectbox("Select Section", list(section_names.keys()) if sections else [], format_func= lambda x: section_names[x] if sections else "", index= list(section_names.keys()).index(fetch_data("SELECT section_id FROM Students WHERE id=?", (student_id,))[0][0]) if fetch_data("SELECT section_id FROM Students WHERE id=?", (student_id,)) else 0) if sections else None


    if st.button("Update Student"):
      conn = get_connection()
      cursor = conn.cursor()
      try:
          cursor.execute("UPDATE Students SET name=?, dob=?, guardian_contact=?, enrollment_date=?, section_id=? WHERE id=?",
                         (name, dob, guardian_contact, enrollment_date, selected_section_id, student_id))
          conn.commit()
          st.success("Student Updated Successfully!")
      except Exception as e:
          st.error(f"Error updating student: {e}")
      finally:
          conn.close()
          st.session_state.show_edit_form = False
          st.rerun()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Students WHERE id=?", (student_id,))
        conn.commit()
        st.success("Student Deleted Successfully!")
    except Exception as e:
        st.error(f"Error deleting student: {e}")
    finally:
        conn.close()
        st.rerun()


def fetch_students(selected_branch_id = None, selected_class_id = None, selected_section_id = None):
    query = """
        SELECT
            st.id,
            st.name,
            st.dob,
            st.guardian_contact,
            st.enrollment_date
        FROM
            Students st
        JOIN
            Sections s ON st.section_id = s.id
        JOIN
            Classes c ON s.class_id = c.id
        JOIN 
            Branches b ON c.branch_id = b.id
        WHERE 1=1
    """

    params = []
    if selected_branch_id:
         query += " AND b.id = ?"
         params.append(selected_branch_id)
    if selected_class_id:
        query += " AND c.id = ?"
        params.append(selected_class_id)
    if selected_section_id:
        query += " AND s.id = ?"
        params.append(selected_section_id)


    return fetch_data(query, params)


def render_page():
    st.title("Manage Students")

    branches = fetch_data("SELECT id,name FROM Branches")
    branch_names = {branch[0]:branch[1] for branch in branches}
    selected_branch_id = st.selectbox("Select Branch", list(branch_names.keys()), format_func=lambda x: branch_names[x])

    classes = fetch_data("SELECT id,name FROM Classes WHERE branch_id = ?", (selected_branch_id,))
    class_names = {class_item[0]:class_item[1] for class_item in classes}

    selected_class_id = st.selectbox("Select Class",list(class_names.keys()) if classes else [], format_func=lambda x: class_names[x] if classes else "")

    sections = fetch_data("SELECT id, name FROM Sections WHERE class_id=?", (selected_class_id,)) if classes else None
    section_names = {section[0]:section[1] for section in sections} if sections else {}
    selected_section_id = st.selectbox("Select Section", list(section_names.keys()) if sections else [], format_func= lambda x: section_names[x] if sections else "") if sections else None


    students = fetch_students(selected_branch_id, selected_class_id, selected_section_id)


    if students:
        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 2,1, 1])
        with col1:
           st.write("**Student ID**")
        with col2:
            st.write("**Student Name**")
        with col3:
           st.write("**Date of Birth**")
        with col4:
            st.write("**Guardian Contact**")
        with col5:
             st.write("**Edit**")
        with col6:
             st.write("**Delete**")

        for student in students:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 2,1, 1])
            with col1:
                st.write(student[0])  # Student ID
            with col2:
                st.write(student[1])  # Student Name
            with col3:
                st.write(student[2])  # Date of Birth
            with col4:
                st.write(student[3])  # Guardian Contact
            with col5:
                 if st.button("✏️", key=f"edit_{student[0]}"):
                    st.session_state.show_edit_form = True
                    st.session_state.student_code = student[0]
                    st.session_state.show_add_form = False
                    st.rerun()
            with col6:
                if st.button("🗑️", key=f"delete_{student[0]}"):
                    delete_student(student[0])

    else:
        st.write("No students available for the selected filters.")
    
    if st.button("Add New Student", key = "add_button"):
        st.session_state.show_add_form = True
        st.session_state.show_edit_form = False


    if st.session_state.get("show_add_form", False):
        add_student()

    if st.session_state.get("show_edit_form",False):
        edit_student(st.session_state.student_code)