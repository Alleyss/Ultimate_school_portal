import sqlite3
import json
from datetime import date

# Database connection function
def get_connection():
    connection = sqlite3.connect("school.db", check_same_thread=False)
    return connection

# Create tables
def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            userType TEXT CHECK(userType IN ('superadmin', 'branchadmin', 'teacher')) NOT NULL,
            branch_id INTEGER,
            additional_details TEXT,
            FOREIGN KEY (branch_id) REFERENCES Branches(id)
        )
    ''')

    # Branches Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            branchadmin_id INTEGER,  -- ADDED THIS COLUMN
           FOREIGN KEY (branchadmin_id) REFERENCES Users(id)
        )
    ''')

    # Classes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch_id INTEGER,
            FOREIGN KEY (branch_id) REFERENCES Branches(id)
        )
    ''')

    # Sections Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            FOREIGN KEY (class_id) REFERENCES Classes(id)
        )
    ''')

    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no INTEGER,
            gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL,
            guardian_contact TEXT,
            enrollment_date DATE DEFAULT (date('now')),
            address TEXT,
            section_id INTEGER NOT NULL,
            FOREIGN KEY (section_id) REFERENCES Sections(id)
        )
    ''')

    # Subjects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES Users(id)
            FOREIGN KEY (class_id) REFERENCES Classes(id)
        )
    ''')

    # Chapters Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_number INTEGER,
            name TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES Subjects(id)
        )
    ''')

    # Topics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            outcome TEXT NOT NULL,
            chapter_id INTEGER NOT NULL,
            FOREIGN KEY (chapter_id) REFERENCES Chapters(id)
        )
    ''')

    # Evaluations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            completed TEXT CHECK(completed IN ('YES','NO')) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Students(id),
            FOREIGN KEY (topic_id) REFERENCES Topics(id)
        )
    ''')

    connection.commit()
    connection.close()


# Register user (Plain Text Password)
def register_user(username, email, password, userType, branch_id=None, additional_details=None):
    connection = get_connection()
    cursor = connection.cursor()
    try:
         cursor.execute('''
            INSERT INTO Users (username, email, password, userType, branch_id, additional_details)
            VALUES (?, ?, ?, ?, ?, ?)
         ''', (username, email, password, userType, branch_id if branch_id else None, json.dumps(additional_details) if additional_details else None))
         connection.commit()
         return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()


# Verify login
def verify_login(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        SELECT password FROM Users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()

    connection.close()

    if user and user[0] == password:
        return True
    return False

#Get user details
def get_user_details(username):
    connection = get_connection()
    cursor = connection.cursor()

    # Fetch all details for the given username
    cursor.execute('''
        SELECT id, username, email, password, userType, branch_id, additional_details
        FROM Users
        WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()

    connection.close()

    # If user exists, map the result to a dictionary
    if user:
        user_details = {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password": user[3],
            "userType": user[4],
            "branch_id": user[5],
            "additional_details": user[6],
        }
        return user_details

    return None
def update_evaluations(student_id=None, topic_id=None):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                if student_id and topic_id:
                    # Single student/topic case
                    cursor.execute("""
                        INSERT INTO Evaluations (student_id, topic_id, completed)
                        SELECT ?, ?, 'NO'
                        WHERE NOT EXISTS (
                            SELECT 1 FROM Evaluations WHERE student_id = ? AND topic_id = ?
                        )
                    """, (student_id, topic_id, student_id, topic_id))
                else:
                    # Bulk insertion for all students and topics
                    cursor.execute("""
                        INSERT INTO Evaluations (student_id, topic_id, completed)
                        SELECT s.id, t.id, 'NO'
                        FROM Students s, Topics t
                        LEFT JOIN Evaluations e
                        ON s.id = e.student_id AND t.id = e.topic_id
                        WHERE e.id IS NULL
                    """)
                connection.commit()
    except Exception as e:
        print(f"Error creating initial evaluations: {e}")