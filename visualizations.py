import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


# Helper function to fetch data from the database
def fetch_data(query, params=None):
    conn = sqlite3.connect("school.db") #Replace with your actual DB name
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# 1. Table with Branch Statistics
def display_branch_stats():
    query = """
        SELECT
            b.name,
            COUNT(DISTINCT s.id) AS num_students,
            COUNT(DISTINCT u.id) AS num_teachers,
            COUNT(DISTINCT c.id) AS num_classes,
            COUNT(DISTINCT sec.id) AS num_sections
        FROM Branches b
        LEFT JOIN Classes c ON b.id = c.branch_id
        LEFT JOIN Sections sec ON c.id = sec.class_id
        LEFT JOIN Students s ON sec.id = s.section_id
        LEFT JOIN Users u ON s.section_id IN (
                SELECT sec2.id
                FROM Sections sec2
                JOIN Classes c2 ON sec2.class_id = c2.id
                JOIN Subjects sub ON c2.id = sub.class_id
                WHERE sub.teacher_id = u.id
            )
        GROUP BY b.name
    """
    results = fetch_data(query)
    if results:
        df = pd.DataFrame(results, columns=['Branch Name', 'Students', 'Teachers', 'Classes', 'Sections'])
        st.table(df)
    else:
        st.write("No branch data available.")


# 2. Student Distribution Based on Branch (Bar Chart)
def student_distribution_by_branch():
    query = """
        SELECT b.name, COUNT(s.id) AS num_students
        FROM Branches b
        LEFT JOIN Classes c ON b.id = c.branch_id
        LEFT JOIN Sections sec ON c.id = sec.class_id
        LEFT JOIN Students s ON sec.id = s.section_id
        GROUP BY b.name
    """
    results = fetch_data(query)
    if results:
        df = pd.DataFrame(results, columns=['Branch Name', 'Number of Students'])
        fig = px.bar(df, x='Branch Name', y='Number of Students', title='Student Distribution by Branch')
        st.plotly_chart(fig)
    else:
        st.write("No student distribution data available.")

# 3. Performance Analysis Based on Selected Subject (Placeholder - Needs further refinement based on your performance data)
def performance_analysis_by_subject(subject_id):

    query = """
        SELECT
        s.name AS student_name,
        t.name AS topic_name,
        e.completed
    FROM
        Evaluations e
    JOIN
        Students s ON e.student_id = s.id
    JOIN
        Topics t ON e.topic_id = t.id
    JOIN
        Chapters c ON t.chapter_id = c.id
    JOIN
        Subjects sub ON c.subject_id = sub.id
    WHERE
        sub.id = ?

    """
    results = fetch_data(query,(subject_id,))
    if results:
        df = pd.DataFrame(results, columns=['Student Name', 'Topic Name', 'Completed'])
        st.write(df)
        # Placeholder: Implement specific analysis and visualizations based on the data, this is a good start.
    else:
        st.write("No performance data available for this subject")

# 4. Cards with Branch-Specific Counts
def display_branch_cards(branch_id):
    query = """
        SELECT
            (SELECT COUNT(DISTINCT c.id) FROM Classes c WHERE c.branch_id = ?) AS total_classes,
            (SELECT COUNT(DISTINCT sec.id) FROM Classes c JOIN Sections sec ON c.id = sec.class_id WHERE c.branch_id = ?) AS total_sections,
            (SELECT COUNT(DISTINCT u.id)
              FROM Users u
              WHERE u.branch_id = ?)
               AS total_teachers,
            (SELECT COUNT(DISTINCT s.id)
             FROM Classes c
             JOIN Sections sec ON c.id = sec.class_id
             JOIN Students s ON sec.id = s.section_id
             WHERE c.branch_id = ?)
              AS total_students,
              (SELECT COUNT(DISTINCT sub.id) FROM Classes c JOIN Subjects sub ON c.id = sub.class_id WHERE c.branch_id = ? ) AS total_subjects,
            (SELECT COUNT(DISTINCT t.id)
            FROM Classes c
            JOIN Sections sec ON c.id = sec.class_id
            JOIN Chapters ch ON c.id IN (
            SELECT s.class_id FROM Subjects s WHERE s.id = ch.subject_id
            )
            JOIN Topics t ON ch.id = t.chapter_id
             WHERE c.branch_id = ? ) as total_topics
    """
    params = (branch_id, branch_id, branch_id, branch_id, branch_id, branch_id)
    results = fetch_data(query, params)

    if results:
        total_classes, total_sections, total_teachers, total_students, total_subjects, total_topics = results[0]

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total Classes", total_classes)
        with col2:
            st.metric("Total Sections", total_sections)
        with col3:
            st.metric("Total Teachers", total_teachers)
        with col4:
            st.metric("Total Students", total_students)
        with col5:
            st.metric("Total Subjects",total_subjects)
        with col6:
            st.metric("Total Topics",total_topics)
    else:
        st.write("No data available for the selected branch.")


# 5. Subject Wise Teacher Distribution
def subject_wise_teacher_distribution():
    query = """
       SELECT sub.name AS subject_name,
           u.username AS teacher_name
        FROM Subjects sub
        JOIN Users u ON sub.teacher_id = u.id
    """
    results = fetch_data(query)
    if results:
        df = pd.DataFrame(results, columns=['Subject Name', 'Teacher Name'])
        st.table(df)
    else:
        st.write("No data available on teacher distribution")


# 6. Class Wise Statistics (Bar Graph)
def class_wise_statistics():
  query = """
    SELECT
        c.name AS class_name,
        sec.name AS section_name,
        COUNT(s.id) AS num_students
    FROM Classes c
    JOIN Sections sec ON c.id = sec.class_id
    LEFT JOIN Students s ON sec.id = s.section_id
    GROUP BY c.name, sec.name
    ORDER BY c.name, sec.name;
    """
  results = fetch_data(query)
  if results:
    df = pd.DataFrame(results, columns=['Class Name', 'Section Name', 'Number of Students'])
    fig = px.bar(df, x='Class Name', y='Number of Students', color='Section Name',
                 title='Student Distribution by Section within Each Class')
    st.plotly_chart(fig)
  else:
      st.write("No Class Wise Statistics available")

# 7. Subject Wise Structure Analysis
def subject_wise_structure_analysis(subject_id):
    # 7.i Card with total chapters,total topics
    query1 = """
        SELECT
        (SELECT COUNT(DISTINCT ch.id) FROM Chapters ch WHERE ch.subject_id = ?) AS total_chapters,
        (SELECT COUNT(DISTINCT t.id)
        FROM Chapters ch JOIN Topics t ON ch.id = t.chapter_id
        WHERE ch.subject_id = ?) AS total_topics
    """
    results = fetch_data(query1, (subject_id, subject_id))

    if results:
      total_chapters, total_topics = results[0]
      col1, col2 = st.columns(2)
      with col1:
        st.metric("Total Chapters", total_chapters)
      with col2:
        st.metric("Total Topics", total_topics)
    else:
      st.write("No data available for this subject")
    # 7.ii Topics per Chapter

    query2 = """
      SELECT ch.name AS chapter_name,
      COUNT(t.id) AS num_topics
      FROM Chapters ch
      LEFT JOIN Topics t ON ch.id = t.chapter_id
      WHERE ch.subject_id = ?
      GROUP BY ch.name;
    """
    results2 = fetch_data(query2,(subject_id,))
    if results2:
        df = pd.DataFrame(results2, columns=['Chapter Name','Number of Topics'])
        st.write("Topics per Chapter")
        st.table(df)
    else:
      st.write("No Topics available for this subject")

    # 7.iii Performance Analysis
    query3 = """
        SELECT
            s.name AS student_name,
            t.name AS topic_name,
            e.completed
        FROM
            Evaluations e
        JOIN
            Students s ON e.student_id = s.id
        JOIN
            Topics t ON e.topic_id = t.id
        JOIN
            Chapters c ON t.chapter_id = c.id
        JOIN
            Subjects sub ON c.subject_id = sub.id
        WHERE
            sub.id = ?

    """
    results3 = fetch_data(query3,(subject_id,))
    if results3:
       df = pd.DataFrame(results3, columns=['Student Name', 'Topic Name', 'Completed'])
       st.write(df)
    else:
      st.write("No data available for Performance Analysis")
    
    query4 = """
    SELECT
       CASE
        WHEN e.completed = 'YES' THEN 'Completed'
        WHEN e.completed = 'NO' THEN 'Not Completed'
       END AS CompletionStatus,
       COUNT(*) AS Count
    FROM
        Evaluations e
    JOIN
        Topics t ON e.topic_id = t.id
    JOIN
        Chapters c ON t.chapter_id = c.id
    JOIN
      Subjects sub ON c.subject_id = sub.id
        WHERE
            sub.id = ?
     GROUP BY CompletionStatus
    """
    results4 = fetch_data(query4, (subject_id,))
    if results4:
        df = pd.DataFrame(results4, columns=['Completion Status', 'Count'])
        st.write("Total count of Performance Analysis")
        st.table(df)
        #Evaluation table pie graph and bar graph per subject,Chapter wise evaluations grade analysis per subject and topics wise evaluations grade analysis
        fig = px.pie(df, names = "Completion Status", values = "Count", title = "Performance Analysis")
        st.plotly_chart(fig)
        fig = px.bar(df, x='Completion Status', y='Count', title = 'Performance Analysis')
        st.plotly_chart(fig)
    else:
        st.write("No evaluation data available")


# 8. Evaluation Visualizations per Student
def evaluation_visualizations_per_student(student_id, subject_id, class_id, section_id):
    # Prepare Query
    query = """
        SELECT
            s.name AS student_name,
            sub.name AS subject_name,
            c.name AS class_name,
            sec.name AS section_name,
            t.name AS topic_name,
            e.completed AS evaluation_status
        FROM Evaluations e
        JOIN Students s ON e.student_id = s.id
        JOIN Topics t ON e.topic_id = t.id
        JOIN Chapters ch ON t.chapter_id = ch.id
        JOIN Subjects sub ON ch.subject_id = sub.id
        JOIN Sections sec ON s.section_id = sec.id
        JOIN Classes c ON sec.class_id = c.id
        WHERE s.id = ?
          AND sub.id = ?
          AND c.id = ?
          AND sec.id = ?
    """
    params = (student_id, subject_id, class_id, section_id)
    results = fetch_data(query, params)

    if results:
        df = pd.DataFrame(results, columns=['Student Name', 'Subject Name', 'Class Name', 'Section Name', 'Topic Name', 'Evaluation Status'])
        st.write(df)
        #Example visualizations
        st.write("Evaluation Visualizations per Student")
        fig = px.histogram(df, x="Topic Name",color="Evaluation Status",title="Evaluation Status per Topic")
        st.plotly_chart(fig)
    else:
        st.write("No Evaluation data available")


def get_overview_data(cursor, teacher_username):
    """Retrieves overview data for the teacher's subject."""
    query = """
    SELECT
        COUNT(DISTINCT s.id) AS total_students,
        COUNT(DISTINCT t.id) AS total_topics,
        sub.name AS subject_name
    FROM
        Subjects sub
    JOIN
        Classes c ON sub.class_id = c.id
    JOIN
       Sections sec ON c.id = sec.class_id
    JOIN
        Students s ON sec.id=s.section_id
    JOIN
        Chapters ch ON sub.id = ch.subject_id
    JOIN
        Topics t ON ch.id = t.chapter_id
    JOIN Users u ON sub.teacher_id = u.id
    WHERE u.username = ? and u.userType = 'teacher'
    """
    cursor.execute(query, (teacher_username,))
    results = cursor.fetchone()
    return results if results else (0, 0, "No Subject Assigned")


def display_overview(cursor, teacher_username):
     """Displays the overview cards."""
     total_students, total_topics, subject_name = get_overview_data(cursor, teacher_username)

     st.subheader("Subject Overview")
     col1, col2, col3 = st.columns(3)
     with col1:
         st.metric("Subject Name", subject_name)
     with col2:
         st.metric("Total Students", total_students)
     with col3:
         st.metric("Total Topics", total_topics)

import plotly.express as px

def get_completion_pie_data(cursor, teacher_username):
     """Retrieves data for the completion pie chart."""
     query = """
         SELECT
         e.completed,
         COUNT(e.id) AS count
     FROM
         Evaluations e
     JOIN
         Topics t ON e.topic_id = t.id
     JOIN
         Chapters ch ON t.chapter_id = ch.id
     JOIN
         Subjects sub ON ch.subject_id = sub.id
     JOIN Users u ON sub.teacher_id = u.id
     WHERE u.username = ? AND u.userType = 'teacher'
     GROUP BY
         e.completed;
     """
     cursor.execute(query, (teacher_username,))
     results = cursor.fetchall()
     if results:
        df = pd.DataFrame(results, columns=["completed", "count"])
        return df
     else:
        return pd.DataFrame({'completed': [], 'count': []})


def display_completion_pie_chart(cursor,teacher_username):
     """Displays the completion pie chart."""
     df = get_completion_pie_data(cursor, teacher_username)
     if not df.empty:
         fig = px.pie(df, values='count', names='completed', title='Completion Status')
         st.plotly_chart(fig)
     else:
         st.write("No Evaluation data found for the subject")

import plotly.express as px

def get_chapter_histogram_data(cursor, teacher_username):
    """Retrieves data for the chapter histogram."""
    query = """
    SELECT
        ch.name as chapter_name,
        e.completed,
        COUNT(e.id) AS count
    FROM
        Evaluations e
    JOIN
        Topics t ON e.topic_id = t.id
    JOIN
        Chapters ch ON t.chapter_id = ch.id
    JOIN
        Subjects sub ON ch.subject_id = sub.id
    JOIN Users u ON sub.teacher_id = u.id
    WHERE u.username = ? AND u.userType = 'teacher'
    GROUP BY
        ch.name, e.completed
    """
    cursor.execute(query, (teacher_username,))
    results = cursor.fetchall()
    if results:
       df = pd.DataFrame(results, columns=["chapter_name", "completed", "count"])
       return df
    else:
        return pd.DataFrame({'chapter_name': [], 'completed': [], 'count': []})

def display_chapter_histogram(cursor, teacher_username):
    """Displays the chapter histogram."""
    df = get_chapter_histogram_data(cursor, teacher_username)
    if not df.empty:
        fig = px.histogram(df, x="chapter_name", y="count", color="completed",
                           title='Chapter Wise Completion Count',
                           barmode = 'group')
        st.plotly_chart(fig)
    else:
       st.write("No evaluation data to display for Chapter histogram")

import plotly.express as px

def get_student_histogram_data(cursor, teacher_username):
    """Retrieves data for the student-wise histogram."""
    query = """
    SELECT
        s.name as student_name,
        e.completed,
        COUNT(e.id) AS count
    FROM
        Evaluations e
    JOIN
        Students s ON e.student_id = s.id
    JOIN
        Topics t ON e.topic_id = t.id
    JOIN
        Chapters ch ON t.chapter_id = ch.id
    JOIN
        Subjects sub ON ch.subject_id = sub.id
    JOIN Users u ON sub.teacher_id = u.id
        WHERE u.username = ? AND u.userType = 'teacher'
    GROUP BY
        s.name, e.completed
    """
    cursor.execute(query, (teacher_username,))
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=['student_name', 'completed', 'count'])
        return df
    else:
        return pd.DataFrame({'student_name': [], 'completed': [], 'count': []})

def display_student_histogram(cursor, teacher_username):
    """Displays the student-wise histogram."""
    df = get_student_histogram_data(cursor, teacher_username)
    if not df.empty:
        fig = px.histogram(df, x="student_name", y="count", color="completed",
                           title='Student Wise Completion Count',
                           barmode = 'group')
        st.plotly_chart(fig)
    else:
        st.write("No data to display for student Histogram")

import plotly.graph_objects as go


def get_student_performance_data(cursor, teacher_username, student_id):
     """Retrieves data for student performance tracking."""
     query = """
     SELECT
         ch.name as chapter_name,
         COUNT(CASE WHEN e.completed = 'YES' THEN 1 END) AS completed_count,
          COUNT(e.id) AS total_count
     FROM
         Evaluations e
     JOIN
         Topics t ON e.topic_id = t.id
     JOIN
         Chapters ch ON t.chapter_id = ch.id
      JOIN
          Subjects sub ON ch.subject_id = sub.id
     JOIN Users u ON sub.teacher_id = u.id
     WHERE u.username = ? AND u.userType = 'teacher' AND e.student_id = ?
     GROUP BY ch.name
     """
     cursor.execute(query, (teacher_username, student_id))
     results = cursor.fetchall()
     if results:
         df = pd.DataFrame(results, columns=["chapter_name", "completed_count", "total_count"])
         return df
     else:
         return pd.DataFrame({'chapter_name': [], 'completed_count': [], 'total_count': []})

def display_student_performance_graph(cursor, teacher_username):
     """Displays the student performance tracking graph."""

     # Get list of students for the selectbox
     query = """
     SELECT DISTINCT(s.id), s.name
     FROM Students s
     JOIN Sections sec ON s.section_id = sec.id
     JOIN Classes c ON sec.class_id = c.id
     JOIN Subjects sub ON c.id = sub.class_id
     JOIN Users u ON sub.teacher_id = u.id
     WHERE u.username = ? AND u.userType = 'teacher'
     """
     cursor.execute(query, (teacher_username,))
     student_options = cursor.fetchall()

     if not student_options:
         st.warning("No Students Assigned for the Teacher")
         return
     student_names = [item[1] for item in student_options]
     student_ids = [item[0] for item in student_options]
     student_id_name_dict = dict(zip(student_names, student_ids))
     selected_student = st.selectbox("Select Student", student_names)
     student_id = student_id_name_dict[selected_student]

     if selected_student:
         df = get_student_performance_data(cursor, teacher_username, student_id)
         if not df.empty:
             fig = go.Figure()
             fig.add_trace(go.Scatter(x=df['chapter_name'],
                         y=df['completed_count']/df['total_count'],
                         mode='lines+markers',
                         name='Completion Rate'))
             fig.update_layout(
                     title='Student Performance by Chapter',
                     xaxis_title='Chapter',
                     yaxis_title='Completed Rate (completed_count / total_count)',
                     yaxis_range=[0,1]
                 )
             st.plotly_chart(fig)
         else:
           st.write("No Performance data for this student")

def get_chapter_wise_counts_data(cursor, teacher_username):
    """Retrieves chapter-wise completion counts for the table."""
    query = """
    SELECT
        ch.name as chapter_name,
        e.completed,
        COUNT(e.id) AS count
    FROM
        Evaluations e
    JOIN
        Topics t ON e.topic_id = t.id
    JOIN
        Chapters ch ON t.chapter_id = ch.id
    JOIN
        Subjects sub ON ch.subject_id = sub.id
    JOIN Users u ON sub.teacher_id = u.id
    WHERE u.username = ? AND u.userType = 'teacher'
    GROUP BY
        ch.name, e.completed
    """
    cursor.execute(query, (teacher_username,))
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=["chapter_name", "completed", "count"])
        return df
    else:
        return pd.DataFrame({'chapter_name': [], 'completed': [], 'count': []})

def display_chapter_wise_table(cursor, teacher_username):
    """Displays chapter-wise counts in a Pandas DataFrame table."""
    df = get_chapter_wise_counts_data(cursor, teacher_username)
    if not df.empty:
        df_pivot = df.pivot_table(index='chapter_name', columns='completed', values='count', fill_value=0)
        st.dataframe(df_pivot)
    else:
      st.write("No evaluation data for chapter wise table")