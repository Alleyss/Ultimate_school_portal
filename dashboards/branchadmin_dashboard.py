import streamlit as st
from visualizations import display_branch_cards,student_distribution_by_branch,subject_wise_structure_analysis,display_branch_stats,subject_wise_teacher_distribution,class_wise_statistics,performance_analysis_by_subject,fetch_data,evaluation_visualizations_per_student
def render_dashboard():
    st.title("Branch Admin Dashboard")
    st.write("Welcome Branch Admin!")
    # Add Branch Admin dashboard functionalities and visualizations here
    if 'userDetails' in st.session_state and 'branch_id' in st.session_state.userDetails:
          branch_id = st.session_state.userDetails['branch_id']
          #4. Cards with specific data of the selected branch
          st.subheader("Branch Specific Data")
          st.write("Branch ID: ",branch_id)
          display_branch_cards(branch_id)

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

 