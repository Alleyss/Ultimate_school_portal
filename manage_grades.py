import streamlit as st
from database import get_connection, auto_insert_evaluations
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode

def fetch_data(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

def update_evaluation_status(student_id, topic_id, completed):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Add print/logging statements for debugging
        print(f"Updating: student_id={student_id}, topic_id={topic_id}, completed={completed}")
        
        cursor.execute("UPDATE Evaluations SET completed=? WHERE student_id=? AND topic_id=?",
                       (completed, student_id, topic_id))
        
        # Check rows affected
        rows_affected = cursor.rowcount
        print(f"Rows affected: {rows_affected}")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating evaluation status: {e}")
    finally:
        conn.close()
        
def render_page():
    st.title("Manage Grades")
    selected_branch_id = st.session_state.userDetails['branch_id']
    teacher_id = st.session_state.userDetails.get('id')  # Get teacher_id from session

    # Fetch classes for the branch
    classes = fetch_data("SELECT id, name FROM Classes WHERE branch_id = ?", (selected_branch_id,))
    class_names = {class_item[0]: class_item[1] for class_item in classes}

    selected_class_id = st.selectbox("Select Class", list(class_names.keys()) if classes else [],
                                     format_func=lambda x: class_names[x] if classes else "", key="class_select")

    # Fetch sections for selected class
    sections = fetch_data("SELECT id, name FROM Sections WHERE class_id=?", (selected_class_id,)) if classes else None
    section_names = {section[0]: section[1] for section in sections} if sections else {}
    selected_section_id = st.selectbox("Select Section", list(section_names.keys()) if sections else [],
                                     format_func=lambda x: section_names[x] if sections else "", key="section_select") if sections else None

    if selected_section_id:
        # Add Initialize Evaluations button
        if st.button("Initialize Evaluations"):
            conn = get_connection()
            try:
                result = auto_insert_evaluations(
                    class_name=class_names[selected_class_id],
                    section_name=section_names[selected_section_id],
                    teacher_id=teacher_id,
                    db=conn
                )
                if result['status'] == 'success':
                    st.success(f"Successfully initialized {result['inserted_count']} evaluation records")
                else:
                    st.error(f"Error initializing evaluations: {result['message']}")
            finally:
                conn.close()

        students = fetch_data(
            """SELECT id, name FROM Students WHERE section_id = ?""",
            (selected_section_id,)
        )
        topics_data = fetch_data("""
            SELECT t.id, t.name 
            FROM Topics t
            JOIN Chapters c ON t.chapter_id = c.id
            JOIN Subjects s ON c.subject_id = s.id
            WHERE s.teacher_id = ?
        """, (teacher_id,))
        
        topics = {topic[0]: topic[1] for topic in topics_data}
        topic_ids = list(topics.keys())

        if students and topics:
            data = []
            for student in students:
                student_row = {"student_name": student[1], "student_id": student[0]}
                for topic_id in topic_ids:
                    evaluation_status = fetch_data("""
                        SELECT completed FROM Evaluations WHERE student_id = ? AND topic_id = ?
                    """, (student[0], topic_id))
                    student_row[str(topic_id)] = evaluation_status[0][0] if evaluation_status else "NO"
                data.append(student_row)

            df = pd.DataFrame(data)

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_column("student_name", header_name="Student Name", editable=False)
            gb.configure_column("student_id", hide=True)
            
            for topic_id in topic_ids:
                cell_renderer = JsCode("""
                    class MySelectCellRenderer {
                        init(params) {
                            this.value = params.value;
                            this.eGui = document.createElement('select');
                            this.options = ['YES','NO'];
                            for(let i = 0; i < this.options.length; i++){
                                let opt = document.createElement('option');
                                opt.value = this.options[i];
                                opt.text= this.options[i];
                                if(this.options[i] == this.value) opt.selected= true;
                                this.eGui.appendChild(opt);
                            }
                            this.eGui.addEventListener('change', (e)=> {
                                params.setValue(e.target.value);
                            })
                        }
                        getGui() {
                            return this.eGui;
                        }
                        getValue(){
                            return this.eGui.value;
                        }
                    }
                """)
                gb.configure_column(
                    str(topic_id),
                    header_name=topics[topic_id],
                    cellRenderer=cell_renderer,
                    editable=True
                )
            
            gridOptions = gb.build()

            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                height=400,
                data_return_mode='AS_INPUT',
                update_mode='MODEL_CHANGED',
                enable_enterprise_modules=True,
                theme='streamlit',
                width='100%'
            )

            if st.button("Save Changes"):
                updated_df = pd.DataFrame(grid_response['data'])
                
                for _, row in updated_df.iterrows():
                    student_id = row['student_id']
                    for topic_id in topic_ids:
                        topic_str = str(topic_id)
                        if topic_str in row:
                            new_value = row[topic_str]
                            # Fetch current value
                            current_evaluation = fetch_data("""
                                SELECT completed FROM Evaluations 
                                WHERE student_id = ? AND topic_id = ?
                            """, (student_id, topic_id))
                            old_value = current_evaluation[0][0] if current_evaluation else None
                            
                            # Update only if value has changed
                            if new_value != old_value:
                                update_evaluation_status(student_id, topic_id, new_value)
                
                st.success("Changes Saved Successfully!")

        elif students:
            st.warning("No topics available for the current teacher.")
        elif topics:
            st.warning("No students available in the selected section.")
        else:
            st.warning("No students or topics to display for the selected filter")
    else:
        st.info("Select class and section to view records.")

if __name__ == "__main__":
    if "userDetails" not in st.session_state:
        st.session_state.userDetails = {'branch_id': 1, 'id': 1}  # Added id for teacher_id
    render_page()