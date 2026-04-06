
# seed_memory.py

from vanna_setup import agent
from vanna.core.user import User


def seed_memory():

    user = User(id="seed_user")

    examples = [
        ("How many patients do we have?",
         "SELECT COUNT(*) AS total_patients FROM patients"),

        ("List all patients from Pune",
         "SELECT * FROM patients WHERE city = 'Pune'"),

        ("How many male and female patients are there?",
         "SELECT gender, COUNT(*) FROM patients GROUP BY gender"),

        ("List all doctors and their specializations",
         "SELECT name, specialization FROM doctors"),

        ("Which doctor has the most appointments?",
         """
         SELECT d.name, COUNT(a.id) AS total_appointments
         FROM doctors d
         JOIN appointments a ON d.id = a.doctor_id
         GROUP BY d.name
         ORDER BY total_appointments DESC
         LIMIT 1
         """),

        ("Show appointments for last month",
         "SELECT * FROM appointments WHERE appointment_date >= DATE('now', '-1 month')"),

        ("How many cancelled appointments are there?",
         "SELECT COUNT(*) FROM appointments WHERE status = 'Cancelled'"),

        ("Show monthly appointment count for the past 6 months",
         """
         SELECT strftime('%Y-%m', appointment_date) AS month,
                COUNT(*) AS total_appointments
         FROM appointments
         WHERE appointment_date >= DATE('now', '-6 months')
         GROUP BY month
         ORDER BY month
         """),

        ("What is the total revenue?",
         "SELECT SUM(total_amount) FROM invoices"),

        ("Show unpaid invoices",
         "SELECT * FROM invoices WHERE status = 'Pending'"),

        ("Top 5 patients by spending",
         """
         SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spent
         FROM patients p
         JOIN invoices i ON p.id = i.patient_id
         GROUP BY p.id
         ORDER BY total_spent DESC
         LIMIT 5
         """),

        ("Show revenue trend by month",
         """
         SELECT strftime('%Y-%m', invoice_date) AS month,
                SUM(total_amount)
         FROM invoices
         GROUP BY month
         ORDER BY month
         """),

        ("Which city has the most patients?",
         """
         SELECT city, COUNT(*) AS patient_count
         FROM patients
         GROUP BY city
         ORDER BY patient_count DESC
         LIMIT 1
         """),

        ("List patients who visited more than 3 times",
         """
         SELECT p.first_name, p.last_name, COUNT(a.id) AS visit_count
         FROM patients p
         JOIN appointments a ON p.id = a.patient_id
         GROUP BY p.id
         HAVING visit_count > 3
         """),

        ("Show revenue by doctor",
         """
         SELECT d.name, SUM(i.total_amount) AS total_revenue
         FROM invoices i
         JOIN appointments a ON i.patient_id = a.patient_id
         JOIN doctors d ON d.id = a.doctor_id
         GROUP BY d.name
         ORDER BY total_revenue DESC
         """)
        
    ]

    # Correct seeding
    for question, sql in examples:

        message = f"""
You are learning SQL mappings.

Question:
{question}

Correct SQL:
{sql}

This is a verified correct SQL. Save it for future use.
"""

        agent.send_message(user, message)

    print(f"Seeded {len(examples)} examples successfully!")


if __name__ == "__main__":
    seed_memory()