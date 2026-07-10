
Handles SQLite database creation and seeding for the
AI Chatbot for Student Support Services project.
 
Tables:
    Students     -> Student_ID, Name, Email, Course
    FAQ          -> FAQ_ID, Category, Question, Answer
    ChatHistory  -> Chat_ID, Student_ID, Query, Response, Date_Time
    Admin        -> Admin_ID, Username, Password
"""
 
import sqlite3
import os
 
DB_NAME = os.path.join(os.path.dirname(__file__), "chatbot.db")
 
 
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()
 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            Student_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            Course TEXT
        )
    """)
 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS FAQ (
            FAQ_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Category TEXT NOT NULL,
            Question TEXT NOT NULL,
            Answer TEXT NOT NULL
        )
    """)
 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ChatHistory (
            Chat_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID INTEGER,
            Query TEXT NOT NULL,
            Response TEXT NOT NULL,
            Date_Time TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
        )
    """)
 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL
        )
    """)
 
    conn.commit()
 
    # Seed default admin (username: admin / password: admin123)
    cur.execute("SELECT COUNT(*) AS c FROM Admin")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO Admin (Username, Password) VALUES (?, ?)",
            ("admin", "admin123"),
        )
        conn.commit()
 
    # Seed FAQ knowledge base (from project report - Sample Questions + Scope)
    cur.execute("SELECT COUNT(*) AS c FROM FAQ")
    if cur.fetchone()["c"] == 0:
        sample_faqs = [
            ("Admissions", "What is the admission process?",
             "Admission details are available on the admission portal. Required documents "
             "include Class 10 and 12 mark sheets, graduation certificate (if applicable), "
             "identity proof, passport-size photographs, and other institution-specific documents."),
 
            ("Library", "What are library timings?",
             "The library is open from 9:00 AM to 5:00 PM on working days."),
 
            ("Fees", "How do I pay fees?",
             "Fees can be paid online through the student portal or at the accounts office, "
             "depending on institutional policy."),
 
            ("Leave Application", "How can I apply for leave?",
             "Submit a leave application through the student portal or the department office."),
 
            ("Academic Calendar", "What is today's timetable?",
             "Please check the timetable section on the student portal for your course and section."),
 
            ("Examination", "When are examinations conducted?",
             "Examinations are conducted as per the academic calendar published on the college website. "
             "Please check the examination schedule section for exact dates."),
 
            ("Results", "How can I check my results?",
             "Results are published on the student portal under the Results section after each examination."),
 
            ("Hostel", "What are the hostel facilities available?",
             "Hostel facilities include furnished rooms, mess/canteen, Wi-Fi, and 24x7 security. "
             "Contact the hostel warden for allotment details."),
 
            ("Placement", "How does the placement cell help students?",
             "The placement cell organizes campus recruitment drives, resume-building workshops, "
             "and mock interviews to help students secure job opportunities."),
 
            ("Scholarships", "What scholarships are available?",
             "Merit-based and need-based scholarships are available. Details and application forms "
             "are available at the accounts/scholarship office."),
 
            ("Faculty", "How can I contact faculty?",
             "Faculty contact details, including email and office hours, are listed on the "
             "department page of the college website."),
 
            ("Grievances", "How do I raise a student grievance?",
             "Student grievances can be submitted through the Student Grievance Cell portal "
             "or by writing to the grievance officer."),
 
            ("Campus Facilities", "What campus facilities are available?",
             "Campus facilities include library, labs, sports grounds, cafeteria, Wi-Fi, "
             "and medical assistance."),
 
            ("Greeting", "hello",
             "Hi! I'm your Student Support Assistant. Ask me about admissions, fees, exams, "
             "library, hostel, placements, and more."),
 
            ("Greeting", "hi",
             "Hello! How can I help you today?"),
 
            ("Thanks", "thank you",
             "You're welcome! Let me know if you have any other questions."),
        ]
        cur.executemany(
            "INSERT INTO FAQ (Category, Question, Answer) VALUES (?, ?, ?)",
            sample_faqs,
        )
        conn.commit()
 
    conn.close()
    print(f"Database initialized at: {DB_NAME}")
 
 
if __name__ == "__main__":
    init_db()
 
