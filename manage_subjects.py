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

def add_subject():
    import streamlit as st

    st.subheader("Add New Subject")
    name = st.text_input("Subject Name")
    
    # Fetch class and teacher data
    classes = fetch_data("SELECT name, MIN(id) as id FROM Classes GROUP BY name")
    class_list = [item[0] for item in classes]
    class_name = st.selectbox("Select Class", class_list)
    
    teachers = fetch_data("SELECT username, MIN(id) as id FROM Users WHERE userType='teacher' GROUP BY username")
    teacher_list = [item[0] for item in teachers]
    teacher_name = st.selectbox("Select Teacher", teacher_list)

    if st.button("Add Subject"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Get class_id
            cursor.execute("SELECT id FROM Classes WHERE name = ?", (class_name,))
            class_id = cursor.fetchone()[0]

            # Get teacher_id
            cursor.execute("SELECT id FROM Users WHERE username = ?", (teacher_name,))
            teacher_id = cursor.fetchone()[0]

            # Insert new subject
            cursor.execute(
                "INSERT INTO Subjects (name, class_id, teacher_id) VALUES (?, ?, ?)",
                (name, class_id, teacher_id)
            )
            conn.commit()
            st.success("Subject Created Successfully!")
        except Exception as e:
            st.error(f"Error creating subject: {e}")
        finally:
            conn.close()
            st.session_state.show_add_form = False
            st.rerun()



def edit_subject(subject_id):
     st.subheader("Edit Subject")
     subject = fetch_data("SELECT * FROM Subjects WHERE id = ?", (subject_id,))[0]
     name = st.text_input("Subject Name", value=subject[1])
     classes = fetch_data("SELECT name, MIN(id) as id FROM Classes GROUP BY name")
     class_list = [item[0] for item in classes]
     class_name = st.selectbox("Select Class", class_list, index= class_list.index(fetch_data("SELECT c.name from Classes c JOIN Subjects s ON c.id = s.class_id WHERE s.id =?",(subject_id,))[0][0])  if fetch_data("SELECT c.name from Classes c JOIN Subjects s ON c.id = s.class_id WHERE s.id =?",(subject_id,)) else 0)

     if st.button("Update Subject"):
         conn = get_connection()
         cursor = conn.cursor()
         try:
             cursor.execute("SELECT id FROM Classes WHERE name = ?", (class_name,))
             class_id = cursor.fetchone()[0]
             cursor.execute("UPDATE Subjects SET name=?, class_id=? WHERE id=?", (name, class_id, subject_id))
             conn.commit()
             st.success("Subject Updated Successfully!")
         except Exception as e:
            st.error(f"Error updating subject: {e}")
         finally:
            conn.close()
            st.session_state.show_edit_form = False
            st.rerun()

def delete_subject(subject_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Subjects WHERE id=?", (subject_id,))
        conn.commit()
        st.success("Subject Deleted Successfully!")
    except Exception as e:
        st.error(f"Error deleting subject: {e}")
    finally:
        conn.close()
        st.rerun()

def fetch_subjects(class_id = None):
    if class_id:
        return fetch_data("SELECT s.id, s.name, c.name FROM Subjects s JOIN Classes c ON s.class_id = c.id WHERE c.id=?", (class_id,))
    else:
      return fetch_data("SELECT s.id, s.name, c.name FROM Subjects s JOIN Classes c ON s.class_id = c.id")

def add_chapter():

    st.subheader("Add New Chapter")
    # Chapter details
    chapter_name = st.text_input("Chapter Name", placeholder="Enter the name of the chapter")
    chapter_number = st.number_input("Chapter Number", min_value=1, step=1, format="%d")

    # Fetch subjects
    subjects = fetch_data("SELECT name, id FROM Subjects")
    if not subjects:
        st.error("No subjects available. Please add subjects first.")
        return

    subject_list = [item[0] for item in subjects]
    subject_name = st.selectbox("Select Subject", subject_list)

    if st.button("Add Chapter"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Get subject_id
            cursor.execute("SELECT id FROM Subjects WHERE name = ?", (subject_name,))
            subject_id = cursor.fetchone()[0]

            # Insert new chapter
            cursor.execute(
                "INSERT INTO Chapters (chapter_number, name, subject_id) VALUES (?, ?, ?)",
                (chapter_number, chapter_name, subject_id)
            )
            conn.commit()
            st.success("Chapter Created Successfully!")
        except Exception as e:
            st.error(f"Error creating chapter: {e}")
        finally:
            conn.close()
            st.rerun()


def add_topic():
    import streamlit as st

    st.subheader("Add New Topic")

    # Input fields for topic details
    topic_name = st.text_input("Topic Name", placeholder="Enter the name of the topic")
    topic_description = st.text_area("Topic Description", placeholder="Enter a brief description of the topic")
    topic_outcome = st.text_area("Topic Outcome", placeholder="Enter the learning outcome of the topic")

    # Fetch classes
    classes = fetch_data("SELECT name, MIN(id) as id FROM Classes GROUP BY name")
    if not classes:
        st.error("No classes available. Please add classes first.")
        return
    class_list = [item[0] for item in classes]
    class_name = st.selectbox("Select Class", class_list, key="add_topic_class")

    # Fetch subjects for the selected class
    subjects_2d = fetch_data(
        "SELECT s.name FROM Subjects s JOIN Classes c ON s.class_id = c.id WHERE c.name=?", (class_name,)
    )
    if not subjects_2d:
        st.error("No subjects available for the selected class. Please add subjects first.")
        return
    subject_list = [item[0] for item in subjects_2d]
    subject_name = st.selectbox("Select Subject", subject_list, key="add_topic_subject")

    # Fetch chapters for the selected subject and class
    chapters_2d = fetch_data(
        "SELECT ch.name FROM Chapters ch JOIN Subjects s ON ch.subject_id = s.id "
        "JOIN Classes c ON s.class_id = c.id WHERE s.name = ? AND c.name = ?",
        (subject_name, class_name)
    )
    if not chapters_2d:
        st.error("No chapters available for the selected subject. Please add chapters first.")
        return
    chapter_list = [item[0] for item in chapters_2d]
    chapter_name = st.selectbox("Select Chapter", chapter_list, key="add_topic_chapter")

    # Add topic button
    if st.button("Add Topic"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Fetch chapter_id
            cursor.execute("SELECT id FROM Chapters WHERE name = ?", (chapter_name,))
            chapter_id = cursor.fetchone()[0]

            # Insert the new topic
            cursor.execute(
                "INSERT INTO Topics (name, description, outcome, chapter_id) VALUES (?, ?, ?, ?)",
                (topic_name, topic_description, topic_outcome, chapter_id)
            )
            conn.commit()
            st.success("Topic Created Successfully!")
        except Exception as e:
            st.error(f"Error creating topic: {e}")
        finally:
            conn.close()
            st.session_state.show_add_form_topic = False
            st.rerun()


def render_page():
    st.title("Manage Subjects")

    classes = fetch_data("SELECT name, MIN(id) as id FROM Classes GROUP BY name")
    class_list = [item[0] for item in classes]
    class_name = st.selectbox("Select Class", class_list,key="class_selectbox")
    if class_name:
        cursor = fetch_data("SELECT id FROM Classes WHERE name=?", (class_name,))
        class_id = cursor[0][0]
        subjects = fetch_subjects(class_id)
    else:
        subjects = fetch_subjects()
    if subjects:
        # Display column headers
        col1, col2, col3, col4,col5= st.columns([2, 2, 2, 1, 1])
        with col1:
          st.write("**Subject ID**")
        with col2:
           st.write("**Subject Name**")
        with col3:
           st.write("**Class Name**")
        with col4:
            st.write("**Edit**")
        with col5:
            st.write("**Delete**")
        for subject in subjects:
             col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
             with col1:
                st.write(subject[0]) # Subject id
             with col2:
                 st.write(subject[1])  # Subject name
             with col3:
                 st.write(subject[2]) # class_name
             with col4:
                 if st.button("✏️", key=f"edit_{subject[0]}"):
                     st.session_state.show_edit_form = True
                     st.session_state.subject_code = subject[0]
                     st.session_state.show_add_form = False
                     st.session_state.show_add_form_chapter = False
                     st.session_state.show_add_form_topic = False
                     st.rerun()
             with col5:
                    if st.button("🗑️", key=f"delete_{subject[0]}"):
                       delete_subject(subject[0])
    else:
        st.write("No subjects available.")

    if st.button("Add New Subject", key = "add_subject_button"):
        st.session_state.show_add_form = True
        st.session_state.show_edit_form = False
        st.session_state.show_add_form_chapter = False
        st.session_state.show_add_form_topic = False
    if st.session_state.get("show_add_form", False):
          add_subject()

    if st.session_state.get("show_edit_form", False):
          edit_subject(st.session_state.subject_code)

    

    # Class and Subject Filter for Chapters
    st.subheader("Manage Chapters")

    classes_for_chapter = fetch_data("SELECT name, MIN(id) as id FROM Classes GROUP BY name")
    class_list_chapter = [item[0] for item in classes_for_chapter]
    class_name_chapter = st.selectbox("Select Class for Chapters", class_list_chapter, key="chapter_class_select")
    if class_name_chapter:
      subjects_for_chapter = fetch_data("SELECT s.name FROM Subjects s JOIN Classes c ON s.class_id = c.id WHERE c.name=? GROUP BY s.name",(class_name_chapter,))
      subject_list_chapter = [item[0] for item in subjects_for_chapter]
      subject_name_chapter = st.selectbox("Select Subject for Chapters", subject_list_chapter, key="chapter_subject_select")
      if subject_name_chapter:
         chapters = fetch_data("SELECT ch.chapter_number, ch.name, ch.subject_id from Chapters ch JOIN Subjects s ON ch.subject_id = s.id WHERE s.name = ?", (subject_name_chapter,))
         if chapters:
           col1,col2,col3=st.columns([2,2,2])
           with col1:
               st.write("**Chapter Number**")
           with col2:
               st.write("**Chapter Name**")
           with col3:
               st.write("**Subject ID**")
           for chapter in chapters:
              col1,col2,col3=st.columns([2,2,2])
              with col1:
                  st.write(chapter[0])
              with col2:
                  st.write(chapter[1])
              with col3:
                  st.write(chapter[2])
         else:
            st.write("No chapters available for the given subject and class")
      else:
        st.write("No subject selected")

    else:
       st.write("No class selected")

    if st.button("Add New Chapter", key = "add_chapter_button"):
        st.session_state.show_add_form_chapter = True
        st.session_state.show_edit_form = False
        st.session_state.show_add_form = False
        st.session_state.show_add_form_topic = False

    if st.session_state.get("show_add_form_chapter",False):
        add_chapter()

    st.subheader("Manage Topics")
    classes_for_topic = fetch_data("SELECT name, MIN(id) as id FROM Classes GROUP BY name")
    class_list_topic = [item[0] for item in classes_for_topic]
    class_name_topic = st.selectbox("Select Class for Topics", class_list_topic, key="topic_class_select")

    if class_name_topic:
      subjects_for_topic = fetch_data("SELECT s.name FROM Subjects s JOIN Classes c ON s.class_id = c.id WHERE c.name=? GROUP BY s.name",(class_name_topic,))
      subject_list_topic = [item[0] for item in subjects_for_topic]
      subject_name_topic = st.selectbox("Select Subject for Topics", subject_list_topic, key="topic_subject_select")
      if subject_name_topic:
        chapters_for_topic = fetch_data("SELECT ch.name from Chapters ch JOIN Subjects s ON ch.subject_id=s.id  JOIN Classes c ON s.class_id = c.id WHERE s.name=? AND c.name = ? GROUP BY ch.name",(subject_name_topic, class_name_topic))
        chapter_list_topic = [item[0] for item in chapters_for_topic]
        chapter_name_topic = st.selectbox("Select Chapter for Topics", chapter_list_topic, key="topic_chapter_select")
        if chapter_name_topic:
            topics = fetch_data("SELECT t.id, t.name, t.description,t.outcome from Topics t JOIN Chapters ch ON t.chapter_id = ch.id WHERE ch.name = ?", (chapter_name_topic,))
            if topics:
                col1,col2,col3,col4=st.columns([2,2,2,2])
                with col1:
                    st.write("**Topic ID**")
                with col2:
                    st.write("**Topic Name**")
                with col3:
                    st.write("**description**")
                with col4:
                    st.write("**outcome**")
                for topic in topics:
                    col1,col2,col3,col4=st.columns([2,2,2,2])
                    with col1:
                        st.write(topic[0])
                    with col2:
                        st.write(topic[1])
                    with col3:
                        st.write(topic[2])
                    with col4:
                        st.write(topic[3])
            else:
               st.write("No topics available for the given chapter, subject and class")
        else:
            st.write("No chapter selected")

      else:
          st.write("No subject selected")
    else:
        st.write("No class selected")
    if st.button("Add New Topic", key = "add_topic_button"):
        st.session_state.show_add_form_topic = True
        st.session_state.show_edit_form = False
        st.session_state.show_add_form_chapter = False
        st.session_state.show_add_form = False
    if st.session_state.get("show_add_form_topic", False):
          add_topic()
