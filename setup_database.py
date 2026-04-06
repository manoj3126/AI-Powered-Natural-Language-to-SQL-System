import sqlite3
from faker import Faker
import random

fake = Faker()

# Create Tables

def create_tables(cursor):
    # Patients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        date_of_birth DATE,
        gender TEXT,
        city TEXT,
        registered_date DATE
    )
    """)

    # Doctors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        department TEXT,
        phone TEXT
    )
    """)

    # Appointments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATETIME,
        status TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id)
    )
    """)

    # Treatments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        treatment_name TEXT,
        cost REAL,
        duration_minutes INTEGER,
        FOREIGN KEY(appointment_id) REFERENCES appointments(id)
    )
    """)

    # Invoices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        invoice_date DATE,
        total_amount REAL,
        paid_amount REAL,
        status TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

# Inserting dummy data

def insert_patients(cursor):
    cities = ["Sangli","Kolhapur","Pune","Mumbai", "Bangalore", "Delhi", "Chennai", "Hyderabad", "Ahmedabad", "Kolkata"]

    for _ in range(200):
        cursor.execute("""
        INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fake.first_name(),
            fake.last_name(),
            fake.email() if random.random() > 0.2 else None,
            fake.phone_number() if random.random() > 0.2 else None,
            fake.date_of_birth(minimum_age=18, maximum_age=80),
            random.choice(["M", "F"]),
            random.choice(cities),
            fake.date_between(start_date="-1y", end_date="today")
        ))


def insert_doctors(cursor):
    specializations = ["Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"]
    departments = ["OPD", "Emergency", "Surgery"]

    for _ in range(15):
        cursor.execute("""
        INSERT INTO doctors (name, specialization, department, phone)
        VALUES (?, ?, ?, ?)
        """, (
            fake.name(),
            random.choice(specializations),
            random.choice(departments),
            fake.phone_number()
        ))



def insert_appointments(cursor):
    statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]

    doctor_ids = list(range(1, 16))

    # Doctor popularity weights
    doctor_weights = [10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]


    for _ in range(500):
        
        # Patient skew (repeat patients)
        patient_id = random.randint(1, 30) if random.random() < 0.2 else random.randint(31, 200)

        # Doctor skew (important improvement)
        doctor_id = random.choices(doctor_ids, weights=doctor_weights)[0]

        cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (
            patient_id,
            doctor_id,
            fake.date_time_between(start_date="-1y", end_date="now"),
            random.choices(statuses, weights=[0.2, 0.5, 0.2, 0.1])[0],
            fake.text(max_nb_chars=50) if random.random() > 0.7 else None
        ))


def insert_treatments(cursor):
    treatment_names = ["X-Ray", "Blood Test", "Consultation", "MRI", "Surgery"]

    # Only completed appointments
    cursor.execute("SELECT id FROM appointments WHERE status='Completed'")
    completed_ids = [row[0] for row in cursor.fetchall()]

    selected_ids = random.sample(completed_ids, min(350, len(completed_ids)))

    for appt_id in selected_ids:
        cursor.execute("""
        INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
        VALUES (?, ?, ?, ?)
        """, (
            appt_id,
            random.choice(treatment_names),
            round(random.uniform(50, 5000), 2),
            random.randint(10, 120)
        ))


def insert_invoices(cursor):
    for _ in range(300):
        total = round(random.uniform(100, 5000), 2)
        paid = total if random.random() > 0.3 else round(random.uniform(0, total), 2)

        status = "Paid" if paid == total else random.choice(["Pending", "Overdue"])

        cursor.execute("""
        INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            random.randint(1, 200),
            fake.date_between(start_date="-1y", end_date="today"),
            total,
            paid,
            status
        ))

# creating  SQLite database
def main():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()


     # Enable FK
    cursor.execute("PRAGMA foreign_keys = ON;")

    # RESET DATABASE
    cursor.executescript("""
    DROP TABLE IF EXISTS treatments;
    DROP TABLE IF EXISTS appointments;
    DROP TABLE IF EXISTS invoices;
    DROP TABLE IF EXISTS doctors;
    DROP TABLE IF EXISTS patients;
    """)


    # Refresh data
    print("Creating tables...")
    create_tables(cursor)

    print("Inserting doctors...")
    insert_doctors(cursor)

    print("Inserting patients...")
    insert_patients(cursor)

    print("Inserting appointments...")
    insert_appointments(cursor)

    print("Inserting treatments...")
    insert_treatments(cursor)

    print("Inserting invoices...")
    insert_invoices(cursor)

    conn.commit()
    conn.close()

    print("\nDatabase created successfully!")
    print("Summary:")
    print("Doctors: 15")
    print("Patients: 200")
    print("Appointments: 500")
    print("Treatments: 350")
    print("Invoices: 300")


if __name__ == "__main__":
    main()


# import sqlite3

# conn = sqlite3.connect("clinic.db")
# cursor = conn.cursor()

# cursor.execute("select * from doctors")
# rows = cursor.fetchall()

# for row in rows:
#     print(row)

# conn.close()