import streamlit as st
import mysql.connector
import pandas as pd
import os

st.set_page_config(page_title="Hospital Management System", page_icon="🏥")

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="HospitalDB"
    )

def login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

def dashboard():
    st.subheader("📊 Dashboard")
    conn = get_connection()
    total_patients = pd.read_sql("SELECT COUNT(*) as count FROM Patient", conn)["count"][0]
    total_doctors = pd.read_sql("SELECT COUNT(*) as count FROM Doctor", conn)["count"][0]
    total_appointments = pd.read_sql("SELECT COUNT(*) as count FROM Appointment", conn)["count"][0]
    conn.close()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patients", total_patients)
    col2.metric("Total Doctors", total_doctors)
    col3.metric("Total Appointments", total_appointments)

def add_department():
    st.subheader("➕ Add Department")
    name = st.text_input("Department Name")

    if st.button("Add Department"):
        if not name:
            st.error("Department name required")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Department (dept_name) VALUES (%s)", (name,))
        conn.commit()
        conn.close()
        st.success("Department added successfully")

def view_departments():
    st.subheader("🏢 Departments")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Department", conn)
    conn.close()
    st.dataframe(df)

def add_doctor():
    st.subheader("➕ Add Doctor")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT dept_id, dept_name FROM Department")
    departments = cursor.fetchall()
    conn.close()

    if not departments:
        st.warning("Add department first")
        return

    dept_dict = {d[1]: d[0] for d in departments}

    name = st.text_input("Doctor Name")
    specialization = st.text_input("Specialization")
    dept_name = st.selectbox("Department", list(dept_dict.keys()))

    if st.button("Add Doctor"):
        if not name or not specialization:
            st.error("Fill all fields")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Doctor (doctor_name, dept_id, specialization) VALUES (%s,%s,%s)",
            (name, dept_dict[dept_name], specialization)
        )
        conn.commit()
        conn.close()
        st.success("Doctor added successfully")

def view_doctors():
    st.subheader("👨‍⚕️ Doctors")
    conn = get_connection()
    df = pd.read_sql("""
        SELECT d.doctor_id, d.doctor_name, dep.dept_name, d.specialization
        FROM Doctor d
        JOIN Department dep ON d.dept_id = dep.dept_id
    """, conn)
    conn.close()
    st.dataframe(df)

def add_patient():
    st.subheader("➕ Add Patient")
    name = st.text_input("Name")
    age = st.number_input("Age", 0, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact = st.text_input("Contact")

    if st.button("Add Patient"):
        if not name or not contact:
            st.error("Fill all required fields")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Patient (patient_name, age, gender, contact_no) VALUES (%s,%s,%s,%s)",
            (name, age, gender, contact)
        )
        conn.commit()
        conn.close()
        st.success("Patient added successfully")

def view_patients():
    st.subheader("🧍 Patients")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Patient", conn)
    conn.close()
    st.dataframe(df)

def book_appointment():
    st.subheader("📅 Book Appointment")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, patient_name FROM Patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT doctor_id, doctor_name FROM Doctor")
    doctors = cursor.fetchall()
    conn.close()

    if not patients or not doctors:
        st.warning("Add patient and doctor first")
        return

    patient_dict = {p[1]: p[0] for p in patients}
    doctor_dict = {d[1]: d[0] for d in doctors}

    p_name = st.selectbox("Patient", list(patient_dict.keys()))
    d_name = st.selectbox("Doctor", list(doctor_dict.keys()))
    date = st.date_input("Date")
    time = st.time_input("Time")

    if st.button("Book Appointment"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Appointment
            WHERE doctor_id=%s AND appointment_date=%s AND appointment_time=%s
        """, (doctor_dict[d_name], date, time))

        if cursor.fetchone():
            st.error("Doctor already booked at this time!")
        else:
            cursor.execute("""
                INSERT INTO Appointment (patient_id, doctor_id, appointment_date, appointment_time)
                VALUES (%s,%s,%s,%s)
            """, (patient_dict[p_name], doctor_dict[d_name], date, time))
            conn.commit()
            st.success("Appointment booked successfully")
        conn.close()

def view_appointments():
    st.subheader("📋 Appointments")
    conn = get_connection()
    df = pd.read_sql("""
        SELECT a.appointment_id, p.patient_name, d.doctor_name,
               a.appointment_date, a.appointment_time
        FROM Appointment a
        JOIN Patient p ON a.patient_id = p.patient_id
        JOIN Doctor d ON a.doctor_id = d.doctor_id
    """, conn)
    conn.close()
    st.dataframe(df)

def logout():
    st.session_state["logged_in"] = False
    st.rerun()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    st.sidebar.title("🏥 Menu")
    menu = [
        "Dashboard",
        "Add Department", "View Departments",
        "Add Doctor", "View Doctors",
        "Add Patient", "View Patients",
        "Book Appointment", "View Appointments",
        "Logout"
    ]

    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Dashboard":
        dashboard()
    elif choice == "Add Department":
        add_department()
    elif choice == "View Departments":
        view_departments()
    elif choice == "Add Doctor":
        add_doctor()
    elif choice == "View Doctors":
        view_doctors()
    elif choice == "Add Patient":
        add_patient()
    elif choice == "View Patients":
        view_patients()
    elif choice == "Book Appointment":
        book_appointment()
    elif choice == "View Appointments":
        view_appointments()
    elif choice == "Logout":
        logout()
