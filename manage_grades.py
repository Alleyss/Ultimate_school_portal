import streamlit as st
from database import get_connection
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode


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


def update_evaluation_status(student_id, topic_id, completed):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Evaluations SET completed=? WHERE student_id=? AND topic_id=?",
                       (completed, student_id, topic_id))
        conn.commit()

    except Exception as e:
        st.error(f"Error updating evaluation status: {e}")
    finally:
        conn.close()



def render_page():
    st.title("Manage Grades")
    selected_branch_id = st.session_state.userDetails['branch_id']

    classes = fetch_data("SELECT id, name FROM Classes WHERE branch_id = ?", (selected_branch_id,))
    class_names = {class_item[0]: class_item[1] for class_item in classes}

    selected_class_id = st.selectbox("Select Class", list(class_names.keys()) if classes else [],
                                     format_func=lambda x: class_names[x] if classes else "", key = "class_select")

    sections = fetch_data("SELECT id, name FROM Sections WHERE class_id=?", (selected_class_id,)) if classes else None
    section_names = {section[0]: section[1] for section in sections} if sections else {}
    selected_section_id = st.selectbox("Select Section", list(section_names.keys()) if sections else [],
                                     format_func=lambda x: section_names[x] if sections else "", key = "section_select") if sections else None
    
    if selected_section_id:
      
        students = fetch_data(
            """SELECT id, name FROM Students WHERE section_id = ?""",
            (selected_section_id,)
        )
        topics = fetch_data("SELECT id, name FROM Topics")
    
        if students and topics:
          student_ids = [student[0] for student in students]
          topic_ids = [topic[0] for topic in topics]
    
          # Creating the structure for the table
          data = []
          for student in students:
            student_row = {"student_name": student[1], "student_id": student[0]}
            for topic in topics:
              student_row[f"topic_{topic[0]}"] = fetch_data("""
                    SELECT completed FROM Evaluations WHERE student_id = ? AND topic_id = ?
                  """, (student[0],topic[0]))[0][0] if fetch_data("""
                    SELECT completed FROM Evaluations WHERE student_id = ? AND topic_id = ?
                  """, (student[0],topic[0])) else "NO"
            data.append(student_row)
          
          df = pd.DataFrame(data)
    
    
          gb = GridOptionsBuilder.from_dataframe(df)
          # Adding the editable dropdowns using cellRenderer
          for topic_id in topic_ids:
            cell_renderer = JsCode("""
                        class MySelectCellRenderer {
                            init(params) {
                                    this.value = params.value;
                                this.eGui = document.createElement('select');
                                this.options = ['YES','NO'];
                                    for(let i = 0; i < this.options.length; i++){
                                        let opt = document.createElement('option')
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
            gb.configure_column(f"topic_{topic_id}",
                cellRenderer=cell_renderer, editable=True,
              )
          gb.configure_column("student_id", hide=True) # hide student ids
          gridOptions = gb.build()
    
    
          grid_response = AgGrid(
              df,
              gridOptions=gridOptions,
              fit_columns_on_grid_load=True,
              allow_unsafe_jscode=True,
              height = 400,
              data_return_mode='AS_INPUT',
               update_mode='MODEL_CHANGED',
              enable_enterprise_modules=True,
               theme='streamlit', #Add theme color to the table
              width='100%'
              
            )

          if st.button("Save Changes"):
              updated_data = grid_response['data']
              for row in updated_data:
                  for topic_id in topic_ids:
                    if f"topic_{topic_id}" in row:
                      new_value = row[f"topic_{topic_id}"]
                      old_value = fetch_data("""
                            SELECT completed FROM Evaluations WHERE student_id = ? AND topic_id = ?
                          """, (row['student_id'],topic_id))[0][0] if fetch_data("""
                            SELECT completed FROM Evaluations WHERE student_id = ? AND topic_id = ?
                          """, (row['student_id'],topic_id)) else "NO"
                      if new_value != old_value:
                        update_evaluation_status(row['student_id'], topic_id,new_value)
              st.success("Changes Saved Successfully!")


        elif students:
            st.write("No topics available to display.")
        elif topics:
          st.write("No students available for the selected filter")
        else:
          st.write("No students or topics to display for the selected filter")

    else:
      st.write("Select class and section to view records.")